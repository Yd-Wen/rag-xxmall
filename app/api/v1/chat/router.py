import json
from datetime import datetime
from fastapi import APIRouter, Depends
from app.api.v1.chat.schema import ChatRequest
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.rag import RAG

# 定义模块路由
router = APIRouter(
    prefix="/chat",    # 接口前缀：/v1/chat
    tags=["聊天接口"],  # 文档分类标签
    # dependencies=[Depends(verify_user_token)]  # 该模块所有接口复用鉴权依赖
)

# 通用工具函数：初始化RAG和会话配置
def _init_rag_session(request: ChatRequest):
    """初始化RAG实例和会话配置"""
    timestamp = datetime.now().isoformat()
    session_config = {
        "configurable": {
            "session_id": request.session_id,
            "timestamp": timestamp
        }
    }
    rag = RAG()
    return rag, session_config, timestamp

# 流式响应接口
@router.post("/stream", response_class=StreamingResponse)
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口
    返回SSE格式的流式响应，专门处理流式输出场景
    """
    rag, session_config, timestamp = _init_rag_session(request)

    async def generate_response():
        try:
            # 获取流式响应迭代器
            response_stream = rag.chain.stream({"question": request.prompt}, session_config)
            
            # 逐个yield响应块（SSE格式）
            for chunk in response_stream:
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
        except Exception as e:
            # 错误处理：返回标准错误格式
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    # 返回SSE格式的流式响应
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Timestamp": timestamp,
            "Access-Control-Allow-Origin": "*",
        }
    )

# 非流式响应接口
@router.post("/completion", response_class=JSONResponse)
async def chat_completion(request: ChatRequest):
    """
    非流式聊天接口
    返回完整的JSON响应，专门处理一次性输出场景
    """
    try:
        rag, session_config, timestamp = _init_rag_session(request)
        # 非流式调用
        response = rag.chain.invoke({"question": request.prompt}, session_config)
        return JSONResponse(
            content={"session_id": request.session_id, "response": response},
            status_code=200,
            headers={
                "Timestamp": timestamp,
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        # 统一异常处理
        return JSONResponse(
            content={"session_id": request.session_id, "error": str(e)},
            status_code=500,
            headers={
                "Timestamp": timestamp,
                "Access-Control-Allow-Origin": "*",
            }
        )
