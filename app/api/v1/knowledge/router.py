import json

from fastapi import APIRouter, Depends
from app.api.v1.knowledge.schema import KnowledgeRequest
from fastapi.responses import StreamingResponse

from app.core.rag import RAG
from app.core.knowledge_base import KnowledgeBase

# 定义模块路由
router = APIRouter(
    prefix="/knowledge",    # 接口前缀：/v1/knowledge
    tags=["知识库接口"],  # 文档分类标签
    # dependencies=[Depends(verify_user_token)]  # 该模块所有接口复用鉴权依赖
)


@router.post("/upload")
async def upload_knowledge(request: KnowledgeRequest):
    """
    上传文件到知识库
    """
    kb = KnowledgeBase()
    result = kb.upload(request.data, request.file_name)
    return {"message": result}


