from pydantic import BaseModel, Field


# 知识库上传
class KnowledgeRequest(BaseModel):
    data: str = Field(..., description="文件内容", min_length=1)
    file_name: str = Field(..., description="文件名", min_length=1)

