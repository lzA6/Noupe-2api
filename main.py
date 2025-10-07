# Noupe-local/main.py

import traceback
import time
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends, Header

from app.core.config import settings
from app.providers.noupe_provider import NoupeProvider

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION
)

# 实例化 Provider
noupe_provider = NoupeProvider()

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    检查 API 密钥的依赖项。
    如果设置了 API_MASTER_KEY，则请求头中必须包含正确的密钥。
    """
    if not settings.API_MASTER_KEY:
        logger.warning("警告：未配置 API_MASTER_KEY，服务将对所有请求开放。")
        return

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing Authorization header.",
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Use 'Bearer <your_api_key>'.",
        )
    
    if token != settings.API_MASTER_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid API Key.",
        )

@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: Request):
    """
    核心聊天路由，所有请求都交给 NoupeProvider 处理。
    """
    try:
        request_data = await request.json()
        logger.info("接收到聊天请求，认证通过，路由到 NoupeProvider...")
        return await noupe_provider.chat_completion(request_data, request)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"主路由发生内部服务器错误: {str(e)}")

@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
async def list_models():
    """
    返回兼容OpenAI格式的模型列表。
    """
    logger.info("接收到模型列表请求，认证通过...")
    
    model_names: List[str] = settings.SUPPORTED_MODELS
    
    model_data: List[Dict[str, Any]] = []
    for name in model_names:
        model_data.append({
            "id": name,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "system"
        })
        
    return {
        "object": "list",
        "data": model_data
    }

@app.get("/")
def root():
    """根路由，提供服务基本信息。"""
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}

# 在启动时打印日志
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
