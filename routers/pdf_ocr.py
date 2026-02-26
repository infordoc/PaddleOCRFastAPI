# -*- coding: utf-8 -*-
"""
PDF OCR 路由模块

功能：从 PDF 文档中提取表格数据
- 支持通过 URL、上传文件或 Base64 的方式处理 PDF
- 自动检测并提取 PDF 中的表格结构
- 基于文本位置坐标智能重建表格的行列关系
- 返回结构化的表格数据（表头 + 数据行）
- 支持自定义 OCR 模型选择

作者：PaddleOCR FastAPI
版本：2.0
"""

from fastapi import APIRouter, HTTPException, UploadFile, status, Query
from models.RestfulModel import *
from models.OCRModel import PDFBase64PostModel
from paddleocr import PaddleOCR
import requests
import os
import tempfile
import fitz  # PyMuPDF - PDF处理库
import numpy as np
from PIL import Image
import io
import base64
from typing import Optional, Union

# 从环境变量获取 OCR 语言配置，默认为中文
OCR_LANGUAGE = os.environ.get("OCR_LANGUAGE", "ch")

# 创建路由器，所有接口前缀为 /pdf
router = APIRouter(prefix="/pdf", tags=["PDF OCR"])

# OCR 实例缓存（支持不同模型配置）
_pdf_ocr_instances = {}

# VL model names
VL_MODELS = ["PaddleOCR-VL-1.5", "PaddleOCR-VL"]

def is_vl_model(model_name: Optional[str]) -> bool:
    """Check if the model name is a VL model"""
    return model_name in VL_MODELS if model_name else False

def get_pdf_ocr(detection_model: Optional[str] = None, recognition_model: Optional[str] = None) -> Union['PaddleOCR', 'PaddleOCRVL']:
    """
    获取 PaddleOCR 3.x 或 PaddleOCRVL 实例（单例模式，支持模型选择）
    
    采用延迟初始化策略，只在第一次调用时创建 OCR 实例，
    避免服务启动时加载模型导致启动变慢。
    
    Args:
        detection_model: 检测模型名称 (默认: PP-OCRv5_server_det)
        recognition_model: 识别模型名称 (默认: PP-OCRv5_server_rec)
    
    模型配置（PaddleOCR 3.x）：
        检测模型:
            - PP-OCRv5_server_det (默认，更准确)
            - PP-OCRv5_mobile_det (轻量级，更快)
            - PP-OCRv4_mobile_det (v4轻量级)
            - PP-OCRv4_server_det (v4服务器版)
            - PaddleOCR-VL-1.5 (多模态视觉语言模型，支持表格、公式、图章、111种语言)
            - PaddleOCR-VL (多模态视觉语言模型)
        
        识别模型:
            - PP-OCRv5_server_rec (默认，更准确)
            - PP-OCRv5_mobile_rec (轻量级，更快)
            - PP-OCRv4_mobile_rec (v4轻量级)
            - PP-OCRv4_server_rec (v4服务器版)
            - PaddleOCR-VL-1.5 (多模态视觉语言模型，支持表格、公式、图章、111种语言)
            - PaddleOCR-VL (多模态视觉语言模型)
    
    Returns:
        Union[PaddleOCR, PaddleOCRVL]: OCR 实例对象
        
    Note:
        当使用 PaddleOCR-VL 模型时，将使用 PaddleOCRVL 接口进行推理，
        支持布局分析、表格识别、图表识别、图章识别等高级功能。
    """
    # 检查是否使用 VL 模型
    use_vl = is_vl_model(detection_model) or is_vl_model(recognition_model)
    
    if use_vl:
        # 确定使用哪个 VL 版本 - 检查两个参数中是否包含 "1.5"
        vl_version = "v1.5" if ("1.5" in (detection_model or "") or "1.5" in (recognition_model or "")) else "v1"
        
        # 创建缓存键
        cache_key = f"VL_{vl_version}_{OCR_LANGUAGE}"
        
        # 如果实例已存在，直接返回
        if cache_key in _pdf_ocr_instances:
            return _pdf_ocr_instances[cache_key]
        
        # 创建 PaddleOCRVL 实例
        from paddleocr import PaddleOCRVL
        
        ocr_instance = PaddleOCRVL(
            pipeline_version=vl_version,
            device=os.environ.get("OCR_DEVICE", "cpu"),
            use_layout_detection=True,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_chart_recognition=True,
            use_seal_recognition=True,
            use_ocr_for_image_block=True,
            format_block_content=True,
            merge_layout_blocks=True,
        )
        
        # 缓存实例
        _pdf_ocr_instances[cache_key] = ocr_instance
        
        return ocr_instance
    else:
        # 使用默认模型 - Server 版本更准确
        if not detection_model:
            detection_model = "PP-OCRv5_server_det"
        if not recognition_model:
            recognition_model = "PP-OCRv5_server_rec"
        
        # 创建缓存键
        cache_key = f"{detection_model}_{recognition_model}_{OCR_LANGUAGE}"
        
        # 如果实例已存在，直接返回
        if cache_key in _pdf_ocr_instances:
            return _pdf_ocr_instances[cache_key]
        
        # 创建新实例
        # PaddleOCR 3.x unified interface with customizable models
        ocr_instance = PaddleOCR(
            text_detection_model_name=detection_model,  # 文本检测模型
            text_recognition_model_name=recognition_model,  # 文本识别模型
            use_angle_cls=True,  # 启用角度分类器
            use_doc_orientation_classify=False,  # 禁用文档方向分类
            use_doc_unwarping=False,  # 禁用文档矫正
            lang=OCR_LANGUAGE  # 语言设置
        )
        
        # 缓存实例
        _pdf_ocr_instances[cache_key] = ocr_instance
        
        return ocr_instance


def pdf_to_images(pdf_path: str):
    """
    将 PDF 文档的每一页转换为高清图像文件
    
    处理流程：
    1. 使用 PyMuPDF 打开 PDF 文档
    2. 逐页渲染为图像，分辨率提高 2 倍（提升 OCR 识别精度）
    3. 将图像保存为临时 PNG 文件
    4. 返回临时文件路径列表
    
    Args:
        pdf_path (str): PDF 文件的绝对路径
    
    Returns:
        list: 包含每页图像信息的列表，每个元素是字典：
            {
                'page_num': int,  # 页码（从1开始）
                'path': str,      # 临时图像文件路径
                'width': int,     # 图像宽度（像素）
                'height': int     # 图像高度（像素）
            }
    
    注意：
        - 调用者需要负责删除返回的临时文件
        - 使用 2 倍分辨率渲染以提高 OCR 识别准确率
    """
    temp_files = []
    pdf_document = fitz.open(pdf_path)
    
    # 遍历 PDF 的每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # 设置渲染矩阵，2.0 表示 2 倍放大（提高 OCR 识别精度）
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        
        # 将 PyMuPDF 的 Pixmap 转换为 PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # 创建临时文件并保存图像
        # delete=False 表示不自动删除，需要手动清理
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(tmp_file.name, 'PNG')
        tmp_file.close()
        
        # 记录页面信息
        temp_files.append({
            'page_num': page_num + 1,  # 页码从 1 开始
            'path': tmp_file.name,      # 临时文件路径
            'width': pix.width,         # 图像宽度
            'height': pix.height        # 图像高度
        })
    
    pdf_document.close()
    return temp_files


def _np_to_list(value):
    """
    将 numpy 数组转换为 Python 列表（用于 JSON 序列化）
    
    Args:
        value: 任意类型的值
    
    Returns:
        如果是 numpy 数组则返回列表，否则原样返回
    """
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def reconstruct_table(texts, boxes, y_threshold=30, min_cols=3):
    """
    基于文本位置坐标智能重建表格结构
    
    核心算法：
    1. 按 Y 轴坐标聚类识别表格的"行"（Y 坐标接近的文本属于同一行）
    2. 对每一行按 X 轴坐标排序识别"列"的顺序
    3. 统计每行的列数，找出最常见的列数作为标准列数
    4. 筛选出列数符合标准的规则行
    5. 第一个规则行作为表头，其余作为数据行
    
    Args:
        texts (list): 识别出的文本列表，如 ['Name', 'Age', 'John', '25']
        boxes (list): 对应的边界框坐标列表，格式 [x1, y1, x2, y2]
        y_threshold (int): Y 轴阈值，判断是否在同一行的依据（默认 30 像素）
        min_cols (int): 表格最少列数，少于此值不认为是表格（默认 3 列）
    
    Returns:
        dict: 表格数据结构
            {
                'has_table': bool,     # 是否检测到有效表格
                'headers': list,       # 表头列表，如 ['Name', 'Age', 'City']
                'rows': list[list],    # 数据行列表，如 [['John', '25', 'NYC'], ['Mary', '30', 'LA']]
                'total_rows': int,     # 数据行总数（不含表头）
                'total_cols': int      # 列总数
            }
    
    表格检测规则：
        - 至少需要 6 个文本框（最少 3 列 x 2 行）
        - 至少需要 2 行数据（1 行表头 + 1 行数据）
        - 大多数行的列数应该一致
        - 列数需要 >= min_cols（默认 3）
    
    示例：
        >>> texts = ['Name', 'Age', 'John', '25']
        >>> boxes = [[10, 10, 50, 30], [60, 10, 100, 30], 
        ...          [10, 40, 50, 60], [60, 40, 100, 60]]
        >>> result = reconstruct_table(texts, boxes)
        >>> result['has_table']
        True
        >>> result['headers']
        ['Name', 'Age']
        >>> result['rows']
        [['John', '25']]
    """
    # 基本验证
    if not texts or not boxes or len(texts) != len(boxes):
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 至少需要 6 个文本框才可能构成表格（3列 x 2行）
    if len(texts) < 6:
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 步骤1：构建文本项目列表，计算每个文本框的中心点和尺寸
    items = []
    for i, (text, box) in enumerate(zip(texts, boxes)):
        if isinstance(box, list) and len(box) >= 4:
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            items.append({
                'text': text,
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'x_center': (x1 + x2) / 2,  # X 轴中心点
                'y_center': (y1 + y2) / 2,  # Y 轴中心点
                'width': x2 - x1,            # 宽度
                'height': y2 - y1,           # 高度
                'index': i                    # 原始索引
            })
    
    if len(items) < 6:
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 步骤2：按 Y 坐标分组，识别表格的"行"
    # 先按 Y 轴中心点排序
    items.sort(key=lambda x: x['y_center'])
    
    rows = []
    current_row = [items[0]]
    
    # 遍历所有项目，根据 Y 坐标阈值判断是否属于同一行
    for item in items[1:]:
        # 如果当前项目的 Y 坐标与当前行的第一个项目接近，则认为在同一行
        if abs(item['y_center'] - current_row[0]['y_center']) < y_threshold:
            current_row.append(item)
        else:
            # 否则，当前行结束，将其按 X 坐标排序后保存
            current_row.sort(key=lambda x: x['x_center'])
            rows.append(current_row)
            current_row = [item]
    
    # 添加最后一行
    if current_row:
        current_row.sort(key=lambda x: x['x_center'])
        rows.append(current_row)
    
    # 步骤3：检查是否是有效表格
    if len(rows) < 2:  # 至少需要 2 行（表头 + 数据）
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 步骤4：统计列数分布，找出最常见的列数
    col_counts = [len(row) for row in rows]
    max_cols = max(col_counts)
    
    # 列数必须 >= min_cols
    if max_cols < min_cols:
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 找出列数符合要求的行（列数 >= min_cols）
    from collections import Counter
    valid_col_counts = [c for c in col_counts if c >= min_cols]
    
    if not valid_col_counts:
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 找出出现次数最多的列数（标准列数）
    col_count_freq = Counter(valid_col_counts)
    most_common_cols = col_count_freq.most_common(1)[0][0]
    
    # 步骤5：筛选出列数为标准列数的规则行
    regular_rows = [row for row in rows if len(row) == most_common_cols]
    
    if len(regular_rows) < 2:  # 至少需要表头+数据各1行
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 步骤6：提取表头和数据行
    # 第一个规则行作为表头
    headers = [item['text'] for item in regular_rows[0]]
    
    # 其余规则行作为数据行
    data_rows = []
    for row in regular_rows[1:]:
        row_data = [item['text'] for item in row]
        # 确保每行列数一致（补齐或裁剪）
        while len(row_data) < len(headers):
            row_data.append('')
        data_rows.append(row_data[:len(headers)])
    
    # 至少要有 1 行数据
    if len(data_rows) < 1:
        return {'has_table': False, 'headers': [], 'rows': []}
    
    # 返回成功识别的表格
    return {
        'has_table': True,
        'headers': headers,
        'rows': data_rows,
        'total_rows': len(data_rows),
        'total_cols': len(headers)
    }


def extract_pdf_ocr_data(result, page_num):
    """
    从 PaddleOCR 3.x 或 PaddleOCRVL 识别结果中提取表格数据，非表格页面返回 None
    
    处理流程：
    1. 兼容性处理：支持 PaddleOCR 3.x OCRResult 对象、列表格式和 PaddleOCRVL 结果
    2. 数据提取：从结果中分离文本列表和边界框坐标列表
    3. 表格重建：调用 reconstruct_table() 算法尝试识别表格结构
    4. 结果筛选：只返回包含有效表格的页面数据
    
    Args:
        result: PaddleOCR 3.x 或 PaddleOCRVL 识别结果，格式为：
            - OCRResult 对象：包含 rec_texts, rec_boxes, rec_scores 等属性
            - 列表格式：[OCRResult] 或传统格式兼容
            - PaddleOCRVL 结果：包含 ocr_texts, layout_res 等字段
        page_num (int): PDF 页码，从 1 开始编号
    
    Returns:
        dict or None: 如果检测到表格，返回：
            {
                'page': int,           # 页码
                'table': {
                    'headers': list,   # 表头
                    'rows': list,      # 数据行
                    'total_rows': int, # 行数
                    'total_cols': int  # 列数
                }
            }
            
        如果未检测到表格，返回 None（该页将被过滤）
    
    兼容性说明：
        - PaddleOCR 3.x 返回 OCRResult 对象（包含 rec_texts, rec_boxes, rec_scores 等属性）
        - PaddleOCRVL 返回包含 ocr_texts, layout_res 等字段的字典
        - 使用统一的 predict() 接口，结果结构更清晰
        - 本函数使用 hasattr() 和字段检查自动检测并兼容不同格式
    
    示例：
        >>> result = ocr.predict('page1.png')
        >>> page_data = extract_pdf_ocr_data(result, 1)
        >>> if page_data:
        ...     print(f"Page {page_data['page']}:")
        ...     print(f"Headers: {page_data['table']['headers']}")
        ...     print(f"Rows: {page_data['table']['rows']}")
    """
    debug = os.environ.get("OCR_DEBUG", "0") == "1"
    
    rec_texts = []  # 识别到的文本列表
    rec_boxes = []  # 对应的边界框坐标列表
    
    # 情况 A: result 是列表类型（PaddleOCR 2.6+ 返回格式）
    if isinstance(result, list) and len(result) > 0:
        item = result[0]  # 获取第一个元素
        
        # 检查是否是 VL 结果
        if isinstance(item, dict) and ('ocr_texts' in item or 'layout_res' in item):
            # 从 VL 结果提取文本和边界框
            ocr_texts = item.get('ocr_texts', [])
            if ocr_texts and isinstance(ocr_texts, list):
                for text_item in ocr_texts:
                    if isinstance(text_item, dict):
                        text = text_item.get('text', '')
                        bbox = text_item.get('bbox', [])
                        if text:
                            rec_texts.append(text)
                            rec_boxes.append(bbox)
            
            # 如果没有 ocr_texts，尝试 layout_res
            if not rec_texts:
                layout_res = item.get('layout_res', [])
                if layout_res and isinstance(layout_res, list):
                    for block in layout_res:
                        if isinstance(block, dict):
                            text = block.get('text', '')
                            bbox = block.get('bbox', [])
                            if text:
                                rec_texts.append(text)
                                rec_boxes.append(bbox)
        # 尝试作为对象访问属性（OCRResult 对象）
        elif hasattr(item, 'rec_texts') and hasattr(item, 'rec_boxes'):
            rec_texts = getattr(item, 'rec_texts', []) or []
            rec_boxes = getattr(item, 'rec_boxes', []) or []
            # 确保是列表类型
            rec_texts = list(rec_texts) if isinstance(rec_texts, (list, tuple)) else []
            rec_boxes = _np_to_list(rec_boxes)  # 转换 numpy 数组为列表
        
        # 尝试作为字典访问（旧版 PaddleOCR 返回格式）
        elif isinstance(item, dict):
            core = item.get('res', item)  # 提取核心数据
            if isinstance(core, dict):
                rec_texts = core.get('rec_texts', [])
                rec_boxes = core.get('rec_boxes', [])
                rec_texts = list(rec_texts) if isinstance(rec_texts, (list, tuple)) else []
                rec_boxes = _np_to_list(rec_boxes)
    
    # 调用表格重建算法
    table_data = reconstruct_table(rec_texts, rec_boxes)
    
    # 调试模式：输出识别结果
    if debug:
        has_table = table_data.get('has_table', False)
        print(f"[extract_pdf_ocr_data] 页 {page_num}: 识别到 {len(rec_texts)} 个文本，检测到表格: {has_table}")
    
    # 只返回包含表格的页面
    if table_data.get('has_table', False):
        return {
            'page': page_num,
            'table': {
                'headers': table_data['headers'],
                'rows': table_data['rows']
            }
        }
    else:
        # 没有表格则返回 None，后续会被过滤掉
        return None


def process_pdf(pdf_path: str, detection_model: Optional[str] = None, recognition_model: Optional[str] = None):
    """
    处理 PDF 文件并提取表格
    
    Args:
        pdf_path: PDF 文件路径
        detection_model: 检测模型名称
        recognition_model: 识别模型名称
    
    Returns:
        tuple: (all_results, image_files) - 提取结果和临时图像文件列表
    """
    # 将 PDF 转换为图像文件
    image_files = pdf_to_images(pdf_path)
    
    # 获取 OCR 实例
    ocr = get_pdf_ocr(detection_model, recognition_model)
    
    # 对每个页面进行 OCR 识别，只保留包含表格的页面
    all_results = []
    for img_info in image_files:
        result = ocr.predict(input=img_info['path'])
        page_data = extract_pdf_ocr_data(result, img_info['page_num'])
        if page_data is not None:  # 只添加包含表格的页面
            all_results.append(page_data)
    
    return all_results, image_files


@router.get('/predict-by-url', response_model=RestfulModel, summary="识别PDF URL")
async def predict_pdf_by_url(
    pdf_url: str,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    """
    通过 URL 下载并识别 PDF 文件中的表格数据
    
    API 端点：GET /pdf/predict-by-url?pdf_url=<url>
    
    工作流程：
    1. 参数验证：检查 URL 格式是否有效
    2. 文件下载：通过 HTTP 请求下载 PDF 文件到临时目录
    3. PDF 转图：将 PDF 每一页转换为高分辨率图像（2x）
    4. OCR 识别：对每页图像执行文字识别（可选择模型）
    5. 表格重建：使用坐标算法识别表格结构
    6. 结果过滤：只返回包含表格的页面
    7. 资源清理：删除临时文件
    
    Args:
        pdf_url (str): PDF 文件的 URL 地址，支持 http/https 协议
        detection_model (str, optional): 检测模型名称
        recognition_model (str, optional): 识别模型名称
    
    Returns:
        RestfulModel: 统一格式的 JSON 响应
            成功时 (200):
            {
                "resultcode": 200,
                "message": "Success: 提取到 N 个表格",
                "data": [
                    {
                        "page": 1,
                        "table": {
                            "headers": ["列1", "列2", "列3"],
                            "rows": [["值1", "值2", "值3"], ...],
                            "total_rows": 10,
                            "total_cols": 3
                        }
                    },
                    ...
                ]
            }
            
            失败时 (400/500):
            {
                "resultcode": 400/500,
                "message": "错误详细信息",
                "data": []
            }
    
    错误处理：
        - 400 Bad Request: 下载失败（网络问题、URL无效、文件不存在）
        - 500 Internal Server Error: 解析失败（非PDF文件、PDF损坏）或识别失败（OCR模型未加载、内存不足）
    
    使用示例：
        # curl 请求
        curl "http://localhost:8000/pdf/predict-by-url?pdf_url=https://example.com/doc.pdf"
        
        # Python requests
        import requests
        url = "http://localhost:8000/pdf/predict-by-url"
        params = {"pdf_url": "https://example.com/doc.pdf"}
        response = requests.get(url, params=params)
        data = response.json()
    
    注意事项：
        - URL 必须可公开访问（无需登录）
        - 建议 PDF 文件大小不超过 50MB
        - 超时时间为 30 秒
        - 表格检测基于文本坐标，复杂表格可能识别不准确
    """
    # 下载PDF文件
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        pdf_content = response.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法下载PDF: {str(e)}"
        )
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(pdf_content)
        tmp_pdf_path = tmp_file.name
    
    try:
        # 处理 PDF
        all_results, image_files = process_pdf(tmp_pdf_path, detection_model, recognition_model)
        
        # 计算总表格数
        total_tables = len(all_results)
        
        restfulModel = RestfulModel(
            resultcode=200,
            message=f"Success: 提取到 {total_tables} 个表格",
            data=all_results
        )
        return restfulModel
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF识别失败: {str(e)}"
        )
    
    finally:
        # 删除临时图片文件
        if 'image_files' in locals():
            for img_info in image_files:
                try:
                    os.unlink(img_info['path'])
                except Exception:
                    pass
        
        # 删除临时PDF文件
        try:
            os.unlink(tmp_pdf_path)
        except Exception:
            pass


@router.post('/predict-by-file', response_model=RestfulModel, summary="识别上传的PDF文件")
async def predict_pdf_by_file(
    file: UploadFile,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    """
    上传 PDF 文件并识别其中的表格数据
    
    API 端点：POST /pdf/predict-by-file
    
    Args:
        file (UploadFile): 通过表单上传的 PDF 文件
        detection_model (str, optional): 检测模型名称
        recognition_model (str, optional): 识别模型名称
    
    Returns:
        RestfulModel: 统一格式的 JSON 响应
            成功时 (200):
            {
                "resultcode": 200,
                "message": "Success: filename.pdf, 提取到 N 个表格",
                "data": [
                    {
                        "page": 1,
                        "table": {
                            "headers": ["列1", "列2", "列3"],
                            "rows": [["值1", "值2", "值3"], ...],
                            "total_rows": 10,
                            "total_cols": 3
                        }
                    },
                    ...
                ]
            }
            
            失败时 (400/500):
            {
                "resultcode": 400/500,
                "message": "错误详细信息",
                "data": []
            }
    
    错误处理：
        - 400 Bad Request: 文件不是 PDF 格式
        - 500 Internal Server Error: 
            * 保存失败（磁盘空间不足、权限问题）
            * 解析失败（非 PDF 文件、PDF 损坏）
            * 识别失败（OCR 模型未加载、内存不足）
    
    使用示例：
        # curl 请求
        curl -X POST "http://localhost:8000/pdf/predict-by-file" \\
             -F "file=@/path/to/document.pdf"
        
        # Python requests
        import requests
        url = "http://localhost:8000/pdf/predict-by-file"
        files = {"file": open("document.pdf", "rb")}
        response = requests.post(url, files=files)
        data = response.json()
        
        # HTML 表单
        <form action="/pdf/predict-by-file" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf">
            <button type="submit">上传识别</button>
        </form>
    
    注意事项：
        - 建议文件大小不超过 50MB
        - 上传超时时间为 60 秒
        - 临时文件会在处理完成后自动删除
        - 表格检测基于文本坐标，复杂表格可能识别不准确
        - 只返回包含表格的页面，纯文本页面会被过滤
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传PDF格式的文件"
        )
    
    # 读取文件内容
    file_bytes = await file.read()
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_pdf_path = tmp_file.name
    
    try:
        # 处理 PDF
        all_results, image_files = process_pdf(tmp_pdf_path, detection_model, recognition_model)
        
        # 计算总表格数
        total_tables = len(all_results)
        
        restfulModel = RestfulModel(
            resultcode=200,
            message=f"Success: {file.filename}, 提取到 {total_tables} 个表格",
            data=all_results
        )
        return restfulModel
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF识别失败: {str(e)}"
        )
    
    finally:
        # 删除临时图片文件
        if 'image_files' in locals():
            for img_info in image_files:
                try:
                    os.unlink(img_info['path'])
                except Exception:
                    pass
        
        # 删除临时PDF文件
        try:
            os.unlink(tmp_pdf_path)
        except Exception:
            pass


@router.post('/predict-by-base64', response_model=RestfulModel, summary="识别 Base64 PDF")
async def predict_pdf_by_base64(pdf_model: PDFBase64PostModel):
    """
    通过 Base64 编码识别 PDF 文件中的表格数据
    
    API 端点：POST /pdf/predict-by-base64
    
    工作流程：
    1. Base64 解码：将 Base64 字符串解码为 PDF 二进制数据
    2. 文件保存：将解码后的数据保存到临时文件
    3. PDF 转图：将 PDF 每一页转换为高分辨率图像（2x）
    4. OCR 识别：对每页图像执行文字识别（可选择模型）
    5. 表格重建：使用坐标算法识别表格结构
    6. 结果过滤：只返回包含表格的页面
    7. 资源清理：删除所有临时文件
    
    Args:
        pdf_model (PDFBase64PostModel): 包含 base64_str 的请求体
            - base64_str: PDF 文件的 Base64 编码字符串
            - detection_model (optional): 检测模型名称
            - recognition_model (optional): 识别模型名称
    
    Returns:
        RestfulModel: 统一格式的 JSON 响应
            成功时 (200):
            {
                "resultcode": 200,
                "message": "Success: 提取到 N 个表格",
                "data": [
                    {
                        "page": 1,
                        "table": {
                            "headers": ["列1", "列2", "列3"],
                            "rows": [["值1", "值2", "值3"], ...],
                            "total_rows": 10,
                            "total_cols": 3
                        }
                    },
                    ...
                ]
            }
            
            失败时 (400/500):
            {
                "resultcode": 400/500,
                "message": "错误详细信息",
                "data": []
            }
    
    错误处理：
        - 400 Bad Request: Base64 解码失败（格式错误、编码错误）
        - 500 Internal Server Error: 
            * PDF 解析失败（非 PDF 数据、文件损坏）
            * OCR 识别失败（模型未加载、内存不足）
    
    使用示例：
        # Python requests
        import requests
        import base64
        
        # 读取 PDF 文件并编码为 Base64
        with open("document.pdf", "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 发送请求
        url = "http://localhost:8000/pdf/predict-by-base64"
        data = {
            "base64_str": pdf_base64,
            "detection_model": "PP-OCRv4_mobile_det",  # 可选
            "recognition_model": "PP-OCRv4_mobile_rec"  # 可选
        }
        response = requests.post(url, json=data)
        result = response.json()
        
        # JavaScript fetch
        const pdfBase64 = btoa(pdfBinaryData);
        fetch('http://localhost:8000/pdf/predict-by-base64', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({base64_str: pdfBase64})
        });
    
    注意事项：
        - Base64 字符串可能很大（PDF 文件 1MB = Base64 约 1.37MB）
        - 建议 PDF 文件大小不超过 20MB
        - 支持标准 Base64 编码（带或不带 data URI scheme）
        - 表格检测基于文本坐标，复杂表格可能识别不准确
    """
    try:
        # 移除可能的 data URI scheme prefix
        base64_str = pdf_model.base64_str
        if ',' in base64_str and base64_str.startswith('data:'):
            base64_str = base64_str.split(',', 1)[1]
        
        # 解码 Base64
        pdf_content = base64.b64decode(base64_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Base64 解码失败: {str(e)}"
        )
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(pdf_content)
        tmp_pdf_path = tmp_file.name
    
    try:
        # 处理 PDF
        all_results, image_files = process_pdf(
            tmp_pdf_path, 
            pdf_model.detection_model, 
            pdf_model.recognition_model
        )
        
        # 计算总表格数
        total_tables = len(all_results)
        
        restfulModel = RestfulModel(
            resultcode=200,
            message=f"Success: 提取到 {total_tables} 个表格",
            data=all_results
        )
        return restfulModel
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF识别失败: {str(e)}"
        )
    
    finally:
        # 删除临时图片文件
        if 'image_files' in locals():
            for img_info in image_files:
                try:
                    os.unlink(img_info['path'])
                except Exception:
                    pass
        
        # 删除临时PDF文件
        try:
            os.unlink(tmp_pdf_path)
        except Exception:
            pass
