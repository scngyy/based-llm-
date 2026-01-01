"""
直接测试上传和访问
"""

import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import *

def test_upload():
    """测试上传到云服务器"""
    
    # 创建测试PDF文件
    test_content = b"%PDF-1.1\n1 0 obj\n<<\n/Length 44\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\n2 0 obj\n<<\n/Type /Catalog\n/Pages 1 0 R\n>>\nendobj\n3 0 obj\n<<\n/Type /Pages\n/Kids [1 0 R]\n/Count 1\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000074 00000 n\n0000000120 00000 n\ntrailer\n<<\n/Size 4\n/Root 2 0 R\n>>\nstartxref\n%%EOF"
    
    with open('test.pdf', 'wb') as f:
        f.write(test_content)
    
    print("测试文件创建完成: test.pdf")
    
    try:
        # 上传文件
        with open('test.pdf', 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            print(f"上传到: {CLOUD_SERVER_URL}/api/upload")
            response = requests.post(f'{CLOUD_SERVER_URL}/api/upload', files=files, timeout=30)
        
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f'✅ 上传成功!')
                file_url = result.get('url')
                print(f'📁 URL: {file_url}')
                
                # 测试访问
                print(f"📋 测试访问: {file_url}")
                test_response = requests.get(file_url, timeout=10)
                print(f'📋 访问测试状态码: {test_response.status_code}')
                if test_response.status_code == 200:
                    print('✅ 文件可以正常访问!')
                else:
                    print('❌ 文件无法访问')
                    
            else:
                print(f'❌ 上传失败: {result.get("error")}')
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            
    except Exception as e:
        print(f'❌ 异常: {str(e)}')
    finally:
        # 清理测试文件
        if os.path.exists('test.pdf'):
            os.remove('test.pdf')
            print('🧹 测试文件已清理')

if __name__ == "__main__":
    test_upload()