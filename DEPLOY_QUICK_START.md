# 🚀 Deploy Rápido no Dokploy

> Deploy PaddleOCR 3.x FastAPI diretamente do GitHub em 5 minutos

## ⚡ Quick Start

### 1️⃣ No Dokploy

1. **Criar Novo Projeto**
   - Tipo: **Docker Compose**
   - Source: **GitHub Repository**

2. **Configurar**
   ```
   Repository: https://github.com/infordoc/PaddleOCRFastAPI
   Branch: main
   Compose File: docker-compose.yml
   ```

3. **Variáveis de Ambiente**
   ```
   OCR_LANGUAGE=pt
   TZ=America/Sao_Paulo
   ```

4. **Deploy**
   - Clique em "Build & Deploy"
   - Aguarde 5-10 minutos (primeira vez)

### 2️⃣ Acessar

- **API Docs**: `http://seu-dominio:8000/docs`
- **Health**: `http://seu-dominio:8000/health`

---

## 📖 Guia Completo

Para instruções detalhadas, veja: [DOKPLOY_DEPLOY.md](DOKPLOY_DEPLOY.md)

---

## 🔧 Configuração Rápida

### Idiomas Disponíveis

```bash
OCR_LANGUAGE=pt  # Português
OCR_LANGUAGE=en  # Inglês
OCR_LANGUAGE=ch  # Chinês
OCR_LANGUAGE=es  # Espanhol
```

### Recursos Recomendados

```
CPU: 2 cores
RAM: 3GB
Disk: 10GB
```

---

## 📊 Estrutura do Projeto

```
.
├── Dockerfile              # Multi-stage build otimizado
├── docker-compose.yml      # Configuração completa para Dokploy
├── main.py                 # FastAPI application
├── requirements.txt        # Dependências Python
├── routers/               # API endpoints
│   ├── ocr.py            # OCR endpoints
│   └── pdf_ocr.py        # PDF extraction endpoints
└── DOKPLOY_DEPLOY.md     # Guia completo de deploy
```

---

## ✅ Características

- ✅ **PaddleOCR 3.x** - Última versão com PP-OCRv5
- ✅ **Multi-stage Build** - Imagem otimizada
- ✅ **Health Checks** - Monitoramento automático
- ✅ **Model Cache** - Persistência de modelos
- ✅ **80+ Idiomas** - Suporte multilíngue
- ✅ **API REST** - Endpoints completos
- ✅ **Docker Compose** - Deploy simplificado

---

## 🧪 Testar Localmente

```bash
# Clone o repositório
git clone https://github.com/infordoc/PaddleOCRFastAPI.git
cd PaddleOCRFastAPI

# Build e start
docker-compose up -d --build

# Verificar logs
docker-compose logs -f

# Acessar
open http://localhost:8000/docs
```

---

## 📚 Documentação

- [DOKPLOY_DEPLOY.md](DOKPLOY_DEPLOY.md) - Guia completo de deploy
- [README.md](README.md) - Documentação principal
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migração 2.x → 3.x
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Referência rápida

---

## 💡 Dicas

1. **Primeira execução**: Aguarde 5-10 min para download dos modelos
2. **Volume persistente**: Mantém modelos entre restarts
3. **Health check**: Aguarda 60s antes de verificar saúde
4. **Recursos**: Ajuste CPU/RAM no docker-compose.yml

---

## 🐛 Problemas?

Veja a seção **Troubleshooting** em [DOKPLOY_DEPLOY.md](DOKPLOY_DEPLOY.md)

---

**Versão**: PaddleOCR 3.4.0 + PaddlePaddle 3.2.0  
**Última atualização**: 2024-02-25
