from pydantic import BaseModel, Field
from datetime import datetime


# 定义请求模型
class ChatRequest(BaseModel):
    session_id: str = Field(None, description="会话ID")
    timestamp: datetime = Field(None, description="请求时间戳，ISO格式字符串")
    prompt: str = Field(..., description="用户提问内容", min_length=1, max_length=2000)
