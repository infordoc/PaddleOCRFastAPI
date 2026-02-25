# Guia de Deploy no Dokploy

## 📦 Deploy PaddleOCR FastAPI no Dokploy

Este guia mostra como fazer deploy do PaddleOCR 3.x FastAPI diretamente do GitHub usando Dokploy.

---

## 🚀 Método 1: Deploy via GitHub (Recomendado)

### Passo 1: Preparar o Repositório

1. Faça fork ou clone este repositório para sua conta GitHub
2. Certifique-se de que os arquivos estão atualizados:
   - `Dockerfile` - Multi-stage build otimizado
   - `docker-compose.yml` - Configuração completa
   - `requirements.txt` - Dependências Python

### Passo 2: Configurar no Dokploy

1. **Criar Novo Projeto**
   - Acesse seu painel Dokploy
   - Clique em "New Project" ou "Novo Projeto"
   - Nome: `paddleocr-api`

2. **Conectar Repositório GitHub**
   - Tipo de Deploy: **Docker Compose**
   - Source: **GitHub Repository**
   - URL: `https://github.com/SEU_USUARIO/PaddleOCRFastAPI`
   - Branch: `main` ou `copilot/update-paddleocr-to-3x`
   - Compose File: `docker-compose.yml`

3. **Configurar Variáveis de Ambiente**
   ```
   TZ=America/Sao_Paulo
   OCR_LANGUAGE=pt
   OCR_DEBUG=0
   USE_GPU=false
   ```

4. **Configurar Porta**
   - Port Mapping: `8000:8000`
   - Protocol: HTTP

5. **Recursos (Ajuste conforme seu servidor)**
   - CPU: 2 cores (limite) / 0.5 cores (reserva)
   - Memory: 3GB (limite) / 1GB (reserva)

### Passo 3: Deploy

1. Clique em "Deploy" ou "Build & Deploy"
2. Dokploy irá:
   - Clonar o repositório
   - Construir a imagem usando o Dockerfile
   - Iniciar o container com docker-compose.yml
   - Configurar health checks

3. **Tempo de primeira execução**: ~5-10 minutos
   - Build da imagem: 3-5 min
   - Download dos modelos PP-OCRv5: 2-5 min

---

## 🔧 Método 2: Deploy Manual com Docker Compose

Se preferir fazer deploy manual em seu servidor:

```bash
# 1. Clone o repositório
git clone https://github.com/infordoc/PaddleOCRFastAPI.git
cd PaddleOCRFastAPI

# 2. (Opcional) Configure variáveis de ambiente
nano docker-compose.yml
# Edite as variáveis conforme necessário

# 3. Build e start
docker-compose up -d --build

# 4. Verifique os logs
docker-compose logs -f paddleocr-api
```

---

## 📊 Verificação do Deploy

### 1. Health Check
```bash
# Verificar se o container está saudável
docker ps

# Deve mostrar "healthy" no STATUS
```

### 2. Acessar API
- **Swagger/Docs**: `http://seu-dominio.com:8000/docs`
- **Health endpoint**: `http://seu-dominio.com:8000/health`

### 3. Teste Rápido
```bash
# Upload de imagem para OCR
curl -X POST "http://localhost:8000/ocr/predict-by-file" \
  -F "file=@sua-imagem.jpg"
```

---

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão | Exemplos |
|----------|-----------|--------|----------|
| `TZ` | Timezone | `America/Sao_Paulo` | `America/New_York`, `Europe/London` |
| `OCR_LANGUAGE` | Idioma de reconhecimento | `pt` | `ch`, `en`, `fr`, `es` |
| `OCR_DEBUG` | Modo debug | `0` | `0` (off), `1` (on) |
| `USE_GPU` | Usar GPU | `false` | `false`, `true` |

### Idiomas Suportados
- `pt` - Português
- `en` - Inglês
- `ch` - Chinês
- `fr` - Francês
- `es` - Espanhol
- `de` - Alemão
- `ja` - Japonês
- `ko` - Coreano

[Lista completa de idiomas](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md)

---

## 💾 Volumes e Persistência

### Volume de Modelos
```yaml
volumes:
  paddleocr_models:/root/.paddleocr
```

**Importante**: Este volume armazena os modelos PP-OCRv5 (~500MB-1GB). Mantê-lo persiste os modelos entre reinicializações, evitando downloads repetidos.

### Volumes Opcionais

Para uploads e outputs persistentes, descomente no `docker-compose.yml`:

```yaml
volumes:
  - ./uploads:/app/uploads      # Imagens enviadas
  - ./output:/app/output        # Resultados salvos
```

---

## 🔍 Recursos do Sistema

### Requisitos Mínimos
- **CPU**: 1 core
- **RAM**: 1.5GB
- **Disco**: 5GB (3GB para modelos + 2GB para sistema)

### Requisitos Recomendados
- **CPU**: 2 cores
- **RAM**: 3GB
- **Disco**: 10GB

### Ajuste de Recursos no Dokploy

No `docker-compose.yml`, ajuste a seção `deploy.resources`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Máximo de CPU
      memory: 3G       # Máximo de RAM
    reservations:
      cpus: '0.5'      # Mínimo de CPU
      memory: 1G       # Mínimo de RAM
```

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker logs paddleocr-api

# Ou com docker-compose
docker-compose logs paddleocr-api
```

**Causas comuns**:
- Porta 8000 já em uso
- RAM insuficiente (< 1.5GB)
- Modelos não conseguem baixar (problemas de rede)

### Health check falha

```bash
# Verificar se a API responde
curl http://localhost:8000/docs

# Verificar logs do health check
docker inspect paddleocr-api | grep -A 10 Health
```

### Modelos não carregam

```bash
# Entrar no container
docker exec -it paddleocr-api bash

# Verificar diretório de modelos
ls -lh /root/.paddleocr/

# Limpar cache e reiniciar
docker-compose down -v
docker-compose up -d
```

### Performance lenta

1. **Aumentar recursos**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4.0'
         memory: 4G
   ```

2. **Verificar uso de CPU/RAM**:
   ```bash
   docker stats paddleocr-api
   ```

3. **Considerar GPU** (requer imagem CUDA):
   ```yaml
   environment:
     - USE_GPU=true
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

---

## 📡 Endpoints da API

### OCR Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/docs` | Documentação Swagger |
| `GET` | `/health` | Health check |
| `GET` | `/ocr/predict-by-path` | OCR de caminho local |
| `POST` | `/ocr/predict-by-base64` | OCR de imagem base64 |
| `POST` | `/ocr/predict-by-file` | OCR de arquivo enviado |
| `GET` | `/ocr/predict-by-url` | OCR de URL de imagem |

### PDF Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/pdf/predict-by-url` | Extrair tabelas de PDF por URL |
| `POST` | `/pdf/predict-by-file` | Extrair tabelas de PDF enviado |

---

## 🔐 Segurança

### Recomendações

1. **Usar HTTPS**: Configure SSL/TLS no Dokploy ou use proxy reverso (Nginx/Traefik)
2. **Limitar Acesso**: Configure firewall para permitir apenas IPs confiáveis
3. **Autenticação**: Considere adicionar API key ou OAuth2
4. **Rate Limiting**: Implemente rate limiting para evitar abuso

### Configuração de Proxy Reverso (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name ocr.seudominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📈 Monitoramento

### Logs

```bash
# Logs em tempo real
docker logs -f paddleocr-api

# Últimas 100 linhas
docker logs --tail 100 paddleocr-api

# Logs com timestamps
docker logs -t paddleocr-api
```

### Métricas

```bash
# CPU, RAM, Network, Disk I/O
docker stats paddleocr-api

# Detalhes do container
docker inspect paddleocr-api
```

### Health Status

```bash
# Verificar health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 🔄 Atualizações

### Atualizar para Nova Versão

```bash
# Com Dokploy: simplesmente clique em "Redeploy"

# Manual:
cd PaddleOCRFastAPI
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Rollback

```bash
# Voltar para versão anterior
git checkout <commit-hash>
docker-compose up -d --build
```

---

## 📚 Recursos Adicionais

- [README Principal](README.md)
- [Guia de Migração 2.x → 3.x](MIGRATION_GUIDE.md)
- [Referência Rápida](QUICK_REFERENCE.md)
- [Changelog](CHANGELOG.md)
- [Documentação PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

---

## 💬 Suporte

- **Issues**: [GitHub Issues](https://github.com/infordoc/PaddleOCRFastAPI/issues)
- **Discussões**: [GitHub Discussions](https://github.com/infordoc/PaddleOCRFastAPI/discussions)
- **Documentação**: `/docs` na API rodando

---

## ✅ Checklist de Deploy

- [ ] Repositório conectado no Dokploy
- [ ] Variáveis de ambiente configuradas
- [ ] Recursos (CPU/RAM) alocados adequadamente
- [ ] Porta 8000 exposta e acessível
- [ ] Volume de modelos configurado
- [ ] Health check passando
- [ ] API acessível via `/docs`
- [ ] Teste de OCR funcionando
- [ ] Logs sem erros críticos
- [ ] Monitoramento configurado

---

**Última atualização**: 2024-02-25  
**Versão**: PaddleOCR 3.x (3.4.0) + PaddlePaddle 3.0+ (3.2.0)
