# 聚合所有模块的路由，便于入口文件统一注册
from fastapi import APIRouter
from app.api.v1.chat.router import router as chat_router
from app.api.v1.history.router import router as history_router
from app.api.v1.knowledge.router import router as knowledge_router


# 总路由
api_router = APIRouter(prefix="/v1")  # 所有接口统一前缀/v1
# 注册各模块路由
api_router.include_router(chat_router) 
api_router.include_router(history_router)
api_router.include_router(knowledge_router) 
