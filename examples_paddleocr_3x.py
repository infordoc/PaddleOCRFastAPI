#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PaddleOCR 3.x Usage Examples

This file demonstrates the simplified API and new features in PaddleOCR 3.x.
"""

import os
from paddleocr import PaddleOCR


def example_basic_ocr():
    """
    Example 1: Basic OCR with simplified API
    
    PaddleOCR 3.x provides a cleaner interface for text recognition.
    """
    print("\n" + "="*60)
    print("Example 1: Basic OCR Recognition")
    print("="*60)
    
    # Initialize with PP-OCRv5 models (default in 3.x)
    ocr = PaddleOCR(lang='en')
    
    # Simple prediction - no need to specify det/rec parameters
    # The predict() method is the unified interface in 3.x
    test_image = 'test_image.jpg'  # Replace with your image path
    
    if not os.path.exists(test_image):
        print(f"⚠ Test image not found: {test_image}")
        print("Please provide a test image to run this example.\n")
        return
    
    result = ocr.predict(test_image)
    
    # New in 3.x: Direct access to results with clearer structure
    for page_result in result:
        print(f"\n📄 Image: {page_result.input_path}")
        print(f"📝 Detected {len(page_result.rec_texts)} text regions\n")
        
        # New in 3.x: Built-in print method
        page_result.print()
        
        # Or access individual components
        for text, box, score in zip(
            page_result.rec_texts,
            page_result.rec_boxes,
            page_result.rec_scores
        ):
            print(f"  Text: {text:30s} | Confidence: {score:.2f}")


def example_with_visualization():
    """
    Example 2: OCR with visualization
    
    PaddleOCR 3.x simplifies result visualization.
    """
    print("\n" + "="*60)
    print("Example 2: OCR with Visualization")
    print("="*60)
    
    ocr = PaddleOCR(lang='ch')  # Chinese language support
    
    test_image = 'test_image.jpg'
    
    if not os.path.exists(test_image):
        print(f"⚠ Test image not found: {test_image}")
        print("Please provide a test image to run this example.\n")
        return
    
    result = ocr.predict(test_image)
    
    # New in 3.x: One-line visualization save
    for page_result in result:
        output_path = 'result_visualization'
        page_result.save_to_img(output_path)
        print(f"✓ Visualization saved to: {output_path}_*.jpg")


def example_custom_models():
    """
    Example 3: Using custom model configurations
    
    PaddleOCR 3.x uses clearer model naming.
    """
    print("\n" + "="*60)
    print("Example 3: Custom Model Configuration")
    print("="*60)
    
    # PP-OCRv5 models offer better accuracy than v4
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",     # Text detection
        text_recognition_model_name="PP-OCRv5_mobile_rec",   # Text recognition
        use_angle_cls=True,                                   # Enable angle classification
        use_doc_orientation_classify=False,                   # Disable for speed
        use_doc_unwarping=False,                             # Disable for speed
        lang='ch'
    )
    
    print("✓ OCR initialized with PP-OCRv5 models")
    print("  - Detection: PP-OCRv5_mobile_det")
    print("  - Recognition: PP-OCRv5_mobile_rec")
    print("  - Angle classification: Enabled")


def example_result_access():
    """
    Example 4: Accessing OCR results
    
    Demonstrates the new result structure in 3.x.
    """
    print("\n" + "="*60)
    print("Example 4: Result Structure")
    print("="*60)
    
    ocr = PaddleOCR(lang='en')
    
    test_image = 'test_image.jpg'
    
    if not os.path.exists(test_image):
        print(f"⚠ Test image not found: {test_image}")
        print("Please provide a test image to run this example.\n")
        return
    
    result = ocr.predict(test_image)
    
    # Access result attributes (new in 3.x)
    page = result[0]
    
    print(f"\n📊 Result Structure:")
    print(f"  - input_path: {page.input_path}")
    print(f"  - rec_texts: List of {len(page.rec_texts)} recognized texts")
    print(f"  - rec_boxes: List of {len(page.rec_boxes)} bounding boxes")
    print(f"  - rec_scores: List of {len(page.rec_scores)} confidence scores")
    
    # Example: Extract text with confidence > 0.9
    high_confidence_texts = [
        text for text, score in zip(page.rec_texts, page.rec_scores)
        if score > 0.9
    ]
    
    print(f"\n✓ Found {len(high_confidence_texts)} high-confidence texts (>0.9)")


def example_multiple_languages():
    """
    Example 5: Multi-language support
    
    PaddleOCR 3.x supports 80+ languages.
    """
    print("\n" + "="*60)
    print("Example 5: Multi-language Support")
    print("="*60)
    
    # Supported languages include: ch, en, fr, german, korean, japan, etc.
    languages = {
        'ch': 'Chinese',
        'en': 'English',
        'fr': 'French',
        'german': 'German',
        'korean': 'Korean',
        'japan': 'Japanese'
    }
    
    print("\nSupported languages (examples):")
    for code, name in languages.items():
        print(f"  - {code:10s}: {name}")
    
    print("\nTo use a specific language:")
    print("  ocr = PaddleOCR(lang='french')")
    
    # See full list: https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md


def main():
    """
    Run all examples
    """
    print("\n" + "="*70)
    print("PaddleOCR 3.x Usage Examples")
    print("="*70)
    print("\nThese examples demonstrate the simplified API in PaddleOCR 3.x.")
    print("Key improvements over 2.x:")
    print("  ✓ Unified predict() interface (replaces ocr() with parameters)")
    print("  ✓ Clearer result structure with direct attribute access")
    print("  ✓ Built-in print() and save_to_img() methods")
    print("  ✓ PP-OCRv5 models for better accuracy")
    print("  ✓ Simplified configuration with descriptive parameter names")
    
    try:
        # Run examples
        example_basic_ocr()
        example_with_visualization()
        example_custom_models()
        example_result_access()
        example_multiple_languages()
        
        print("\n" + "="*70)
        print("✓ All examples completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
