import json

from fastapi import APIRouter, Depends
from app.api.v1.knowledge.schema import KnowledgeRequest, KnowledgeResponse
from fastapi.responses import JSONResponse

from app.core.rag import RAG
from app.core.knowledge_base import KnowledgeBase

# 定义模块路由
router = APIRouter(
    prefix="/knowledge",    # 接口前缀：/v1/knowledge
    tags=["知识库接口"],  # 文档分类标签
    # dependencies=[Depends(verify_user_token)]  # 该模块所有接口复用鉴权依赖
)


@router.post("/upload", response_class=JSONResponse)
async def upload_knowledge(request: KnowledgeRequest):
    """
    上传文件到知识库
    根据文件名（唯一）和内容将文件上传到知识库中，并返回上传结果
    """
    kb = KnowledgeBase()
    result = kb.upload(request.data, request.file_name)

    reponse = KnowledgeResponse(
        file_name=request.file_name, 
        message=result
    )

    return JSONResponse(
        content=reponse.dict(),
        status_code=200
    )

@router.get("/get", response_class=JSONResponse)
async def get_knowledge(category: str = 'all'):
    """
    获取知识库
    根据分类获取知识库中的内容，如果不指定分类则返回所有内容
    """
    kb = KnowledgeBase()
    items = kb.get(category)

    return JSONResponse(
        content={"items": items},
        status_code=200
    )

