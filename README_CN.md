# PaddleOCRFastAPI

一个可 Docker (Compose) 部署的, 基于 `FastAPI` 的简易版 Paddle OCR Web API.

## 版本选择

| PaddleOCR | Branch | 状态 |
| :--: | :--: | :--: |
| **v3.x (v3.4.0)** | **main** | **✅ 当前版本** |
| v2.7 | [paddleocr-v2.7](https://github.com/cgcel/PaddleOCRFastAPI/tree/paddleocr-v2.7) | 历史版本 |
| v2.5 | [paddleocr-v2.5](https://github.com/cgcel/PaddleOCRFastAPI/tree/paddleocr-v2.5) | 历史版本 |

> **注意：** 主分支现在使用 PaddleOCR 3.x 配合 PaddlePaddle 3.0+，提供更好的性能、新模型管道（PP-OCRv5）和统一的推理接口。

## 接口功能

- [x] **PaddleOCR 3.x** 搭载 PP-OCRv5 模型，识别精度显著提升
- [x] **PaddlePaddle 3.0+** 兼容性，性能优化
- [x] 局域网范围内路径图片 OCR 识别
- [x] Base64 数据识别
- [x] 上传文件识别
- [x] 图片 URL 识别
- [x] PDF 表格提取（基于 PPStructureV3）
- [x] 多语言支持（80+ 语言）

## 部署方式

### 直接部署

1. 复制项目至部署路径

   ```shell
   git clone https://github.com/cgcel/PaddleOCRFastAPI.git
   ```

   > *master 分支为项目中支持的 PaddleOCR 的最新版本, 如需安装特定版本, 请克隆对应版本号的分支.*

2. (可选) 新建虚拟环境, 避免依赖冲突
3. 安装所需依赖

   ```shell
   pip3 install -r requirements.txt
   ```

4. 运行 FastAPI

   ```shell
   uvicorn main:app --host 0.0.0.0
   ```

### Docker 部署

在 `Centos 7`, `Ubuntu 20.04`, `Ubuntu 22.04`, `Windows 10`, `Windows 11` 中测试成功, 需要先安装好 `Docker`.

1. 复制项目至部署路径

   ```shell
   git clone https://github.com/cgcel/PaddleOCRFastAPI.git
   ```

   > *master 分支为项目中支持的 PaddleOCR 的最新版本, 如需安装特定版本, 请克隆对应版本号的分支.*

2. 制作 Docker 镜像

   ```shell
   cd PaddleOCRFastAPI
   # 手工下载模型，避免程序第一次运行时自动下载。实现完全离线，加快启动速度
   cd pp-ocrv4/ && sh download_det_cls_rec.sh

   # 返回Dockfile所在目录，开始build
   cd ..
   # 使用宿主机网络build
   # 可以用宿主机上的http_proxy和https_proxy
   docker build -t paddleocrfastapi:latest --network host .
   ```

3. 编辑 `docker-compose.yml`

   ```yaml
   version: "3"

   services:

     paddleocrfastapi:
       container_name: paddleocrfastapi # 自定义容器名
       image: paddleocrfastapi:latest # 第2步自定义的镜像名与标签
       environment:
         - TZ=Asia/Hong_Kong
       ports:
        - "8000:8000" # 自定义服务暴露端口, 8000 为 FastAPI 默认端口, 不做修改
       restart: unless-stopped
   ```

4. 生成 Docker 容器并运行

   ```shell
   docker-compose up -d
   ```

5. Swagger 页面请访问 localhost:\<port\>/docs

## Change language

1. 将此仓库克隆至本地.
2. 编辑 `routers/ocr.py`, 修改参数 "lang":

   ```python
   ocr = PaddleOCR(use_angle_cls=True, lang="ch")
   ```

   编辑前, 先阅读 [supported language list](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/multi_languages_en.md#5-support-languages-and-abbreviations).

3. 重新创建 docker 镜像, 或直接运行 `main.py`.

## 运行截图
API 文档：`/docs`

![Swagger](https://raw.githubusercontent.com/cgcel/PaddleOCRFastAPI/dev/screenshots/Swagger.png)

## PaddleOCR 3.x 新特性

本项目已升级至 PaddleOCR 3.x，带来重大改进：

### 主要升级
1. **新模型管道**：PP-OCRv5 显著提升各类文本识别精度，包括手写体
2. **统一推理接口**：简化的 `predict()` API，使用更便捷
3. **PaddlePaddle 3.0 兼容**：完全支持最新 PaddlePaddle 特性和优化
4. **增强表格识别**：PPStructureV3 提供更好的文档理解和表格提取能力

### 从 2.x 迁移
如果您从 PaddleOCR 2.x 升级：
- API 现在使用 `predict()` 方法，而不是带参数的 `ocr()`
- `show_log` 参数被新的日志系统替代
- `use_onnx` 被高性能推理功能替代
- `PPStructure` 现在是 `PPStructureV3`

详情请参阅 [PaddleOCR 3.x 升级文档](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/paddleocr_3x_upgrade_cn.md)

## 文档

- 📖 [快速参考指南](QUICK_REFERENCE.md) - 快速命令和示例
- 📋 [迁移指南](MIGRATION_GUIDE.md) - 从 2.x 迁移到 3.x 的详细说明
- 📝 [更新日志](CHANGELOG.md) - 完整的变更列表
- 💡 [使用示例](examples_paddleocr_3x.py) - 3.x 功能代码示例

## 开发路线图

- [x] 支持 PaddleOCR v3.x (PP-OCRv5)
- [x] 图片 URL 识别
- [x] PDF 表格提取
- [ ] GPU 模式优化
- [ ] 批量处理支持
- [ ] 实时流式 OCR

## License

**PaddleOCRFastAPI** is licensed under the MIT license. Refer to [LICENSE](https://github.com/cgcel/PaddleOCRFastAPI/blob/master/LICENSE) for more information.
