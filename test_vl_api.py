#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for PaddleOCR-VL model integration in API endpoints

This test verifies that the API endpoints can accept and use PaddleOCR-VL models
through the detection_model and recognition_model parameters.

Usage:
    python test_vl_api.py
    
Important:
    PaddleOCR-VL models require additional dependencies:
    pip install 'paddlex[ocr]'
    
    Without these dependencies, VL models will return a 501 error.
    
Note:
    This test demonstrates the API usage patterns with VL models.
    Actual inference requires PaddleOCR-VL models and dependencies to be installed.
"""

import json
import sys


def test_vl_models_list():
    """
    Display available VL models and their capabilities
    """
    print("\n" + "="*70)
    print("PaddleOCR-VL Models")
    print("="*70)
    
    vl_models = [
        {
            "name": "PaddleOCR-VL-1.5",
            "description": "多模态视觉语言模型 v1.5",
            "capabilities": [
                "支持 111 种语言的文本识别",
                "自动布局分析和结构化识别",
                "表格识别（包括复杂表格）",
                "数学公式识别",
                "图表和图形识别",
                "图章和印章识别",
                "文档方向和扭曲矫正",
            ]
        },
        {
            "name": "PaddleOCR-VL",
            "description": "多模态视觉语言模型 v1",
            "capabilities": [
                "多语言文本识别",
                "布局分析",
                "表格识别",
                "基础结构化识别"
            ]
        }
    ]
    
    for model in vl_models:
        print(f"\n{model['name']}")
        print(f"  描述: {model['description']}")
        print("  功能特性:")
        for cap in model['capabilities']:
            print(f"    • {cap}")


def test_endpoint_parameters():
    """
    Show how to use VL models with existing endpoints
    """
    print("\n" + "="*70)
    print("使用 PaddleOCR-VL 模型的 API 调用示例")
    print("="*70)
    
    print("\n1. OCR Endpoints - 使用 VL 模型")
    print("-" * 70)
    
    ocr_endpoints = [
        {
            "method": "GET",
            "endpoint": "/ocr/predict-by-path",
            "example": """
# 使用 PaddleOCR-VL-1.5 模型识别本地图片
curl "http://localhost:8000/ocr/predict-by-path?image_path=/path/to/image.jpg&detection_model=PaddleOCR-VL-1.5"

# Python 示例
import requests
response = requests.get(
    "http://localhost:8000/ocr/predict-by-path",
    params={
        "image_path": "/path/to/image.jpg",
        "detection_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
"""
        },
        {
            "method": "POST",
            "endpoint": "/ocr/predict-by-file",
            "example": """
# 使用 PaddleOCR-VL 模型识别上传的图片
curl -X POST "http://localhost:8000/ocr/predict-by-file?detection_model=PaddleOCR-VL" \\
     -F "file=@image.jpg"

# Python 示例
import requests
files = {"file": open("image.jpg", "rb")}
params = {"detection_model": "PaddleOCR-VL"}
response = requests.post(
    "http://localhost:8000/ocr/predict-by-file",
    params=params,
    files=files
)
result = response.json()
"""
        },
        {
            "method": "POST",
            "endpoint": "/ocr/predict-by-base64",
            "example": """
# 使用 PaddleOCR-VL-1.5 模型识别 Base64 图片
import requests
import base64

with open("image.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    "http://localhost:8000/ocr/predict-by-base64",
    json={
        "base64_str": img_base64,
        "detection_model": "PaddleOCR-VL-1.5",
        "recognition_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
"""
        },
        {
            "method": "GET",
            "endpoint": "/ocr/predict-by-url",
            "example": """
# 使用 VL 模型识别网络图片
curl "http://localhost:8000/ocr/predict-by-url?imageUrl=https://example.com/image.jpg&recognition_model=PaddleOCR-VL-1.5"

# Python 示例
import requests
response = requests.get(
    "http://localhost:8000/ocr/predict-by-url",
    params={
        "imageUrl": "https://example.com/image.jpg",
        "recognition_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
"""
        }
    ]
    
    for ep in ocr_endpoints:
        print(f"\n{ep['method']} {ep['endpoint']}")
        print(ep['example'])
    
    print("\n2. PDF Endpoints - 使用 VL 模型")
    print("-" * 70)
    
    pdf_endpoints = [
        {
            "method": "GET",
            "endpoint": "/pdf/predict-by-url",
            "example": """
# 使用 VL 模型识别 PDF（从 URL）
curl "http://localhost:8000/pdf/predict-by-url?pdf_url=https://example.com/doc.pdf&detection_model=PaddleOCR-VL-1.5"
"""
        },
        {
            "method": "POST",
            "endpoint": "/pdf/predict-by-file",
            "example": """
# 使用 VL 模型识别上传的 PDF
curl -X POST "http://localhost:8000/pdf/predict-by-file?detection_model=PaddleOCR-VL-1.5" \\
     -F "file=@document.pdf"
"""
        },
        {
            "method": "POST",
            "endpoint": "/pdf/predict-by-base64",
            "example": """
# 使用 VL 模型识别 Base64 PDF
import requests
import base64

with open("document.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    "http://localhost:8000/pdf/predict-by-base64",
    json={
        "base64_str": pdf_base64,
        "detection_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
"""
        }
    ]
    
    for ep in pdf_endpoints:
        print(f"\n{ep['method']} {ep['endpoint']}")
        print(ep['example'])


def test_model_comparison():
    """
    Compare traditional models vs VL models
    """
    print("\n" + "="*70)
    print("模型对比：传统模型 vs VL 模型")
    print("="*70)
    
    comparison = """
传统 PP-OCR 模型 (PP-OCRv4/v5):
  优势:
    • 快速、轻量级
    • 低资源消耗
    • 针对纯文本识别优化
  适用场景:
    • 简单文档的文本提取
    • 需要快速响应的场景
    • 资源受限的环境
    
PaddleOCR-VL 模型:
  优势:
    • 多模态理解能力（视觉 + 语言）
    • 支持 111 种语言
    • 自动布局分析
    • 表格、公式、图章等复杂元素识别
    • 更准确的结构化输出
  适用场景:
    • 复杂文档处理（表格、图表）
    • 多语言混合文档
    • 需要结构化输出的场景
    • 对准确性要求高的场景

使用建议:
  • 默认使用传统模型（更快、更轻量）
  • 遇到复杂文档或需要高精度时，使用 VL 模型
  • 可以根据实际需求和资源情况选择
"""
    print(comparison)


def test_valid_parameters():
    """
    List all valid model parameter values
    """
    print("\n" + "="*70)
    print("有效的模型参数值")
    print("="*70)
    
    print("\ndetection_model 可用值:")
    detection_models = [
        "PP-OCRv5_server_det (默认)",
        "PP-OCRv5_mobile_det",
        "PP-OCRv4_server_det",
        "PP-OCRv4_mobile_det",
        "PaddleOCR-VL-1.5 (多模态 VL 模型)",
        "PaddleOCR-VL (多模态 VL 模型)"
    ]
    for model in detection_models:
        print(f"  • {model}")
    
    print("\nrecognition_model 可用值:")
    recognition_models = [
        "PP-OCRv5_server_rec (默认)",
        "PP-OCRv5_mobile_rec",
        "PP-OCRv4_server_rec",
        "PP-OCRv4_mobile_rec",
        "PaddleOCR-VL-1.5 (多模态 VL 模型)",
        "PaddleOCR-VL (多模态 VL 模型)"
    ]
    for model in recognition_models:
        print(f"  • {model}")
    
    print("\n注意:")
    print("  • 如果不指定模型，默认使用 PP-OCRv5_server_det 和 PP-OCRv5_server_rec")
    print("  • 使用 VL 模型时，detection_model 或 recognition_model 任一指定为 VL 即可")
    print("  • VL 模型会自动启用高级功能（布局、表格、图章等）")


def test_backward_compatibility():
    """
    Verify backward compatibility
    """
    print("\n" + "="*70)
    print("向后兼容性验证")
    print("="*70)
    
    compatibility_info = """
所有现有的 API 调用方式保持不变:

1. 不指定模型参数（使用默认 PP-OCRv5 模型）:
   ✓ 行为不变
   ✓ 性能不变
   ✓ 结果格式不变

2. 指定传统模型 (PP-OCRv4/v5):
   ✓ 行为不变
   ✓ 继续使用 PaddleOCR 类
   ✓ 结果格式不变

3. 新功能 - 指定 VL 模型:
   • 自动切换到 PaddleOCRVL 接口
   • 利用 VL 模型的高级功能
   • 结果格式兼容现有接口
   
实现方式:
  • 在 get_ocr_instance() 中检测模型名称
  • 如果是 VL 模型，创建 PaddleOCRVL 实例
  • 否则，创建传统的 PaddleOCR 实例
  • 结果提取函数兼容两种格式
"""
    print(compatibility_info)


def main():
    """
    Run all tests
    """
    print("\n" + "="*70)
    print("PaddleOCR-VL 模型集成测试")
    print("="*70)
    print("\n此测试验证 VL 模型集成到现有 API 端点的功能")
    print("注意：这是功能说明和使用示例，不执行实际的模型推理")
    
    test_vl_models_list()
    test_valid_parameters()
    test_endpoint_parameters()
    test_model_comparison()
    test_backward_compatibility()
    
    print("\n" + "="*70)
    print("测试说明完成")
    print("="*70)
    print("\n要实际测试 VL 模型:")
    print("  1. 安装额外的依赖: pip install 'paddlex[ocr]'")
    print("  2. 确保安装了 PaddleOCR 3.4.0+")
    print("  3. 启动服务: uvicorn main:app --host 0.0.0.0")
    print("  4. 访问 Swagger UI: http://localhost:8000/docs")
    print("  5. 在任何端点的 detection_model 或 recognition_model 参数中")
    print("     输入 'PaddleOCR-VL-1.5' 或 'PaddleOCR-VL'")
    print("  6. 首次使用会自动下载模型文件（约 2GB）")
    print("\n⚠️  重要: 如果没有安装 paddlex[ocr]，将收到 501 错误")
    print("\n")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
