from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.api.v1.history.schema import HistoryRequest, HistoryResponse, Message
from app.core.history_store import get_history


# 定义模块路由
router = APIRouter(
    prefix="/history",    # 接口前缀：/v1/history
    tags=["历史记录接口"],  # 文档分类标签
    # dependencies=[Depends(verify_user_token)]  # 该模块所有接口复用鉴权依赖
)

# 查询对话历史接口
@router.post("/query", response_class=JSONResponse)
async def query_history(request: HistoryRequest):
    """
    查询对话历史接口
    根据会话ID返回完整的对话历史记录
    """
    try:
        # 获取对话历史存储实例
        history_store = get_history(request.session_id)
        # 获取所有消息
        messages = history_store.messages
        total = len(messages)

        # 取最后N条消息（最新的）
        if request.limit and request.limit > 0:
            messages = messages[-request.limit:]  
        
        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(Message(
                role=msg.type,
                content=msg.content,
                timestamp=msg.additional_kwargs.get("timestamp", '')
            ))
        
        # 构建响应
        response = HistoryResponse(
            session_id=request.session_id,
            messages=formatted_messages,
            total=total 
        )
        
        return JSONResponse(
            content=response.dict(),
            status_code=200
        )
    except Exception as e:
        # 统一异常处理
        return JSONResponse(
            content={"session_id": request.session_id, "error": str(e)},
            status_code=500
        )
