import json

from fastapi import APIRouter, Query, Path
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
    上传文件/商品/推荐等知识到知识库
    根据文件名（唯一）和内容将文件上传到知识库中，并返回上传结果
    """
    kb = KnowledgeBase()
    result = kb.upload(request)

    response = KnowledgeResponse(
        id=request.id,
        message=result
    )

    return JSONResponse(
        content=response.dict(),
        status_code=200
    )

@router.get("/get", response_class=JSONResponse)
async def get_knowledge(category: str = Query(None, description="知识库分类，不指定则返回所有内容")):
    """
    获取知识库
    根据分类获取知识库中的内容，如果不指定分类则返回所有内容
    """
    kb = KnowledgeBase()
    result = kb.get(category)

    return JSONResponse(
        content=result.dict() if isinstance(result, dict) else result,
        status_code=200
    )

@router.put("/update/{id}", response_class=JSONResponse)
async def update_knowledge(
    request: KnowledgeRequest,
    id: str = Path(..., description="要更新的知识库记录ID"),
):
    """
    更新知识库
    根据id（文件标题/商品ID/推荐ID）更新知识库中的内容，如果内容有变更则重新生成向量
    """
    if request.id != id:
        raise HTTPException(
            status_code=400,
            detail=f"路径ID({id})与请求体ID({request.id})不一致，更新失败"
        )
    kb = KnowledgeBase()
    result = kb.update(request)

    response = KnowledgeResponse(
        id=request.id,
        message=result
    )

    return JSONResponse(
        content=response.dict(),
        status_code=200
    )

@router.delete("/delete/{id}", response_class=JSONResponse)
async def delete_knowledge(id: str = Path(..., description="要删除的知识库记录ID")):
    """
    删除知识库
    根据id（文件标题/商品ID/推荐ID）删除知识库中的内容
    """
    kb = KnowledgeBase()
    result = kb.remove(id)

    response = KnowledgeResponse(
        id=id,
        message=result
    )

    return JSONResponse(
        content=response.dict(),
        status_code=200
    )
