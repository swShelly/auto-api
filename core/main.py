"""
主应用入口 - FastAPI 实现

此模块提供：
- RESTful API 端点
- 健康检查端点
- 基础错误处理
- 日志记录
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# 配置日志
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="AUTO-API", description="测试自动化 API 服务", version="1.0.0")

# 应用配置
app.env = os.getenv("ENV", "development")
logger.info(f"应用启动，环境: {app.env}")


# ==================== 健康检查端点 ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点
    用于 CI/CD 流水线和负载均衡器检查应用状态
    """
    return {"status": "healthy", "environment": app.env, "service": "AUTO-API"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    就绪检查端点
    检查应用是否已准备好处理请求
    """
    return {"ready": True, "environment": app.env}


# ==================== 示例 API 端点 ====================
@app.get("/api/v1/status", tags=["Status"])
async def get_status():
    """获取应用状态"""
    return {"status": "running", "environment": app.env, "version": "1.0.0"}


@app.post("/api/v1/test", tags=["Tests"])
async def create_test(test_data: dict):
    """
    创建测试用例

    示例请求体：
    {
        "name": "Test Name",
        "description": "Test Description"
    }
    """
    logger.info(f"创建测试: {test_data.get('name')}")
    return {"id": 1, "status": "created", "data": test_data}


@app.get("/api/v1/test/{test_id}", tags=["Tests"])
async def get_test(test_id: int):
    """获取测试用例详情"""
    if test_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid test ID")

    return {"id": test_id, "name": f"Test {test_id}", "status": "passed"}


# ==================== 错误处理 ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    logger.error(f"HTTP 异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "status_code": exc.status_code})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未预期的错误: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "status_code": 500})


# ==================== 启动事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("AUTO-API 服务启动中...")
    logger.info(f"环境变量 ENV={app.env}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("AUTO-API 服务关闭")


# ==================== 根端点 ====================
@app.get("/", tags=["Root"])
async def root():
    """API 根端点"""
    return {"message": "欢迎使用 AUTO-API", "docs": "/docs", "openapi": "/openapi.json"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
