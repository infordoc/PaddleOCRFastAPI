# Novo Recurso: Seleção de Modelo, PDF Base64 e PDF OCR Completo

## 📋 Visão Geral

Recursos adicionados ao PaddleOCR FastAPI:

1. **Seleção de Modelo**: Todos os endpoints suportam escolha de modelo OCR
2. **PDF Base64**: Endpoints para enviar PDF como base64
3. **PDF OCR Completo**: Novos endpoints para extrair todo o texto de PDF (não apenas tabelas)
4. **Modelos Server por Padrão**: Modelos mais precisos como padrão

---

## 🎯 1. Modelos Padrão Atualizados

### Novo Padrão (Mais Preciso)
- **Detecção**: `PP-OCRv5_server_det` - Servidor, mais preciso
- **Reconhecimento**: `PP-OCRv5_server_rec` - Servidor, mais preciso

### Modelos Disponíveis

#### Modelos de Detecção
- `PP-OCRv5_server_det` - **Padrão**, mais preciso, mais lento
- `PP-OCRv5_mobile_det` - Leve e rápido
- `PP-OCRv4_mobile_det` - V4 leve
- `PP-OCRv4_server_det` - V4 servidor

#### Modelos de Reconhecimento
- `PP-OCRv5_server_rec` - **Padrão**, mais preciso, mais lento
- `PP-OCRv5_mobile_rec` - Leve e rápido
- `PP-OCRv4_mobile_rec` - V4 leve
- `PP-OCRv4_server_rec` - V4 servidor

### Usar Modelos Mobile para Performance

```python
# Para velocidade, use modelos mobile
response = requests.post(
    'http://localhost:8000/ocr/predict-by-file?detection_model=PP-OCRv5_mobile_det&recognition_model=PP-OCRv5_mobile_rec',
    files={'file': open('imagem.jpg', 'rb')}
)
```

---

## 📄 2. Novos Endpoints: PDF OCR Completo

### Diferença entre Endpoints PDF

| Endpoint | Função | Retorno |
|----------|--------|---------|
| **POST /ocr/pdf-predict-by-file** | OCR completo | Todo o texto do PDF |
| **POST /ocr/pdf-predict-by-base64** | OCR completo | Todo o texto do PDF |
| POST /pdf/predict-by-file | Extração de tabelas | Apenas tabelas estruturadas |
| POST /pdf/predict-by-base64 | Extração de tabelas | Apenas tabelas estruturadas |

### Endpoint: PDF Upload (OCR Completo)

```
POST /ocr/pdf-predict-by-file
```

**Exemplo:**
```python
import requests

response = requests.post(
    'http://localhost:8000/ocr/pdf-predict-by-file',
    files={'file': open('documento.pdf', 'rb')}
)

result = response.json()
print(f"Status: {result['resultcode']}")
print(f"Mensagem: {result['message']}")

for page_result in result['data']:
    print(f"\nPágina {page_result['page']}:")
    print(f"Textos reconhecidos: {len(page_result['rec_texts'])}")
    for i, text in enumerate(page_result['rec_texts'][:5]):  # Primeiros 5
        print(f"  {i+1}. {text}")
```

### Endpoint: PDF Base64 (OCR Completo)

```
POST /ocr/pdf-predict-by-base64
```

**Exemplo:**
```python
import base64
import requests

# Ler e codificar PDF
with open("documento.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

# Enviar requisição
response = requests.post(
    'http://localhost:8000/ocr/pdf-predict-by-base64',
    json={
        "base64_str": pdf_base64,
        "detection_model": "PP-OCRv5_server_det",  # Opcional
        "recognition_model": "PP-OCRv5_server_rec"  # Opcional
    }
)

result = response.json()
for page_result in result['data']:
    print(f"Página {page_result['page']}: {len(page_result['rec_texts'])} textos")
```

### Response Format

```json
{
  "resultcode": 200,
  "message": "Success: document.pdf, 处理了 3 页",
  "data": [
    {
      "page": 1,
      "input_path": "/tmp/xxx.png",
      "rec_texts": ["Título do Documento", "Parágrafo 1...", "..."],
      "rec_boxes": [
        [[10, 20], [100, 20], [100, 50], [10, 50]],
        [[10, 60], [200, 60], [200, 90], [10, 90]],
        ...
      ]
    },
    {
      "page": 2,
      "rec_texts": ["Continuação...", "..."],
      "rec_boxes": [...]
    }
  ]
}
```

---

## 📊 Todos os Endpoints Atualizados

### OCR - Imagens

| Método | Endpoint | Modelos | Descrição |
|--------|----------|---------|-----------|
| GET | `/ocr/predict-by-path` | Query params | Imagem local |
| POST | `/ocr/predict-by-base64` | Body JSON | Imagem base64 |
| POST | `/ocr/predict-by-file` | Query params | Upload imagem |
| GET | `/ocr/predict-by-url` | Query params | URL imagem |

### OCR - PDF Completo (NOVO)

| Método | Endpoint | Modelos | Descrição |
|--------|----------|---------|-----------|
| POST | `/ocr/pdf-predict-by-file` | Query params | Upload PDF, OCR completo |
| POST | `/ocr/pdf-predict-by-base64` | Body JSON | PDF base64, OCR completo |

### PDF - Extração de Tabelas

| Método | Endpoint | Modelos | Descrição |
|--------|----------|---------|-----------|
| GET | `/pdf/predict-by-url` | Query params | URL PDF, tabelas |
| POST | `/pdf/predict-by-file` | Query params | Upload PDF, tabelas |
| POST | `/pdf/predict-by-base64` | Body JSON | PDF base64, tabelas |

---

## ⚡ Performance e Recursos

### Comparação de Modelos

| Modelo | RAM | Velocidade | Precisão | Uso Recomendado |
|--------|-----|------------|----------|-----------------|
| **Server (Padrão)** | ~1-2GB | Lento | Alta | Produção, precisão crítica |
| Mobile | ~500MB | Rápido | Boa | Alto volume, velocidade |

### Quando Usar Cada Modelo

**Use Server (padrão):**
- Documentos importantes
- Precisão é crítica
- Volume baixo/médio
- Recursos de hardware adequados

**Use Mobile:**
- Alto volume de requisições
- Velocidade é crítica
- Recursos limitados
- Precisão aceitável

---

## 🔄 Comparação: OCR PDF vs Extração de Tabelas

### Use `/ocr/pdf-*` quando:
- Precisa de **todo o texto** do documento
- Quer extrair parágrafos, títulos, notas
- Precisa das coordenadas de cada texto
- Documento tem texto livre (não só tabelas)

### Use `/pdf/*` quando:
- Precisa apenas de **dados tabulares**
- Quer estrutura de tabela (headers + rows)
- Documento contém planilhas/tabelas
- Precisa de dados estruturados prontos

---

## 🧪 Testando

### Via cURL

```bash
# OCR completo de PDF
curl -X POST "http://localhost:8000/ocr/pdf-predict-by-file" \
  -F "file=@documento.pdf"

# Extração de tabelas
curl -X POST "http://localhost:8000/pdf/predict-by-file" \
  -F "file=@documento.pdf"
```

### Via Swagger UI

1. Acesse: `http://localhost:8000/docs`
2. Encontre os novos endpoints em **OCR**:
   - `POST /ocr/pdf-predict-by-file`
   - `POST /ocr/pdf-predict-by-base64`
3. Clique em "Try it out"
4. Faça upload ou cole base64
5. Execute e veja o resultado

---

## 📝 Notas Importantes

### Modelos Padrão
- **Mudança**: Agora usa modelos **server** por padrão
- **Motivo**: Melhor precisão para a maioria dos casos
- **Performance**: ~2x mais lento que mobile, mas mais preciso
- **Compatibilidade**: Modelos mobile ainda disponíveis via parâmetros

### Recursos de Sistema
- **Mobile**: 500MB RAM, processamento rápido
- **Server**: 1-2GB RAM, processamento mais lento
- **Recomendação VPS**: Mínimo 2GB RAM para server models

### PDF OCR
- Converte cada página para imagem (2x resolução)
- Processa página por página
- Retorna resultado estruturado por página
- Páginas com erro não interrompem o processamento

---

## 🆘 Suporte

### Problemas Comuns

**"Out of memory" com modelos server:**
```python
# Solução: Use modelos mobile
response = requests.post(
    'http://localhost:8000/ocr/predict-by-file?detection_model=PP-OCRv5_mobile_det&recognition_model=PP-OCRv5_mobile_rec',
    files={'file': open('image.jpg', 'rb')}
)
```

**PDF muito grande:**
- Recomendado: Máximo 20MB ou 50 páginas
- Processar em partes se necessário

---

## 📖 Exemplos Completos

### Exemplo 1: OCR Completo de PDF com Modelos Mobile

```python
import requests

response = requests.post(
    'http://localhost:8000/ocr/pdf-predict-by-file',
    params={
        'detection_model': 'PP-OCRv5_mobile_det',
        'recognition_model': 'PP-OCRv5_mobile_rec'
    },
    files={'file': open('documento.pdf', 'rb')}
)

result = response.json()
print(f"Processou {len(result['data'])} páginas")
```

### Exemplo 2: Comparar OCR vs Tabelas

```python
import requests

pdf_file = open('relatorio.pdf', 'rb')

# OCR completo
ocr_result = requests.post(
    'http://localhost:8000/ocr/pdf-predict-by-file',
    files={'file': pdf_file}
).json()

pdf_file.seek(0)  # Resetar ponteiro

# Só tabelas
table_result = requests.post(
    'http://localhost:8000/pdf/predict-by-file',
    files={'file': pdf_file}
).json()

print(f"OCR encontrou {sum(len(p['rec_texts']) for p in ocr_result['data'])} textos")
print(f"Tabelas encontrou {len(table_result['data'])} tabelas")
```

---

**Última atualização**: 2024-02-25  
**Commit**: b7a984d

### Como Usar

#### Endpoints OCR

**Arquivo Upload (Multipart)**
```bash
curl -X POST "http://localhost:8000/ocr/predict-by-file?detection_model=PP-OCRv4_mobile_det&recognition_model=PP-OCRv4_mobile_rec" \
  -F "file=@imagem.jpg"
```

**Base64 (JSON)**
```python
import requests
import base64

with open("imagem.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    'http://localhost:8000/ocr/predict-by-base64',
    json={
        "base64_str": img_base64,
        "detection_model": "PP-OCRv4_mobile_det",
        "recognition_model": "PP-OCRv4_mobile_rec"
    }
)
```

**URL**
```bash
curl "http://localhost:8000/ocr/predict-by-url?imageUrl=https://example.com/img.jpg&detection_model=PP-OCRv4_mobile_det&recognition_model=PP-OCRv4_mobile_rec"
```

#### Endpoints PDF

**Arquivo Upload (Multipart)**
```bash
curl -X POST "http://localhost:8000/pdf/predict-by-file?detection_model=PP-OCRv4_mobile_det&recognition_model=PP-OCRv4_mobile_rec" \
  -F "file=@documento.pdf"
```

**URL**
```bash
curl "http://localhost:8000/pdf/predict-by-url?pdf_url=https://example.com/doc.pdf&detection_model=PP-OCRv4_mobile_det&recognition_model=PP-OCRv4_mobile_rec"
```

---

## 📄 2. Novo Endpoint: PDF Base64

### Endpoint

```
POST /pdf/predict-by-base64
```

### Request Body

```json
{
  "base64_str": "JVBERi0xLjQKJeLjz9MK...",
  "detection_model": "PP-OCRv4_mobile_det",
  "recognition_model": "PP-OCRv4_mobile_rec"
}
```

### Exemplo Python

```python
import base64
import requests

# Ler e codificar PDF
with open("documento.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

# Enviar requisição
response = requests.post(
    'http://localhost:8000/pdf/predict-by-base64',
    json={
        "base64_str": pdf_base64,
        "detection_model": "PP-OCRv4_mobile_det",  # Opcional
        "recognition_model": "PP-OCRv4_mobile_rec"  # Opcional
    }
)

# Processar resultado
result = response.json()
print(f"Status: {result['resultcode']}")
print(f"Mensagem: {result['message']}")
print(f"Tabelas extraídas: {len(result['data'])}")

for table in result['data']:
    print(f"\nPágina {table['page']}:")
    print(f"  Cabeçalhos: {table['table']['headers']}")
    print(f"  Linhas: {len(table['table']['rows'])}")
```

### Exemplo JavaScript

```javascript
// Ler arquivo PDF
const fileInput = document.getElementById('pdfFile');
const file = fileInput.files[0];

const reader = new FileReader();
reader.onload = async function(e) {
    const base64 = e.target.result.split(',')[1]; // Remove data URI prefix
    
    // Enviar requisição
    const response = await fetch('http://localhost:8000/pdf/predict-by-base64', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            base64_str: base64,
            detection_model: 'PP-OCRv4_mobile_det',
            recognition_model: 'PP-OCRv4_mobile_rec'
        })
    });
    
    const result = await response.json();
    console.log('Tabelas:', result.data);
};

reader.readAsDataURL(file);
```

### Response

```json
{
  "resultcode": 200,
  "message": "Success: 提取到 2 个表格",
  "data": [
    {
      "page": 1,
      "table": {
        "headers": ["Nome", "Idade", "Cidade"],
        "rows": [
          ["João", "25", "São Paulo"],
          ["Maria", "30", "Rio de Janeiro"]
        ]
      }
    }
  ]
}
```

---

## 🔄 Melhorando Resultados

Se você estava obtendo resultados melhores antes do PR, experimente usar os modelos PP-OCRv4:

```python
# Use PP-OCRv4 para compatibilidade com resultados anteriores
{
    "detection_model": "PP-OCRv4_mobile_det",
    "recognition_model": "PP-OCRv4_mobile_rec"
}
```

### Quando Usar Cada Modelo

| Modelo | Uso Recomendado |
|--------|----------------|
| **PP-OCRv5_mobile** | Padrão, bom equilíbrio velocidade/precisão |
| **PP-OCRv5_server** | Máxima precisão, documentos complexos |
| **PP-OCRv4_mobile** | Compatibilidade com versão anterior |
| **PP-OCRv4_server** | Precisão v4, documentos complexos |

---

## 📊 Todos os Endpoints Atualizados

### OCR Endpoints

| Método | Endpoint | Parâmetros de Modelo |
|--------|----------|---------------------|
| GET | `/ocr/predict-by-path` | Query: `detection_model`, `recognition_model` |
| POST | `/ocr/predict-by-base64` | Body JSON: `detection_model`, `recognition_model` |
| POST | `/ocr/predict-by-file` | Query: `detection_model`, `recognition_model` |
| GET | `/ocr/predict-by-url` | Query: `detection_model`, `recognition_model` |

### PDF Endpoints

| Método | Endpoint | Parâmetros de Modelo | Status |
|--------|----------|---------------------|--------|
| GET | `/pdf/predict-by-url` | Query: `detection_model`, `recognition_model` | Atualizado |
| POST | `/pdf/predict-by-file` | Query: `detection_model`, `recognition_model` | Atualizado |
| POST | `/pdf/predict-by-base64` | Body JSON: `detection_model`, `recognition_model` | **NOVO** |

---

## ⚡ Performance

### Cache de Instâncias

O sistema agora mantém cache de instâncias OCR para diferentes configurações de modelo:

- Primeira requisição: Carrega modelo (~10-30s)
- Requisições subsequentes: Reutiliza instância (instantâneo)
- Cache por combinação de modelos e idioma

### Recomendações

1. **Teste diferentes modelos** para encontrar o melhor para seu caso
2. **Use mobile para volume alto**, server para precisão crítica
3. **Mantenha configuração consistente** para aproveitar cache

---

## 🧪 Testando

### Via Swagger UI

1. Acesse: `http://localhost:8000/docs`
2. Expanda o endpoint desejado
3. Clique em "Try it out"
4. Preencha os parâmetros de modelo (opcional)
5. Execute

### Via Python

Execute o script de teste:
```bash
python test_new_features.py
```

---

## 📝 Notas

- **Compatibilidade**: Todos os endpoints mantêm compatibilidade com código existente
- **Padrão**: Se não especificar modelo, usa PP-OCRv5_mobile
- **Base64**: Suporta com ou sem prefixo data URI (`data:application/pdf;base64,`)
- **Limite**: PDF base64 recomendado até ~20MB

---

## 🆘 Suporte

Para questões ou problemas:
1. Verifique Swagger UI: `/docs`
2. Teste com script: `python test_new_features.py`
3. Abra issue no GitHub

---

**Última atualização**: 2024-02-25  
**Commit**: 607e084
