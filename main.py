from fastapi import FastAPI
from app.api import api_router
from app.core.config import settings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI实例
app = FastAPI(title="AI客服后台", version="1.0")

app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源（前端域名，多个用列表）
    allow_origins=[
        "http://localhost:8080",  # 本地开发环境（必加）
        "http://127.0.0.1:8080",  # 备用本地地址
        "https://yindongwen.top",    # 生产环境前端域名（如有）
        "*"  # 临时测试：允许所有域名（生产环境不推荐）
    ],
    allow_credentials=True,  # 允许携带 Cookie/认证信息
    allow_methods=["*"],     # 允许所有 HTTP 方法（GET/POST/PUT 等）
    allow_headers=["*"],     # 允许所有请求头
    # 额外：允许跨域请求的预检（OPTIONS）缓存时间（减少预检请求）
    max_age=3600
)

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
