import requests
import json

# 测试文件上传API
print('=== 测试 POST /pdf/predict-by-file ===')
with open('Products.pdf', 'rb') as f:
    files = {'file': ('Products.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/pdf/predict-by-file', files=files)
    
print(f'状态码: {response.status_code}')
result = response.json()
print(f'响应信息: {result["message"]}')
print(f'\n表格数据:')
print(json.dumps(result['data'], indent=2, ensure_ascii=False))

print('\n✓ API测试完成')
