from pydantic import BaseModel, Field
from typing import List, Optional

# 知识库记录
class KnowledgeRecord(BaseModel):
    id: str = Field(..., description="唯一标识：文件标题/商品ID/推荐ID", min_length=1)
    category: str = Field(default='file', description="知识库分类")
    url: list[str] = Field(default_factory=list, description="文件URL列表")
    md5: str = Field(..., description="内容MD5")
    chroma_ids: list[str] = Field(default_factory=list, description="向量ID列表")
    create_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    update_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="更新时间")


# 知识库上传/更新
class KnowledgeRequest(BaseModel):
    id: str = Field(..., description="唯一标识：文件标题/商品ID/推荐ID", min_length=1)
    category: Optional[str] = Field(default='file', description="知识库分类", min_length=1)
    content: str = Field(..., description="内容", min_length=1)
    url: List[str] = Field(default=[], description="文件URL列表")


class KnowledgeResponse(BaseModel):
    id: str = Field(..., description="唯一标识：文件标题/商品ID/推荐ID", min_length=1)
    message: str = Field(..., description="响应消息")
