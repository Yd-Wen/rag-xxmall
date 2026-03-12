from fastapi import FastAPI
from app.api import api_router
from app.core.config import settings
import uvicorn

# 创建FastAPI实例
app = FastAPI(title="AI客服后台", version="1.0")

# 注册所有路由
app.include_router(api_router)


# 根路径健康检查
@app.get("/")
async def root():
    return {"msg": "AI客服后台运行中"}


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host=settings.APP_HOST,
#         port=settings.APP_PORT,
#         reload=True  # 开发环境热重载
#     )
