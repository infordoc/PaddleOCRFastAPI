# -*- coding: utf-8 -*-

from typing import List, Set, Optional

from pydantic import BaseModel


class OCRModel(BaseModel):
    coordinate: List  # 图像坐标
    result: Set


class Base64PostModel(BaseModel):
    base64_str: str  # base64字符串
    detection_model: Optional[str] = None  # 检测模型名称
    recognition_model: Optional[str] = None  # 识别模型名称


class PDFBase64PostModel(BaseModel):
    base64_str: str  # PDF base64字符串
    detection_model: Optional[str] = None  # 检测模型名称
    recognition_model: Optional[str] = None  # 识别模型名称
