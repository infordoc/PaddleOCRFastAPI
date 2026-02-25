# Changelog - PaddleOCR 3.x Update

## Version 3.x (Current)

### Date: 2024

### Summary
Upgraded PaddleOCRFastAPI to use PaddleOCR 3.x (v3.4.0) with PaddlePaddle 3.0+ (v3.2.0), bringing significant improvements in performance, accuracy, and ease of use.

---

## 🎉 Major Upgrades

### 1. PaddleOCR 3.x Integration
- **Upgraded from**: PaddleOCR 2.x
- **Upgraded to**: PaddleOCR 3.4.0
- **Benefits**:
  - Enhanced accuracy with PP-OCRv5 models
  - Simplified and unified `predict()` API
  - Better result structure with direct attribute access
  - Improved multi-language support (80+ languages)

### 2. PaddlePaddle 3.0+ Compatibility
- **Upgraded from**: PaddlePaddle 2.x
- **Upgraded to**: PaddlePaddle 3.2.0
- **Benefits**:
  - Performance optimizations
  - CINN compiler support
  - Better hardware compatibility
  - Modern architecture support

### 3. PP-OCRv5 Models
- **Detection Model**: PP-OCRv5_mobile_det
- **Recognition Model**: PP-OCRv5_mobile_rec
- **Improvements**:
  - Higher accuracy for various text types
  - Better handwriting recognition
  - Improved complex document parsing

### 4. PPStructureV3 Table Recognition
- **Upgraded from**: PPStructure (2.x)
- **Upgraded to**: PPStructureV3 (3.x)
- **Benefits**:
  - More accurate table structure detection
  - Better handling of complex tables
  - Improved PDF table extraction

---

## 📝 API Changes

### Simplified OCR Interface

**Before (2.x):**
```python
ocr = PaddleOCR(show_log=False, lang="en")
result = ocr.ocr("img.png", det=True, rec=True)
```

**After (3.x):**
```python
ocr = PaddleOCR(lang="en")
result = ocr.predict("img.png")
```

### Clearer Result Structure

**Before (2.x):**
```python
# Nested lists: [[[bbox], (text, score)], ...]
for res in result:
    for line in res:
        bbox, (text, score) = line
```

**After (3.x):**
```python
# Direct attribute access
for res in result:
    res.print()  # Built-in print
    res.save_to_img("output")  # Built-in visualization
    # Or access attributes
    texts = res.rec_texts
    boxes = res.rec_boxes
    scores = res.rec_scores
```

### Model Configuration

**Before (2.x):**
```python
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_onnx=True  # Deprecated
)
```

**After (3.x):**
```python
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_angle_cls=True,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    lang='ch'
)
```

---

## 🔄 Breaking Changes

### Removed/Deprecated Features

1. **`show_log` parameter**: Replaced with new logging system
2. **`use_onnx` parameter**: Replaced with high-performance inference
3. **`PPStructure`**: Replaced with `PPStructureV3`
4. **`.ocr()` with parameters**: Use `.predict()` instead

### Migration Required For

- Code using `show_log=False` for logging control
- Code using `use_onnx=True` for ONNX inference
- Code importing `PPStructure` (change to `PPStructureV3`)
- Code calling `.ocr(det=True, rec=True)` (change to `.predict()`)

---

## ✨ New Features

### 1. Enhanced Model Pipelines
- PP-OCRv5 for improved accuracy
- Better handwriting recognition
- Enhanced multi-language support

### 2. Simplified API
- Unified `predict()` interface
- Built-in `print()` and `save_to_img()` methods
- Clearer parameter names

### 3. Better Table Recognition
- PPStructureV3 with improved accuracy
- Advanced document understanding
- Better complex table handling

### 4. PDF Processing
- Enhanced PDF to table extraction
- Better multi-page handling
- Improved coordinate-based table reconstruction

---

## 🐛 Bug Fixes

- Fixed result structure inconsistencies
- Improved error handling
- Better memory management
- Enhanced compatibility with different input formats

---

## 📚 Documentation Updates

### New Documentation
- `MIGRATION_GUIDE.md`: Comprehensive migration guide
- `examples_paddleocr_3x.py`: Usage examples for 3.x
- Updated `README.md` and `README_CN.md`
- `test_compatibility.py`: Validation script

### Updated Documentation
- All code comments updated for 3.x
- API endpoint documentation
- Docker deployment instructions
- Testing guidelines

---

## 🧪 Testing

### New Tests
- `test_compatibility.py`: Validates 3.x compatibility
- Updated `test_paddleocr.py`: Tests PP-OCRv5 initialization
- Updated `test_ppstructure.py`: Tests PPStructureV3

### Test Coverage
- ✅ Import validation
- ✅ Model initialization
- ✅ API structure verification
- ✅ Code pattern analysis
- ✅ Deprecated API detection

---

## 🔧 Configuration

### Requirements Updates
- `paddleocr>=3.0.0` (was: no version constraint)
- `paddlepaddle>=3.0.0` (was: no version constraint)
- Added version comments in `requirements.in`

### Docker Updates
- Updated Dockerfile with 3.x comments
- Maintained compatibility with existing deployment

---

## 🚀 Performance Improvements

### Expected Improvements
1. **Recognition Accuracy**: ~5-10% improvement with PP-OCRv5
2. **Inference Speed**: PaddlePaddle 3.0 optimizations
3. **Memory Usage**: Better resource management
4. **Table Extraction**: More accurate with PPStructureV3

---

## 📋 REST API Endpoints (No Changes)

All existing endpoints remain unchanged for backward compatibility:

- `GET /ocr/predict-by-path` - Local image recognition
- `POST /ocr/predict-by-base64` - Base64 image recognition
- `POST /ocr/predict-by-file` - File upload recognition
- `GET /ocr/predict-by-url` - URL image recognition
- `GET /pdf/predict-by-url` - PDF URL table extraction
- `POST /pdf/predict-by-file` - PDF upload table extraction

---

## 🔮 Future Roadmap

### Planned Features
- [ ] GPU mode optimization
- [ ] Batch processing support
- [ ] Real-time streaming OCR
- [ ] Custom model fine-tuning guides
- [ ] Enhanced visualization options

### Known Limitations
- Incomplete native C++ deployment support
- High-performance service deployment not yet on par with PaddleServing 2.x
- On-device deployment supports limited models

---

## 🤝 Migration Guide

For detailed migration instructions, see `MIGRATION_GUIDE.md`.

### Quick Migration Checklist
- [x] Update dependencies to PaddleOCR 3.x
- [x] Remove `show_log` parameters
- [x] Replace `.ocr()` with `.predict()`
- [x] Update `PPStructure` to `PPStructureV3`
- [x] Update model names to PP-OCRv5
- [x] Test all API endpoints
- [x] Validate result processing

---

## 📞 Support

### Resources
- [PaddleOCR 3.x Official Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Usage Examples](examples_paddleocr_3x.py)
- [GitHub Issues](https://github.com/infordoc/PaddleOCRFastAPI/issues)

### Getting Help
1. Check the migration guide
2. Review the examples
3. Search existing issues
4. Create a new issue with details

---

## 🎯 Compatibility

### Supported Versions
- **Python**: 3.9+
- **PaddleOCR**: 3.x (3.4.0+)
- **PaddlePaddle**: 3.x (3.2.0+)
- **FastAPI**: 0.115+

### Tested Platforms
- ✅ Linux (Ubuntu 20.04, 22.04, CentOS 7)
- ✅ Windows (10, 11)
- ✅ macOS (Intel and Apple Silicon)
- ✅ Docker

---

## 👥 Contributors

This update was made possible by the PaddleOCR community and the FastAPI ecosystem.

### Special Thanks
- PaddlePaddle team for PaddleOCR 3.x
- Original PaddleOCRFastAPI contributors
- Community testers and reviewers

---

## 📄 License

This project maintains the MIT license. See [LICENSE](LICENSE) for details.

---

## 📅 Version History

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **3.x** | **2024** | **PaddleOCR 3.x, PP-OCRv5, PaddlePaddle 3.0+** |
| 2.7 | 2023 | PaddleOCR 2.7, PP-OCRv4 |
| 2.5 | 2022 | PaddleOCR 2.5, PP-OCRv3 |

---

*For more information, see the [README](README.md) and [MIGRATION_GUIDE](MIGRATION_GUIDE.md).*
