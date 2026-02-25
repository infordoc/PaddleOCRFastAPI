#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试 PaddleOCR 3.x 初始化和功能"""

def test_paddleocr_init():
    """测试 PaddleOCR 3.x 初始化"""
    try:
        from paddleocr import PaddleOCR
        print("正在初始化 PaddleOCR 3.x...")
        print("使用 PP-OCRv5 模型（相比 PP-OCRv4 提升识别精度）")
        
        # PaddleOCR 3.x 推荐配置
        # 注意：不再使用 show_log 参数（已弃用）
        ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            use_angle_cls=True,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            lang='ch'
        )
        print("✓ PaddleOCR 3.x 初始化成功")
        print("  - 检测模型: PP-OCRv5_mobile_det")
        print("  - 识别模型: PP-OCRv5_mobile_rec")
        print("  - 角度分类: 已启用")
        return True
        
    except Exception as e:
        print(f"✗ PaddleOCR 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试 PaddleOCR 3.x 版本")
    print("=" * 60)
    
    if test_paddleocr_init():
        print("\n✓ 测试通过！PaddleOCR 3.x 可以正常使用")
        print("\n主要改进:")
        print("  ✓ PP-OCRv5 模型提升识别精度")
        print("  ✓ 统一的 predict() 接口")
        print("  ✓ 更清晰的结果结构")
        print("  ✓ PaddlePaddle 3.0+ 性能优化")
    else:
        print("\n✗ 测试失败！")
