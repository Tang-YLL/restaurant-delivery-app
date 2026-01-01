"""
FastAPI应用主文件
配置静态文件服务和API路由
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db
from app.core.redis_client import init_redis, close_redis
from app.core.logger import setup_logger
from app.core.exceptions import (
    AppException, app_exception_handler,
    validation_exception_handler, sqlalchemy_exception_handler,
    general_exception_handler
)
from app.api import auth, users, products, categories, cart, orders, reviews, admin_auth, favorites
from app.api.admin import orders as admin_orders, analytics, users as admin_users, reviews as admin_reviews, audit_logs, products as admin_products, uploads

settings = get_settings()
logger = setup_logger()

# 检查是否为测试环境
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info("应用启动中...")
    await init_db()
    if not IS_TESTING:
        await init_redis()
    logger.info("应用启动完成")
    yield
    # 关闭事件
    logger.info("应用关闭中...")
    if not IS_TESTING:
        await close_redis()
    logger.info("应用关闭完成")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="餐厅管理系统API",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 挂载静态文件服务（仅在非测试环境）
if not IS_TESTING:
    # 挂载/static目录
    try:
        app.mount("/static", StaticFiles(directory=settings.STATIC_FILES_PATH), name="static")
        logger.info(f"静态文件已挂载: /static -> {settings.STATIC_FILES_PATH}")
    except RuntimeError as e:
        logger.warning(f"/static挂载失败: {e}")

    # 挂载商品图片目录 - 注意：uploads.py返回的路径是/images/products/xxx.png
    # 所以这里应该挂载到public/images，而不是public/images/products
    try:
        images_dir = os.path.abspath("public/images")
        if os.path.exists(images_dir):
            app.mount("/images", StaticFiles(directory=images_dir), name="images")
            logger.info(f"图片目录已挂载: /images -> {images_dir}")
        else:
            logger.warning(f"图片目录不存在: {images_dir}")
    except RuntimeError as e:
        logger.warning(f"/images挂载失败: {e}")

# 注册API路由
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(cart.router, prefix=settings.API_V1_PREFIX)
app.include_router(orders.router, prefix=settings.API_V1_PREFIX)
app.include_router(reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(favorites.router, prefix=settings.API_V1_PREFIX)

# 注册管理后台API路由
app.include_router(admin_orders.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_users.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_products.router, prefix=settings.API_V1_PREFIX)
app.include_router(uploads.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "餐厅管理系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "static_files": "/static"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
