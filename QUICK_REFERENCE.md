# PaddleOCR 3.x Quick Reference

## Quick Start

### Installation
```bash
pip install paddleocr>=3.0.0 paddlepaddle>=3.0.0
```

### Basic Usage
```python
from paddleocr import PaddleOCR

# Initialize (PP-OCRv5 by default)
ocr = PaddleOCR(lang='en')

# Recognize text
result = ocr.predict('image.jpg')

# Print results
for res in result:
    res.print()
```

---

## API Comparison: 2.x vs 3.x

### Initialization

| 2.x | 3.x |
|-----|-----|
| `PaddleOCR(show_log=False)` | `PaddleOCR()` (use logging system) |
| `PaddleOCR(use_onnx=True)` | Use high-performance inference |
| `PaddleOCR()` (PP-OCRv4) | `PaddleOCR()` (PP-OCRv5 default) |

### Recognition

| 2.x | 3.x |
|-----|-----|
| `ocr.ocr('img.jpg', det=True, rec=True)` | `ocr.predict('img.jpg')` |
| `ocr.ocr('img.jpg', cls=False)` | Configure in initialization |

### Results

| 2.x | 3.x |
|-----|-----|
| `[[[bbox], (text, score)]]` | `result[0].rec_texts` |
| Manual extraction | `result[0].rec_boxes` |
| Custom visualization | `result[0].save_to_img()` |

---

## Common Tasks

### 1. Basic Text Recognition
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='en')
result = ocr.predict('document.jpg')

# Access results
page = result[0]
for text, score in zip(page.rec_texts, page.rec_scores):
    print(f"{text}: {score:.2f}")
```

### 2. Multi-Language Recognition
```python
# Chinese
ocr_ch = PaddleOCR(lang='ch')

# French
ocr_fr = PaddleOCR(lang='french')

# German
ocr_de = PaddleOCR(lang='german')

# Japanese
ocr_ja = PaddleOCR(lang='japan')
```

### 3. Custom Model Configuration
```python
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_angle_cls=True,                    # Enable text rotation
    use_doc_orientation_classify=False,    # Disable for speed
    use_doc_unwarping=False,              # Disable for speed
    lang='en'
)
```

### 4. High Confidence Filtering
```python
result = ocr.predict('image.jpg')
page = result[0]

high_conf = [
    text for text, score in zip(page.rec_texts, page.rec_scores)
    if score > 0.9
]
```

### 5. Table Recognition
```python
from paddleocr import PPStructureV3

engine = PPStructureV3(
    use_table_recognition=True,
    use_chart_recognition=False,
    use_formula_recognition=False
)

result = engine.predict(image)
```

---

## REST API Endpoints

### Image Recognition

#### Recognize Local Image
```bash
GET /ocr/predict-by-path?image_path=/path/to/image.jpg
```

#### Recognize Base64 Image
```bash
POST /ocr/predict-by-base64
Content-Type: application/json

{
  "base64_str": "data:image/png;base64,..."
}
```

#### Recognize Uploaded File
```bash
POST /ocr/predict-by-file
Content-Type: multipart/form-data

file: <image_file>
```

#### Recognize Image URL
```bash
GET /ocr/predict-by-url?imageUrl=https://example.com/image.jpg
```

### PDF Table Extraction

#### Extract from PDF URL
```bash
GET /pdf/predict-by-url?pdf_url=https://example.com/doc.pdf
```

#### Extract from Uploaded PDF
```bash
POST /pdf/predict-by-file
Content-Type: multipart/form-data

file: <pdf_file>
```

---

## Response Format

### OCR Recognition Response
```json
{
  "resultcode": 200,
  "message": "Success",
  "data": [
    {
      "input_path": "image.jpg",
      "rec_texts": ["Hello", "World"],
      "rec_boxes": [
        [10, 20, 100, 50],
        [10, 60, 100, 90]
      ]
    }
  ]
}
```

### PDF Table Response
```json
{
  "resultcode": 200,
  "message": "Success: 提取到 2 个表格",
  "data": [
    {
      "page": 1,
      "table": {
        "headers": ["Name", "Age", "City"],
        "rows": [
          ["John", "25", "NYC"],
          ["Mary", "30", "LA"]
        ]
      }
    }
  ]
}
```

---

## Configuration Options

### Language Codes
| Code | Language | Code | Language |
|------|----------|------|----------|
| `ch` | Chinese | `en` | English |
| `french` | French | `german` | German |
| `korean` | Korean | `japan` | Japanese |
| `arabic` | Arabic | `russian` | Russian |
| `spanish` | Spanish | `portuguese` | Portuguese |

[Full list](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md)

### Model Options
- **Detection**: `PP-OCRv5_mobile_det`, `PP-OCRv5_server_det`
- **Recognition**: `PP-OCRv5_mobile_rec`, `PP-OCRv5_server_rec`
- **Angle Classification**: `use_angle_cls=True/False`

### Performance Tuning
```python
# Faster (lower accuracy)
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_angle_cls=False,
    use_doc_orientation_classify=False
)

# Slower (higher accuracy)
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    use_angle_cls=True
)
```

---

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'paddleocr'
```
**Solution**: `pip install paddleocr>=3.0.0`

### Deprecated Parameter Warning
```
Warning: 'show_log' parameter is deprecated
```
**Solution**: Remove `show_log` parameter, configure logging separately

### PPStructure Import Error
```
ImportError: cannot import name 'PPStructure'
```
**Solution**: Use `from paddleocr import PPStructureV3` instead

### Model Not Found
```
Error: Model PP-OCRv4 not found
```
**Solution**: Update to PP-OCRv5 model names

---

## Environment Variables

### OCR Language
```bash
export OCR_LANGUAGE=ch  # Chinese (default)
export OCR_LANGUAGE=en  # English
```

### Debug Mode
```bash
export OCR_DEBUG=1  # Enable debug output
```

---

## Docker Usage

### Build Image
```bash
docker build -t paddleocrapi:latest .
```

### Run Container
```bash
docker run -d -p 8000:8000 \
  -e OCR_LANGUAGE=en \
  paddleocrapi:latest
```

### Docker Compose
```yaml
services:
  paddleocrapi:
    image: paddleocrapi:latest
    ports:
      - "8000:8000"
    environment:
      - OCR_LANGUAGE=ch
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

---

## Testing

### Run Compatibility Tests
```bash
python test_compatibility.py
```

### Test Basic OCR
```bash
python test_paddleocr.py
```

### Test Table Extraction
```bash
python test_ppstructure.py
```

### Test API
```bash
# Start server
uvicorn main:app --host 0.0.0.0

# Run tests
python test_api.py
```

---

## Performance Tips

1. **Use Mobile Models**: Faster inference, smaller memory
2. **Disable Unused Features**: Turn off angle classification if not needed
3. **Batch Processing**: Process multiple images together
4. **GPU Acceleration**: Enable GPU for faster processing
5. **Model Caching**: Reuse model instances

---

## Resources

- **Documentation**: [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
- **Examples**: `examples_paddleocr_3x.py`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **Changelog**: `CHANGELOG.md`
- **API Docs**: `http://localhost:8000/docs`

---

## Version Info

- **PaddleOCR**: 3.4.0+
- **PaddlePaddle**: 3.2.0+
- **Python**: 3.9+
- **FastAPI**: 0.115+

---

*Last Updated: 2024*
