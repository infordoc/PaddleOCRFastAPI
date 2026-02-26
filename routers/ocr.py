# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, UploadFile, status, Query
from models.OCRModel import *
from models.RestfulModel import *
from paddleocr import PaddleOCR
from utils.ImageHelper import base64_to_ndarray, bytes_to_ndarray
import requests
import os
import tempfile
import numpy as np
from typing import Optional, Union
import fitz  # PyMuPDF - para processar PDF
import base64

OCR_LANGUAGE = os.environ.get("OCR_LANGUAGE", "ch")

router = APIRouter(prefix="/ocr", tags=["OCR"])

# Cache for OCR instances with different model configurations
_ocr_instances = {}

# VL model names
VL_MODELS = ["PaddleOCR-VL-1.5", "PaddleOCR-VL"]

def is_vl_model(model_name: Optional[str]) -> bool:
    """Check if the model name is a VL model"""
    return model_name in VL_MODELS if model_name else False

def get_ocr_instance(detection_model: Optional[str] = None, recognition_model: Optional[str] = None) -> Union['PaddleOCR', 'PaddleOCRVL']:
    """
    获取或创建 PaddleOCR 或 PaddleOCRVL 实例（支持模型选择）
    
    Args:
        detection_model: 检测模型名称 (默认: PP-OCRv5_server_det)
        recognition_model: 识别模型名称 (默认: PP-OCRv5_server_rec)
    
    可用模型:
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
        Union[PaddleOCR, PaddleOCRVL]: OCR 实例
        
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
        if cache_key in _ocr_instances:
            return _ocr_instances[cache_key]
        
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
        _ocr_instances[cache_key] = ocr_instance
        
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
        if cache_key in _ocr_instances:
            return _ocr_instances[cache_key]
        
        # 创建新实例
        ocr_instance = PaddleOCR(
            text_detection_model_name=detection_model,
            text_recognition_model_name=recognition_model,
            use_angle_cls=True,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            lang=OCR_LANGUAGE
        )
        
        # 缓存实例
        _ocr_instances[cache_key] = ocr_instance
        
        return ocr_instance


# 保持向后兼容性 - 默认实例
ocr = get_ocr_instance()
def _np_to_list(value):
    """仅把需要的 numpy 数组转换为 Python list，其它类型原样返回。"""
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def extract_ocr_data(result):
    """
    从 PaddleOCR 3.x 或 PaddleOCRVL predict 返回结构中提取所需字段
    
    PaddleOCR 3.x 返回格式说明：
    - 统一的 predict() 接口返回 OCRResult 对象列表
    - 每个结果包含 rec_texts, rec_boxes, rec_scores, input_path 等属性
    - 相比 2.x 的嵌套列表结构更清晰易用
    
    PaddleOCRVL 返回格式说明：
    - 返回包含识别内容的字典或对象
    - 可能包含 ocr_texts, layout_res, table_res_list 等字段
    - 需要适配以兼容现有的 rec_texts/rec_boxes 格式
    
    返回格式: [{ 'input_path': str, 'rec_texts': list[str], 'rec_boxes': list }]
    
    支持以下几种可能格式:
    1. {'res': {...}}  # 单个结果
    2. [{'res': {...}}, {'res': {...}}]  # 多页结果
    3. OCRResult 对象: 具备属性 input_path / rec_texts / rec_boxes
    4. 直接是 dict {...}
    5. PaddleOCRVL 结果: 包含 ocr_texts, layout_res 等字段
    """

    debug = os.environ.get("OCR_DEBUG", "0") == "1"

    def _extract_from_dict(d: dict):
        if not isinstance(d, dict):
            return None
        core = d.get('res', d)  # 如果包含 res 用 res，没有就直接用自身
        if not isinstance(core, dict):
            return None
        input_path = core.get('input_path', '')
        rec_texts = core.get('rec_texts')
        if rec_texts is None:
            rec_texts = []
        rec_boxes = core.get('rec_boxes')
        if rec_boxes is None:
            rec_boxes = []
        # 仅当 rec_texts 是 list/tuple 才保留，否则置空，避免出现 numpy 数组被错误当成文本
        rec_texts = list(rec_texts) if isinstance(rec_texts, (list, tuple)) else []
        rec_boxes = _np_to_list(rec_boxes)
        return {
            'input_path': input_path,
            'rec_texts': rec_texts,
            'rec_boxes': rec_boxes
        }
    
    def _extract_from_vl_result(vl_result):
        """Extract text and boxes from PaddleOCRVL result"""
        rec_texts = []
        rec_boxes = []
        
        # Try to extract from ocr_texts field
        ocr_texts = vl_result.get('ocr_texts', [])
        if ocr_texts and isinstance(ocr_texts, list):
            for item in ocr_texts:
                if isinstance(item, dict):
                    text = item.get('text', '')
                    bbox = item.get('bbox', [])
                    if text:
                        rec_texts.append(text)
                        rec_boxes.append(bbox)
        
        # If no ocr_texts, try layout_res
        if not rec_texts:
            layout_res = vl_result.get('layout_res', [])
            if layout_res and isinstance(layout_res, list):
                for block in layout_res:
                    if isinstance(block, dict):
                        text = block.get('text', '')
                        bbox = block.get('bbox', [])
                        if text:
                            rec_texts.append(text)
                            rec_boxes.append(bbox)
        
        # If still no texts, try to get from response field
        if not rec_texts:
            response = vl_result.get('response', '')
            if response and isinstance(response, str):
                # For simple text responses, create a single entry
                rec_texts = [response]
                rec_boxes = [[]]
        
        return {
            'input_path': vl_result.get('input_path', ''),
            'rec_texts': rec_texts,
            'rec_boxes': rec_boxes
        }

    extracted = []

    # 情况 A: result 是 list
    if isinstance(result, list):
        for item in result:
            data = None
            # dict 情况
            if isinstance(item, dict):
                # Check if it's a VL result
                if 'ocr_texts' in item or 'layout_res' in item or 'response' in item:
                    data = _extract_from_vl_result(item)
                else:
                    data = _extract_from_dict(item)
            else:  # 对象属性情况
                input_path = getattr(item, 'input_path', '')
                rec_texts = getattr(item, 'rec_texts', []) or []
                rec_boxes = getattr(item, 'rec_boxes', []) or []
                rec_boxes = _np_to_list(rec_boxes)
                if rec_texts or rec_boxes or input_path:
                    data = {
                        'input_path': input_path,
                        'rec_texts': list(rec_texts) if isinstance(rec_texts, (list, tuple)) else [],
                        'rec_boxes': rec_boxes
                    }
            if data:
                extracted.append(data)
        if extracted:
            return extracted

    # 情况 B: result 是 dict
    if isinstance(result, dict):
        # Check if it's a VL result
        if 'ocr_texts' in result or 'layout_res' in result or 'response' in result:
            data = _extract_from_vl_result(result)
        else:
            data = _extract_from_dict(result)
        if data:
            return [data]

    # 其它未知情况: 返回空结构，便于前端处理
    if debug:
        print(f"[extract_ocr_data] 未识别的结果类型: {type(result)}")
    return [{'input_path': '', 'rec_texts': [], 'rec_boxes': []}]


@router.get('/predict-by-path', response_model=RestfulModel, summary="识别本地图片")
def predict_by_path(
    image_path: str,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    ocr_instance = get_ocr_instance(detection_model, recognition_model)
    result = ocr_instance.predict(input=image_path)
    # 提取关键数据：input_path, rec_texts, rec_boxes
    result_data = extract_ocr_data(result)
    restfulModel = RestfulModel(
        resultcode=200, message="Success", data=result_data, cls=OCRModel)
    return restfulModel


@router.post('/predict-by-base64', response_model=RestfulModel, summary="识别 Base64 数据")
def predict_by_base64(base64model: Base64PostModel):
    img = base64_to_ndarray(base64model.base64_str)
    
    # 保存为临时文件，因为predict方法需要文件路径
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        import cv2
        cv2.imwrite(tmp_file.name, img)
        tmp_file_path = tmp_file.name
    
    try:
        ocr_instance = get_ocr_instance(base64model.detection_model, base64model.recognition_model)
        result = ocr_instance.predict(input=tmp_file_path)
    finally:
        # 删除临时文件
        try:
            os.unlink(tmp_file_path)
        except Exception:
            pass
    
    # 提取关键数据：input_path, rec_texts, rec_boxes
    result_data = extract_ocr_data(result)
    restfulModel = RestfulModel(
        resultcode=200, message="Success", data=result_data, cls=OCRModel)
    return restfulModel


@router.post('/predict-by-file', response_model=RestfulModel, summary="识别上传文件")
async def predict_by_file(
    file: UploadFile,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    restfulModel: RestfulModel = RestfulModel()
    if file.filename.endswith((".jpg", ".png", ".jpeg", ".bmp", ".tiff")):  # 支持更多图片格式
        restfulModel.resultcode = 200
        restfulModel.message = file.filename
        file_data = file.file
        file_bytes = file_data.read()
        
        # 保存为临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            tmp_file_path = tmp_file.name
        
        try:
            ocr_instance = get_ocr_instance(detection_model, recognition_model)
            result = ocr_instance.predict(input=tmp_file_path)
        finally:
            # 删除临时文件
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass
        
        # 提取关键数据：input_path, rec_texts, rec_boxes
        result_data = extract_ocr_data(result)
        restfulModel.data = result_data
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传支持的图片格式 (.jpg, .png, .jpeg, .bmp, .tiff)"
        )
    return restfulModel


@router.get('/predict-by-url', response_model=RestfulModel, summary="识别图片 URL")
async def predict_by_url(
    imageUrl: str,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    # 直接使用URL进行predict
    ocr_instance = get_ocr_instance(detection_model, recognition_model)
    result = ocr_instance.predict(input=imageUrl)
    # 提取关键数据：input_path, rec_texts, rec_boxes
    result_data = extract_ocr_data(result)
    restfulModel = RestfulModel(
        resultcode=200, message="Success", data=result_data)
    return restfulModel


def pdf_to_images(pdf_path: str):
    """
    将 PDF 文档的每一页转换为图像，用于 OCR 处理
    
    Args:
        pdf_path: PDF 文件路径
    
    Returns:
        list: 包含每页图像信息的列表 [{'page_num': int, 'path': str}, ...]
    """
    temp_files = []
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        mat = fitz.Matrix(2.0, 2.0)  # 2倍放大提高识别率
        pix = page.get_pixmap(matrix=mat)
        
        # 保存为临时图像文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
            pix.save(tmp_img.name)
            temp_files.append({
                'page_num': page_num + 1,
                'path': tmp_img.name
            })
    
    pdf_document.close()
    return temp_files


@router.post('/pdf-predict-by-file', response_model=RestfulModel, summary="识别上传的PDF文件（全文OCR）")
async def pdf_predict_by_file(
    file: UploadFile,
    detection_model: Optional[str] = Query(None, description="检测模型 (PP-OCRv5_server_det, PP-OCRv5_mobile_det, PP-OCRv4_server_det, PP-OCRv4_mobile_det, PaddleOCR-VL-1.5, PaddleOCR-VL)"),
    recognition_model: Optional[str] = Query(None, description="识别模型 (PP-OCRv5_server_rec, PP-OCRv5_mobile_rec, PP-OCRv4_server_rec, PP-OCRv4_mobile_rec, PaddleOCR-VL-1.5, PaddleOCR-VL)")
):
    """
    上传 PDF 文件并对每一页进行 OCR 文本识别
    
    与 /pdf/predict-by-file 的区别：
    - 本接口返回完整的 OCR 文本识别结果
    - /pdf/predict-by-file 仅提取表格数据
    
    Args:
        file: PDF 文件
        detection_model: 检测模型（可选）
        recognition_model: 识别模型（可选）
    
    Returns:
        RestfulModel: 包含每页 OCR 识别结果的响应
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传PDF格式的文件"
        )
    
    # 读取文件内容
    file_bytes = await file.read()
    
    # 保存为临时PDF文件
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf.write(file_bytes)
        tmp_pdf_path = tmp_pdf.name
    
    try:
        # 将 PDF 转换为图像
        image_files = pdf_to_images(tmp_pdf_path)
        
        # 获取 OCR 实例
        ocr_instance = get_ocr_instance(detection_model, recognition_model)
        
        # 对每页进行 OCR 识别
        all_results = []
        for img_info in image_files:
            try:
                result = ocr_instance.predict(input=img_info['path'])
                page_data = extract_ocr_data(result)
                
                # 添加页码信息
                if page_data and len(page_data) > 0:
                    page_data[0]['page'] = img_info['page_num']
                    all_results.extend(page_data)
            except Exception as e:
                # 即使某页失败，也继续处理其他页
                all_results.append({
                    'page': img_info['page_num'],
                    'error': str(e),
                    'rec_texts': [],
                    'rec_boxes': []
                })
        
        restfulModel = RestfulModel(
            resultcode=200,
            message=f"Success: {file.filename}, 处理了 {len(image_files)} 页",
            data=all_results
        )
        return restfulModel
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF识别失败: {str(e)}"
        )
    
    finally:
        # 删除临时文件
        if 'image_files' in locals():
            for img_info in image_files:
                try:
                    os.unlink(img_info['path'])
                except Exception:
                    pass
        
        try:
            os.unlink(tmp_pdf_path)
        except Exception:
            pass


@router.post('/pdf-predict-by-base64', response_model=RestfulModel, summary="识别 Base64 PDF（全文OCR）")
async def pdf_predict_by_base64(
    pdf_model: PDFBase64PostModel
):
    """
    通过 Base64 编码识别 PDF 文件的全部文本
    
    与 /pdf/predict-by-base64 的区别：
    - 本接口返回完整的 OCR 文本识别结果
    - /pdf/predict-by-base64 仅提取表格数据
    
    Args:
        pdf_model: 包含 base64_str 和可选模型参数的请求体
    
    Returns:
        RestfulModel: 包含每页 OCR 识别结果的响应
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
    
    # 保存为临时PDF文件
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf.write(pdf_content)
        tmp_pdf_path = tmp_pdf.name
    
    try:
        # 将 PDF 转换为图像
        image_files = pdf_to_images(tmp_pdf_path)
        
        # 获取 OCR 实例
        ocr_instance = get_ocr_instance(pdf_model.detection_model, pdf_model.recognition_model)
        
        # 对每页进行 OCR 识别
        all_results = []
        for img_info in image_files:
            try:
                result = ocr_instance.predict(input=img_info['path'])
                page_data = extract_ocr_data(result)
                
                # 添加页码信息
                if page_data and len(page_data) > 0:
                    page_data[0]['page'] = img_info['page_num']
                    all_results.extend(page_data)
            except Exception as e:
                # 即使某页失败，也继续处理其他页
                all_results.append({
                    'page': img_info['page_num'],
                    'error': str(e),
                    'rec_texts': [],
                    'rec_boxes': []
                })
        
        restfulModel = RestfulModel(
            resultcode=200,
            message=f"Success: 处理了 {len(image_files)} 页",
            data=all_results
        )
        return restfulModel
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF识别失败: {str(e)}"
        )
    
    finally:
        # 删除临时文件
        if 'image_files' in locals():
            for img_info in image_files:
                try:
                    os.unlink(img_info['path'])
                except Exception:
                    pass
        
        try:
            os.unlink(tmp_pdf_path)
        except Exception:
            pass
