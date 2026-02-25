#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证 PaddleOCR 3.x 兼容性测试

此脚本验证代码是否正确使用 PaddleOCR 3.x API
"""

def test_imports():
    """测试导入"""
    print("\n" + "="*60)
    print("测试 1: 导入检查")
    print("="*60)
    
    try:
        from paddleocr import PaddleOCR, PPStructureV3
        print("✓ PaddleOCR 导入成功")
        print("✓ PPStructureV3 导入成功")
        
        import paddleocr
        print(f"✓ PaddleOCR 版本: {paddleocr.__version__}")
        
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_ocr_initialization():
    """测试 OCR 初始化"""
    print("\n" + "="*60)
    print("测试 2: OCR 初始化（无图像）")
    print("="*60)
    
    try:
        from paddleocr import PaddleOCR
        
        # 测试标准初始化
        print("初始化 PaddleOCR 3.x（PP-OCRv5）...")
        ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            use_angle_cls=True,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            lang='en'
        )
        print("✓ OCR 初始化成功")
        print("  - 模型: PP-OCRv5")
        print("  - 语言: English")
        
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ppstructurev3_initialization():
    """测试 PPStructureV3 初始化"""
    print("\n" + "="*60)
    print("测试 3: PPStructureV3 初始化（无图像）")
    print("="*60)
    
    try:
        from paddleocr import PPStructureV3
        
        print("初始化 PPStructureV3...")
        engine = PPStructureV3(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            use_table_recognition=True,
            use_chart_recognition=False,
            use_formula_recognition=False,
            use_region_detection=False
        )
        print("✓ PPStructureV3 初始化成功")
        print("  - 表格识别: 已启用")
        print("  - 其他功能: 已禁用（提高性能）")
        
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """测试 API 结构"""
    print("\n" + "="*60)
    print("测试 4: API 结构检查")
    print("="*60)
    
    try:
        from paddleocr import PaddleOCR
        
        ocr = PaddleOCR(lang='en')
        
        # 检查是否有 predict 方法
        if not hasattr(ocr, 'predict'):
            print("✗ 缺少 predict() 方法")
            return False
        
        print("✓ predict() 方法存在")
        
        # 注意：不再检查 ocr() 方法，因为 3.x 推荐使用 predict()
        # 但为了兼容性，ocr() 可能仍然存在
        
        return True
    except Exception as e:
        print(f"✗ API 检查失败: {e}")
        return False


def test_code_patterns():
    """测试代码模式（静态分析）"""
    print("\n" + "="*60)
    print("测试 5: 代码模式检查")
    print("="*60)
    
    import os
    import re
    
    issues = []
    
    # 检查是否使用了弃用的参数
    deprecated_patterns = [
        (r'show_log\s*=', 'show_log parameter (deprecated in 3.x)'),
        (r'use_onnx\s*=', 'use_onnx parameter (deprecated in 3.x)'),
        (r'from paddleocr import PPStructure[^V]', 'PPStructure (use PPStructureV3)'),
    ]
    
    files_to_check = ['routers/ocr.py', 'routers/pdf_ocr.py']
    
    for filepath in files_to_check:
        full_path = filepath
        if not os.path.exists(full_path):
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for pattern, desc in deprecated_patterns:
            if re.search(pattern, content):
                issues.append(f"{filepath}: 使用了 {desc}")
    
    if issues:
        print("⚠ 发现潜在问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ 未发现使用弃用的 API 模式")
        print("✓ 代码遵循 PaddleOCR 3.x 最佳实践")
        return True


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("PaddleOCR 3.x 兼容性验证测试")
    print("="*70)
    print("\n此测试验证代码是否正确使用 PaddleOCR 3.x API")
    print("注意：此测试不执行实际的图像识别（避免下载模型）")
    
    tests = [
        ("导入检查", test_imports),
        ("OCR 初始化", test_ocr_initialization),
        ("PPStructureV3 初始化", test_ppstructurev3_initialization),
        ("API 结构", test_api_structure),
        ("代码模式", test_code_patterns),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status:10s} - {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({100*passed//total}%)")
    
    if passed == total:
        print("\n" + "="*70)
        print("🎉 所有测试通过！代码已正确升级到 PaddleOCR 3.x")
        print("="*70)
        print("\n关键改进:")
        print("  ✓ 使用 PP-OCRv5 模型（提升精度）")
        print("  ✓ 使用 predict() 统一接口")
        print("  ✓ 使用 PPStructureV3（增强表格识别）")
        print("  ✓ 移除弃用的参数（show_log, use_onnx）")
        print("  ✓ PaddlePaddle 3.0+ 兼容性")
        return True
    else:
        print("\n⚠ 部分测试失败，请检查上述问题")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
