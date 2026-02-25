# Novo Recurso: Seleção de Modelo e PDF Base64

## 📋 Visão Geral

Foram adicionados dois novos recursos ao PaddleOCR FastAPI:

1. **Seleção de Modelo**: Todos os endpoints agora suportam escolha de modelo OCR
2. **PDF Base64**: Novo endpoint para enviar PDF como base64

---

## 🎯 1. Seleção de Modelo

### Modelos Disponíveis

#### Modelos de Detecção
- `PP-OCRv5_mobile_det` - **Padrão**, leve e rápido
- `PP-OCRv5_server_det` - Mais preciso, mais lento
- `PP-OCRv4_mobile_det` - V4 leve
- `PP-OCRv4_server_det` - V4 servidor

#### Modelos de Reconhecimento
- `PP-OCRv5_mobile_rec` - **Padrão**, leve e rápido
- `PP-OCRv5_server_rec` - Mais preciso, mais lento
- `PP-OCRv4_mobile_rec` - V4 leve
- `PP-OCRv4_server_rec` - V4 servidor

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
