# -*- coding: utf-8 -*-

# import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
import yaml
import warnings

from models.RestfulModel import *
from routers import ocr, pdf_ocr
from utils.ImageHelper import *

# Suppress expected library warnings for cleaner logs
# Only suppress warnings from PaddlePaddle/PaddleOCR libraries
# These warnings are informational and don't affect functionality
# Using specific patterns to avoid suppressing unintended warnings
warnings.filterwarnings("ignore", message=r"^`lang` and `ocr_version` will be ignored", module="paddleocr.*")
warnings.filterwarnings("ignore", message=r"^No ccache found", module="paddle.*")
warnings.filterwarnings("ignore", message=r"^Non compatible API\.", module="paddle.*")
warnings.filterwarnings("ignore", message=r"^To copy construct from a tensor,", module="paddle.*")

app = FastAPI(title="Paddle OCR API",
              description="基于 Paddle OCR 和 FastAPI 的自用接口")


# 跨域设置
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Health check endpoint for Docker/Dokploy
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for container orchestration and load balancers.
    Returns 200 OK if the service is running properly.
    """
    return {
        "status": "healthy",
        "service": "PaddleOCR FastAPI",
        "version": "3.x"
    }

app.include_router(ocr.router)
app.include_router(pdf_ocr.router)

# uvicorn.run(app=app, host="0.0.0.0", port=8000)
