import json

from fastapi import APIRouter, Depends
from app.api.v1.chat.schema import ChatRequest
from fastapi.responses import StreamingResponse

from app.core.rag import RAG

# 定义模块路由
router = APIRouter(
    prefix="/chat",    # 接口前缀：/v1/chat
    tags=["聊天接口"],  # 文档分类标签
    # dependencies=[Depends(verify_user_token)]  # 该模块所有接口复用鉴权依赖
)


@router.post("/stream", response_class=StreamingResponse)
async def chat(request: ChatRequest):
    session_config = {
        "configurable": {
            "session_id": request.session_id
        }
    }

    rag = RAG()

    if request.stream:
        # 流式响应实现
        async def generate_response():
            try:
                # 获取流式响应迭代器
                response_stream = rag.chain.stream({"question": request.prompt}, session_config)

                # 逐个yield响应块
                for chunk in response_stream:
                    # 将每个chunk包装成JSON格式
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"

                # 发送结束标记
                yield "data: [DONE]\n\n"
            except Exception as e:
                # 错误处理
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"

        # 返回SSE格式的流式响应
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # 非流式响应
        response = rag.chain.invoke({"question": request.prompt}, session_config)
        return {"session_id": request.session_id, "response": response}

    # if request.stream:
    #     # return StreamingResponse(
    #     #     rag.chain.stream({"question": request.prompt}, session_config),
    #     #     media_type="text/plain; charset=utf-8"
    #     # )
    #     return rag.chain.stream({"question": request.prompt}, session_config)
    # else:
    #     response = rag.chain.invoke({"question": request.prompt}, session_config)
    #     return {"session_id": request.session_id, "response": response}
