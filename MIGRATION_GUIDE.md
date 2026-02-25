# PaddleOCR 3.x Migration Guide

This guide helps users migrate from PaddleOCR 2.x to 3.x in the PaddleOCRFastAPI project.

## Overview

PaddleOCRFastAPI has been upgraded to PaddleOCR 3.x (v3.4.0) with PaddlePaddle 3.0+ (v3.2.0), bringing significant improvements in performance, accuracy, and ease of use.

## Why Upgrade to 3.x?

### Key Benefits

1. **Enhanced Model Pipelines**: PP-OCRv5 offers superior recognition accuracy for various text types, including handwriting
2. **Improved Performance**: PaddlePaddle 3.0 brings optimizations for both training and inference
3. **Simplified API**: Unified `predict()` interface makes integration easier
4. **Better Table Recognition**: PPStructureV3 provides more accurate table extraction from documents
5. **Modern Architecture**: Modular and plugin-based design reduces maintenance complexity

## API Changes

### Basic OCR Recognition

**PaddleOCR 2.x:**
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="en", show_log=False)
result = ocr.ocr("img.png", det=True, rec=True)
for res in result:
    for line in res:
        print(line)
```

**PaddleOCR 3.x:**
```python
from paddleocr import PaddleOCR

# show_log parameter removed - use new logging system
ocr = PaddleOCR(lang="en")

# Simplified predict method - no det/rec parameters
result = ocr.predict("img.png")

# Direct access to results with simpler structure
for res in result:
    res.print()  # Built-in print method
```

### Visualization

**PaddleOCR 2.x:**
```python
from PIL import Image
from paddleocr import draw_ocr

result = result[0]
image = Image.open(img_path).convert("RGB")
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path="simfang.ttf")
im_show = Image.fromarray(im_show)
im_show.save("result.jpg")
```

**PaddleOCR 3.x:**
```python
# Much simpler!
result = ocr.predict("img.png")
for res in result:
    res.save_to_img("result")  # Automatically saves visualization
```

### Model Configuration

**PaddleOCR 2.x:**
```python
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_onnx=True  # Deprecated in 3.x
)
```

**PaddleOCR 3.x:**
```python
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_angle_cls=True,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    lang='ch'
    # use_onnx replaced by high-performance inference features
)
```

### Table Structure Recognition

**PaddleOCR 2.x:**
```python
from paddleocr import PPStructure

# Old PPStructure interface
table_engine = PPStructure()
result = table_engine(img)
```

**PaddleOCR 3.x:**
```python
from paddleocr import PPStructureV3

# New PPStructureV3 with more options
table_engine = PPStructureV3(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    use_table_recognition=True,
    use_chart_recognition=False,
    use_formula_recognition=False,
    use_region_detection=False
)
result = table_engine.predict(img)
```

## API Endpoints (No Changes)

The REST API endpoints remain unchanged, so your client code doesn't need modifications:

- `GET /ocr/predict-by-path` - Recognize local image
- `POST /ocr/predict-by-base64` - Recognize base64 image
- `POST /ocr/predict-by-file` - Recognize uploaded file
- `GET /ocr/predict-by-url` - Recognize image from URL
- `GET /pdf/predict-by-url` - Extract tables from PDF URL
- `POST /pdf/predict-by-file` - Extract tables from uploaded PDF

## Result Format Changes

### OCR Results

**PaddleOCR 2.x Format:**
```python
# Nested list structure
[
    [
        [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # bbox
        ("text", 0.95)                              # text and confidence
    ],
    ...
]
```

**PaddleOCR 3.x Format:**
```python
# Object with attributes
result[0].rec_texts  # List of recognized texts
result[0].rec_boxes  # List of bounding boxes
result[0].rec_scores # List of confidence scores
result[0].input_path # Input file path
```

The API server automatically handles this conversion for backward compatibility.

## Known Limitations

Current PaddleOCR 3.0 limitations:

1. Incomplete native C++ deployment support
2. High-performance service deployment not yet on par with PaddleServing 2.x
3. On-device deployment supports only key models (broader support coming)

## Testing Your Migration

After upgrading, test the following:

1. **Basic OCR**: Test text recognition on sample images
2. **Multi-language**: Verify language-specific recognition
3. **PDF Tables**: Test table extraction from PDF documents
4. **API Endpoints**: Ensure all REST endpoints work correctly

### Test Commands

```bash
# Test basic initialization
python test_paddleocr.py

# Test table extraction
python test_ppstructure.py

# Test API endpoints
python test_api.py
```

## Troubleshooting

### Issue: Import Error

**Problem:**
```python
ImportError: cannot import name 'PPStructure' from 'paddleocr'
```

**Solution:**
```python
# Change this:
from paddleocr import PPStructure

# To this:
from paddleocr import PPStructureV3
```

### Issue: Deprecated Parameter Warning

**Problem:**
```
Warning: 'show_log' parameter is deprecated
```

**Solution:**
Remove the `show_log` parameter and configure logging using the new logging system (see PaddleOCR documentation).

### Issue: Model Not Found

**Problem:**
```
Error: Model PP-OCRv4 not found
```

**Solution:**
Update model names to use PP-OCRv5:
```python
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec"
)
```

## Additional Resources

- [PaddleOCR 3.x Official Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR 3.x Upgrade Notes](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/paddleocr_3x_upgrade_en.md)
- [PP-OCRv5 Model Documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/ppocr_introduction_en.md)
- [PPStructureV3 Documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/ppstructure_en.md)

## Support

If you encounter issues during migration:

1. Check this guide and the official PaddleOCR documentation
2. Review the test files in this repository for working examples
3. Open an issue on the [GitHub repository](https://github.com/infordoc/PaddleOCRFastAPI/issues)

## Version History

- **v3.x (Current)**: PaddleOCR 3.4.0 + PaddlePaddle 3.2.0
  - PP-OCRv5 models
  - PPStructureV3 table recognition
  - Simplified API
  - Performance optimizations

- **v2.7 (Legacy)**: PaddleOCR 2.7
  - PP-OCRv4 models
  - Original PPStructure
  - Legacy API

- **v2.5 (Legacy)**: PaddleOCR 2.5
  - PP-OCRv3 models
  - Basic functionality
