from pydantic import BaseModel, Field


# 定义请求模型
class ChatRequest(BaseModel):
    session_id: str = Field(None, description="会话ID")
    prompt: str = Field(..., description="用户提问内容", min_length=1, max_length=2000)
