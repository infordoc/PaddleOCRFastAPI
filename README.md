[![Docker Build](https://github.com/neozhu/PaddleOCRFastAPI/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/neozhu/PaddleOCRFastAPI/actions/workflows/docker-publish.yml)
[![Python Build](https://github.com/neozhu/PaddleOCRFastAPI/actions/workflows/python-build.yml/badge.svg)](https://github.com/neozhu/PaddleOCRFastAPI/actions/workflows/python-build.yml)

# PaddleOCRFastAPI

![GitHub](https://img.shields.io/github/license/cgcel/PaddleOCRFastAPI)

[中文](./README_CN.md)

A simple way to deploy `PaddleOCR` based on `FastAPI`.

## Support Version

| PaddleOCR | Branch | Status |
| :--: | :--: | :--: |
| **v3.x (v3.4.0)** | **main** | **✅ Current** |
| v2.7 | [paddleocr-v2.7](https://github.com/neozhu/PaddleOCRFastAPI/tree/paddleocr-v2.7) | Legacy |
| v2.5 | [paddleocr-v2.5](https://github.com/neozhu/PaddleOCRFastAPI/tree/paddleocr-v2.5) | Legacy |

> **Note:** The main branch now uses PaddleOCR 3.x with PaddlePaddle 3.0+, featuring improved performance, new model pipelines (PP-OCRv5), and unified inference interfaces.

## Features

- [x] **PaddleOCR 3.x** with PP-OCRv5 models for enhanced accuracy
- [x] **PaddlePaddle 3.0+** compatibility with optimized performance
- [x] **PaddleOCR-VL support** - Optional multimodal vision-language models for advanced document analysis
  - 111 language support
  - Automatic layout detection
  - Complex table recognition
  - Formula and chart recognition
  - Seal and stamp recognition
  - **✅ Docker images include VL dependencies by default**
- [x] Local path image recognition
- [x] Base64 data recognition
- [x] Upload file recognition
- [x] URL image recognition
- [x] PDF table extraction with PPStructureV3
- [x] Multi-language support (80+ languages with traditional models, 111 with VL models)
- [x] Model selection support (PP-OCRv4, PP-OCRv5, PaddleOCR-VL)

> 📖 **See [PaddleOCR-VL Integration Guide](PADDLEOCR_VL_GUIDE.md)** for detailed documentation on using VL models
> 
> ✅ **Docker Deployment**: VL dependencies are pre-installed in Docker images. For local installation, `requirements.txt` now includes `paddlex[ocr]`.

## Deployment Methods

### Docker Deployment (Recommended for VL Models)

The Docker setup includes all dependencies for both traditional PP-OCR and VL models.

**Quick Start with Docker Compose:**
```shell
docker-compose up -d
```

**Benefits:**
- ✅ All VL dependencies (`paddlex[ocr]`) pre-installed
- ✅ Persistent model cache across restarts
- ✅ Resource limits optimized for VL models
- ✅ Health checks and auto-restart

See [Docker Deployment](#docker-deployment) section below for detailed configuration.

### Deploy Directly

1. Copy the project to the deployment path

   ```shell
   git clone https://github.com/neozhu/PaddleOCRFastAPI.git
   ```

   > *The master branch is the most recent version of PaddleOCR supported by the project. To install a specific version, clone the branch with the corresponding version number.*

2. (Optional) Create new virtual environment to avoid dependency conflicts
3. Install required dependencies

   ```shell
   pip3 install -r requirements.txt
   ```
   
   > **Note**: `requirements.txt` now includes `paddlex[ocr]` for VL model support.

4. Run FastAPI

   ```shell
   uvicorn main:app --host 0.0.0.0
   ```

### Docker Deployment

Test completed in `Centos 7`, `Ubuntu 20.04`, `Ubuntu 22.04`, `Windows 10`, `Windows 11`, requires `Docker` to be installed.

#### Quick Deploy with Dokploy

For deployment using Dokploy (Docker + GitHub), see:
- 🚀 [Quick Start Guide](DEPLOY_QUICK_START.md) - 5-minute setup
- 📖 [Complete Dokploy Guide](DOKPLOY_DEPLOY.md) - Detailed instructions

#### Manual Docker Build

1. Copy the project to the deployment path

   ```shell
   git clone https://github.com/neozhu/PaddleOCRFastAPI.git
   ```

   > *The master branch is the most recent version of PaddleOCR supported by the project. To install a specific version, clone the branch with the corresponding version number.*

2. Building a Docker Image

   ```shell
   cd PaddleOCRFastAPI
   # 手工下载模型，避免程序第一次运行时自动下载，实现完全离线，加快启动速度
   cd pp-ocrv4/ && sh download_det_cls_rec.sh
   
   # 返回Dockfile所在目录，开始build
   cd ..
   # 使用宿主机网络
   # 可直接使用宿主机上的代理设置，例如在build时，用宿主机上的代理
   # docker build -t paddleocrfastapi:latest --network host --build-arg HTTP_PROXY=http://127.0.0.1:8888 --build-arg HTTPS_PROXY=http://127.0.0.1:8888 .
   docker build -t paddleocrfastapi:latest --network host .
   ```

3. Edit `docker-compose.yml`

   ```yaml
   version: "3"

   services:

     paddleocrfastapi:
       container_name: paddleocrfastapi # Custom Container Name
       image: paddleocrfastapi:lastest # Customized Image Name & Label in Step 2
       environment:
         - TZ=Asia/Hong_Kong
         - OCR_LANGUAGE=ch # support 80 languages. refer to https://github.com/Mushroomcat9998/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md#language_abbreviations
       ports:
        - "8000:8000" # Customize the service exposure port, 8000 is the default FastAPI port, do not modify
       restart: unless-stopped
   ```

4. Create the Docker container and run

   ```shell
   docker compose up -d
   ```

5. Swagger Page at `localhost:<port>/docs`

## deploy and push your local code as blazordevlab/paddleocrapi:latest to Docker Hub 
1. Login to Docker Hub
```
docker login
```
2. Build the Docker Image
```
docker build -t blazordevlab/paddleocrapi:latest .
```
3. Push the Image to Docker Hub
```
docker push blazordevlab/paddleocrapi:latest
```

## Change language

1. Clone this repo to localhost.
2. Edit `routers/ocr.py`, modify the parameter "lang":

   ```python
   ocr = PaddleOCR(use_angle_cls=True, lang="ch")
   ```

   Before modify, read the [supported language list](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/multi_languages_en.md#5-support-languages-and-abbreviations).

3. Rebuild the docker image, or run the `main.py` directly.

## Screenshots
API Docs: `/docs`

![Swagger](https://raw.githubusercontent.com/cgcel/PaddleOCRFastAPI/dev/screenshots/Swagger.png)

## What's New in PaddleOCR 3.x

This project has been upgraded to PaddleOCR 3.x, bringing significant improvements:

### Key Upgrades
1. **New Model Pipelines**: PP-OCRv5 with improved recognition accuracy for various text types including handwriting
2. **Unified Inference Interface**: Simplified `predict()` API for streamlined usage
3. **PaddlePaddle 3.0 Compatibility**: Full support for the latest PaddlePaddle features and optimizations
4. **Enhanced Table Recognition**: PPStructureV3 for better document understanding and table extraction

### Migration from 2.x
If you're upgrading from PaddleOCR 2.x:
- The API now uses `predict()` method instead of `ocr()` with parameters
- `show_log` parameter is replaced by a new logging system
- `use_onnx` is replaced by high-performance inference features
- `PPStructure` is now `PPStructureV3`

For more details, see the [PaddleOCR 3.x Upgrade Documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/paddleocr_3x_upgrade_en.md)

## Documentation

- 📖 [Quick Reference Guide](QUICK_REFERENCE.md) - Quick commands and examples
- 🌟 [PaddleOCR-VL Integration Guide](PADDLEOCR_VL_GUIDE.md) - Using multimodal VL models for advanced OCR
- 📋 [Migration Guide](MIGRATION_GUIDE.md) - Detailed migration from 2.x to 3.x
- 📝 [Changelog](CHANGELOG.md) - Complete list of changes
- 💡 [Usage Examples](examples_paddleocr_3x.py) - Code examples for 3.x features

## Quick Start with VL Models

Use advanced multimodal models for complex documents:

```python
import requests

# Using PaddleOCR-VL-1.5 for complex document recognition
response = requests.get(
    "http://localhost:8000/ocr/predict-by-path",
    params={
        "image_path": "/path/to/complex_document.jpg",
        "detection_model": "PaddleOCR-VL-1.5"
    }
)
result = response.json()
```

See the [PaddleOCR-VL Integration Guide](PADDLEOCR_VL_GUIDE.md) for more examples and detailed documentation.

## Roadmap

- [x] Support PaddleOCR v3.x (PP-OCRv5)
- [x] Image URL recognition
- [x] PDF table extraction
- [x] **PaddleOCR-VL multimodal model support**
- [x] **Model selection for all endpoints (PP-OCRv4, PP-OCRv5, VL)**
- [ ] GPU mode optimization
- [ ] Batch processing support
- [ ] Real-time streaming OCR

## License

**PaddleOCRFastAPI** is licensed under the MIT license. Refer to [LICENSE](https://github.com/cgcel/PaddleOCRFastAPI/blob/master/LICENSE) for more information.
