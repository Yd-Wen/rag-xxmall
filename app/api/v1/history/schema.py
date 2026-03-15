from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# 定义消息模型
class Message(BaseModel):
    role: str = Field(..., description="消息类型: human 或 ai")
    timestamp: str = Field(None, description="消息时间戳")
    content: str = Field(..., description="消息内容")


# 定义请求模型
class HistoryRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    limit: Optional[int] = Field(100, description="返回的消息数量限制，默认为100")


# 定义响应模型
class HistoryResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    messages: List[Message] = Field(..., description="对话历史消息列表")
    total: int = Field(..., description="消息总数")
