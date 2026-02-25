#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for new features:
1. Model selection in all endpoints
2. PDF base64 endpoint

Usage:
    python test_new_features.py
"""

import requests
import base64
import json

BASE_URL = "http://localhost:8000"

def test_ocr_with_model_selection():
    """
    Test OCR endpoint with custom model selection
    """
    print("\n" + "="*60)
    print("Test 1: OCR with Model Selection")
    print("="*60)
    
    # Test with PP-OCRv4 models
    url = f"{BASE_URL}/ocr/predict-by-file"
    params = {
        "detection_model": "PP-OCRv4_mobile_det",
        "recognition_model": "PP-OCRv4_mobile_rec"
    }
    
    print(f"\nEndpoint: POST {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    print("\nExpected: OCR will use PP-OCRv4 models instead of default PP-OCRv5")
    print("Status: Ready to test (requires image file)")


def test_pdf_base64():
    """
    Test PDF base64 endpoint
    """
    print("\n" + "="*60)
    print("Test 2: PDF Base64 Endpoint")
    print("="*60)
    
    url = f"{BASE_URL}/pdf/predict-by-base64"
    
    print(f"\nEndpoint: POST {url}")
    print("\nRequest Body Structure:")
    print(json.dumps({
        "base64_str": "JVBERi0xLjQKJeLjz9M...",  # PDF base64 string
        "detection_model": "PP-OCRv4_mobile_det",  # Optional
        "recognition_model": "PP-OCRv4_mobile_rec"  # Optional
    }, indent=2))
    
    print("\nExample Usage:")
    print("""
    import base64
    import requests
    
    # Read and encode PDF
    with open("document.pdf", "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Send request
    response = requests.post(
        "http://localhost:8000/pdf/predict-by-base64",
        json={
            "base64_str": pdf_base64,
            "detection_model": "PP-OCRv4_mobile_det",
            "recognition_model": "PP-OCRv4_mobile_rec"
        }
    )
    
    # Process result
    result = response.json()
    print(f"Extracted {len(result['data'])} tables")
    """)


def test_model_options():
    """
    Display available model options
    """
    print("\n" + "="*60)
    print("Available Models")
    print("="*60)
    
    print("\nDetection Models:")
    detection_models = [
        ("PP-OCRv5_mobile_det", "Default, lightweight, fast"),
        ("PP-OCRv5_server_det", "More accurate, slower"),
        ("PP-OCRv4_mobile_det", "V4 lightweight"),
        ("PP-OCRv4_server_det", "V4 server version")
    ]
    for model, desc in detection_models:
        print(f"  ✓ {model:25s} - {desc}")
    
    print("\nRecognition Models:")
    recognition_models = [
        ("PP-OCRv5_mobile_rec", "Default, lightweight, fast"),
        ("PP-OCRv5_server_rec", "More accurate, slower"),
        ("PP-OCRv4_mobile_rec", "V4 lightweight"),
        ("PP-OCRv4_server_rec", "V4 server version")
    ]
    for model, desc in recognition_models:
        print(f"  ✓ {model:25s} - {desc}")
    
    print("\nNote: If you were getting better results before,")
    print("try using PP-OCRv4 models:")
    print("  - detection_model=PP-OCRv4_mobile_det")
    print("  - recognition_model=PP-OCRv4_mobile_rec")


def test_all_endpoints():
    """
    Display all updated endpoints
    """
    print("\n" + "="*60)
    print("All Endpoints with Model Selection")
    print("="*60)
    
    endpoints = [
        ("OCR", [
            ("GET", "/ocr/predict-by-path", "?image_path=...&detection_model=...&recognition_model=..."),
            ("POST", "/ocr/predict-by-base64", '{"base64_str": "...", "detection_model": "...", "recognition_model": "..."}'),
            ("POST", "/ocr/predict-by-file", "?detection_model=...&recognition_model=... (with file upload)"),
            ("GET", "/ocr/predict-by-url", "?imageUrl=...&detection_model=...&recognition_model=...")
        ]),
        ("PDF", [
            ("GET", "/pdf/predict-by-url", "?pdf_url=...&detection_model=...&recognition_model=..."),
            ("POST", "/pdf/predict-by-file", "?detection_model=...&recognition_model=... (with file upload)"),
            ("POST", "/pdf/predict-by-base64", '{"base64_str": "...", "detection_model": "...", "recognition_model": "..."}')
        ])
    ]
    
    for category, items in endpoints:
        print(f"\n{category} Endpoints:")
        for method, endpoint, params in items:
            new_marker = " [NEW]" if "base64" in endpoint and category == "PDF" else ""
            print(f"  {method:6s} {endpoint:30s}{new_marker}")
            print(f"         {params}")


def main():
    print("\n" + "="*70)
    print("PaddleOCR FastAPI - New Features Test")
    print("="*70)
    print("\nFeatures Added:")
    print("  1. Model selection for all OCR and PDF endpoints")
    print("  2. New PDF base64 endpoint")
    print("  3. Support for PP-OCRv4 and PP-OCRv5 models")
    
    test_model_options()
    test_all_endpoints()
    test_ocr_with_model_selection()
    test_pdf_base64()
    
    print("\n" + "="*70)
    print("Tests Overview Complete")
    print("="*70)
    print("\nTo actually test:")
    print("  1. Start the server: uvicorn main:app --host 0.0.0.0")
    print("  2. Access Swagger UI: http://localhost:8000/docs")
    print("  3. Try the new endpoints with model parameters")
    print("\n")


if __name__ == "__main__":
    main()
