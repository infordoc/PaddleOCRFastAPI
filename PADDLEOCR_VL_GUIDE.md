# PaddleOCR-VL Integration Guide

## Overview

This document describes the integration of PaddleOCR-VL (Vision-Language) models into the PaddleOCRFastAPI endpoints. The integration adds optional support for advanced multimodal OCR capabilities while maintaining full backward compatibility with existing PP-OCR models.

## What are PaddleOCR-VL Models?

PaddleOCR-VL models are multimodal vision-language models that combine visual understanding with natural language processing to provide advanced document analysis capabilities.

### Available VL Models

#### PaddleOCR-VL-1.5 (Recommended)
- **Latest multimodal vision-language model**
- **Supports 111 languages** for text recognition
- **Advanced capabilities:**
  - Automatic layout detection and analysis
  - Complex table recognition (including merged cells)
  - Mathematical formula recognition
  - Chart and diagram recognition
  - Seal and stamp recognition
  - Document orientation and dewarping
- **Structured output** with detailed metadata

#### PaddleOCR-VL (v1)
- **First-generation multimodal model**
- **Core capabilities:**
  - Multi-language text recognition
  - Layout analysis
  - Basic table recognition
  - Structured recognition

### Comparison: Traditional vs VL Models

| Feature | PP-OCR (v4/v5) | PaddleOCR-VL |
|---------|----------------|--------------|
| **Speed** | Fast | Moderate |
| **Resource Usage** | Low | Higher |
| **Languages** | Single/limited | 111 languages |
| **Tables** | Coordinate-based | Structure-aware |
| **Formulas** | Text only | LaTeX output |
| **Seals/Stamps** | No | Yes |
| **Charts** | No | Yes |
| **Layout Analysis** | No | Yes |
| **Best For** | Simple text extraction | Complex documents |

## Usage

### Using VL Models in API Endpoints

All existing OCR and PDF endpoints support VL models through the optional `detection_model` and/or `recognition_model` parameters.

#### Available Endpoints

**OCR Endpoints:**
- `GET /ocr/predict-by-path` - Recognize local image
- `POST /ocr/predict-by-file` - Recognize uploaded file
- `POST /ocr/predict-by-base64` - Recognize Base64 image
- `GET /ocr/predict-by-url` - Recognize image from URL
- `POST /ocr/pdf-predict-by-file` - Recognize uploaded PDF (full OCR)
- `POST /ocr/pdf-predict-by-base64` - Recognize Base64 PDF (full OCR)

**PDF Endpoints:**
- `GET /pdf/predict-by-url` - Extract tables from PDF URL
- `POST /pdf/predict-by-file` - Extract tables from uploaded PDF
- `POST /pdf/predict-by-base64` - Extract tables from Base64 PDF

### Parameter Values

#### detection_model (Optional)
- `PP-OCRv5_server_det` (default) - PP-OCRv5 server detection model
- `PP-OCRv5_mobile_det` - PP-OCRv5 mobile detection model
- `PP-OCRv4_server_det` - PP-OCRv4 server detection model
- `PP-OCRv4_mobile_det` - PP-OCRv4 mobile detection model
- **`PaddleOCR-VL-1.5`** - VL v1.5 model (multimodal)
- **`PaddleOCR-VL`** - VL v1 model (multimodal)

#### recognition_model (Optional)
- `PP-OCRv5_server_rec` (default) - PP-OCRv5 server recognition model
- `PP-OCRv5_mobile_rec` - PP-OCRv5 mobile recognition model
- `PP-OCRv4_server_rec` - PP-OCRv4 server recognition model
- `PP-OCRv4_mobile_rec` - PP-OCRv4 mobile recognition model
- **`PaddleOCR-VL-1.5`** - VL v1.5 model (multimodal)
- **`PaddleOCR-VL`** - VL v1 model (multimodal)

**Note:** Specifying either `detection_model` or `recognition_model` as a VL model will activate the VL engine.

## Examples

### Example 1: Using VL Model for Image Recognition

#### cURL
```bash
# Using VL-1.5 model
curl "http://localhost:8000/ocr/predict-by-path?image_path=/path/to/image.jpg&detection_model=PaddleOCR-VL-1.5"
```

#### Python
```python
import requests

# Using VL-1.5 model
response = requests.get(
    "http://localhost:8000/ocr/predict-by-path",
    params={
        "image_path": "/path/to/image.jpg",
        "detection_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()

# Process results
for item in result['data']:
    print("Recognized texts:", item['rec_texts'])
    print("Bounding boxes:", item['rec_boxes'])
```

### Example 2: Upload File with VL Model

#### cURL
```bash
curl -X POST "http://localhost:8000/ocr/predict-by-file?detection_model=PaddleOCR-VL" \
     -F "file=@complex_document.jpg"
```

#### Python
```python
import requests

files = {"file": open("complex_document.jpg", "rb")}
params = {"detection_model": "PaddleOCR-VL"}

response = requests.post(
    "http://localhost:8000/ocr/predict-by-file",
    params=params,
    files=files
)
result = response.json()
```

### Example 3: Base64 Recognition with VL Model

```python
import requests
import base64

# Read and encode image
with open("document.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

# Send request with VL model
response = requests.post(
    "http://localhost:8000/ocr/predict-by-base64",
    json={
        "base64_str": img_base64,
        "detection_model": "PaddleOCR-VL-1.5",
        "recognition_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
```

### Example 4: PDF Processing with VL Model

```python
import requests
import base64

# Read and encode PDF
with open("complex_document.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

# Process PDF with VL model for better table recognition
response = requests.post(
    "http://localhost:8000/pdf/predict-by-base64",
    json={
        "base64_str": pdf_base64,
        "detection_model": "PaddleOCR-VL-1.5"
    }
)

result = response.json()

# Extract tables
for page in result['data']:
    print(f"Page {page['page']}:")
    table = page['table']
    print(f"Headers: {table['headers']}")
    print(f"Rows: {table['rows']}")
```

## Response Format

The response format remains consistent across all models, ensuring backward compatibility:

```json
{
    "resultcode": 200,
    "message": "Success",
    "data": [
        {
            "input_path": "path/to/image.jpg",
            "rec_texts": [
                "Text line 1",
                "Text line 2",
                "..."
            ],
            "rec_boxes": [
                [x1, y1, x2, y2],
                [x1, y1, x2, y2],
                "..."
            ]
        }
    ]
}
```

For PDF endpoints with table extraction:

```json
{
    "resultcode": 200,
    "message": "Success: 提取到 N 个表格",
    "data": [
        {
            "page": 1,
            "table": {
                "headers": ["Column1", "Column2", "..."],
                "rows": [
                    ["Value1", "Value2", "..."],
                    "..."
                ]
            }
        }
    ]
}
```

## Implementation Details

### Architecture

1. **Model Detection**: Helper function `is_vl_model()` checks if the specified model is a VL model
2. **Instance Creation**: 
   - VL models: Creates `PaddleOCRVL` instance with advanced features enabled
   - Traditional models: Creates standard `PaddleOCR` instance
3. **Instance Caching**: Both VL and traditional instances are cached for performance
4. **Result Extraction**: Compatible extraction logic handles both VL and traditional results

### Code Flow

```
User Request
    ↓
Endpoint (with model parameters)
    ↓
get_ocr_instance(detection_model, recognition_model)
    ↓
Is VL model? ──→ Yes ──→ Create PaddleOCRVL instance
    ↓                        ↓
    No                       Use VL features:
    ↓                        - Layout detection
Create PaddleOCR instance   - Table recognition
    ↓                        - Formula recognition
    └──→ Perform prediction ← Chart recognition
            ↓                - Seal recognition
    extract_ocr_data()
            ↓
    Format response (compatible with both)
            ↓
    Return JSON
```

### Key Functions

#### routers/ocr.py

```python
def is_vl_model(model_name: Optional[str]) -> bool:
    """Check if the model name is a VL model"""
    return model_name in ["PaddleOCR-VL-1.5", "PaddleOCR-VL"]

def get_ocr_instance(detection_model, recognition_model) -> Union[PaddleOCR, PaddleOCRVL]:
    """Get or create OCR instance, supporting both traditional and VL models"""
    # Detect VL model and create appropriate instance
    # Returns cached instance if available
```

#### routers/pdf_ocr.py

```python
def get_pdf_ocr(detection_model, recognition_model) -> Union[PaddleOCR, PaddleOCRVL]:
    """Get or create OCR instance for PDF processing"""
    # Similar to get_ocr_instance but for PDF endpoints
```

## Backward Compatibility

### Guaranteed Compatibility

✅ **Default behavior unchanged**: Calls without model parameters use PP-OCRv5 models
✅ **Existing parameters work**: PP-OCRv4 and PP-OCRv5 model names function as before
✅ **Response format preserved**: All responses maintain the same JSON structure
✅ **No breaking changes**: Existing API clients work without modification

### Migration Path

No migration is needed! The VL models are purely additive:

1. **Current users**: Continue using the API as-is (no changes required)
2. **New features**: Add `detection_model=PaddleOCR-VL-1.5` to use VL capabilities
3. **Gradual adoption**: Test VL models on complex documents, keep traditional models for simple cases

## Performance Considerations

### Model Size & Download
- **First use**: VL models download automatically (~2GB)
- **Subsequent uses**: Models are cached locally
- **Storage**: Ensure adequate disk space

### Resource Usage
| Model | Memory | CPU Usage | Speed |
|-------|--------|-----------|-------|
| PP-OCRv5 | ~500MB | Low | Fast |
| PaddleOCR-VL | ~2GB | Medium-High | Moderate |

### Recommendations

- **Simple documents**: Use default PP-OCR models (faster, lighter)
- **Complex documents**: Use VL models for better accuracy
- **Mixed workload**: Route by document complexity
- **Resource limits**: Consider separate instances for VL models

## Environment Variables

You can configure the OCR behavior using environment variables:

```bash
# Language setting (default: ch)
export OCR_LANGUAGE=ch

# Device selection (default: cpu)
export OCR_DEVICE=cpu  # or 'gpu'

# Debug mode (default: 0)
export OCR_DEBUG=1  # Enable verbose logging
```

## Testing

### Run VL API Tests

```bash
# Documentation and usage examples
python test_vl_api.py

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000

# Test with Swagger UI
# Open: http://localhost:8000/docs
```

### Manual Testing

1. **Start server**: `uvicorn main:app`
2. **Access Swagger UI**: http://localhost:8000/docs
3. **Choose an endpoint**: e.g., `/ocr/predict-by-file`
4. **Set model parameter**: `detection_model=PaddleOCR-VL-1.5`
5. **Upload file and execute**

## Troubleshooting

### Issue: Models Not Downloading

**Solution**: Ensure internet connection and adequate disk space. First use requires downloading ~2GB.

### Issue: Out of Memory

**Solution**: VL models require more memory. Consider:
- Using CPU with more RAM
- Using GPU if available
- Processing smaller images/documents

### Issue: Slow Performance

**Solution**: 
- VL models are slower than traditional models
- Use traditional models for simple documents
- Consider GPU acceleration for VL models

### Issue: Unexpected Results

**Solution**:
- Enable debug mode: `OCR_DEBUG=1`
- Check logs for detailed information
- Verify model is correctly specified

## Future Enhancements

Potential future improvements:

- [ ] Streaming support for large documents
- [ ] Batch processing for multiple files
- [ ] Custom prompt support for VL models
- [ ] Fine-tuning endpoint
- [ ] Model versioning and selection
- [ ] Performance monitoring and metrics

## References

- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL Models](https://github.com/PaddlePaddle/PaddleOCR#paddleocr-vision-language)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/infordoc/PaddleOCRFastAPI/issues)
- PaddleOCR Community: [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)

---

**Last Updated**: February 2026
**Version**: 2.1.0
