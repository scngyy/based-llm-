"""
云服务器调试测试
"""

import requests
from utils.config import *

def debug_server():
    """调试云服务器状态"""
    
    print(f"🔍 配置的云服务器: {CLOUD_SERVER_URL}")
    print()
    
    # 测试1: 连通性测试
    print("🌐 测试1: 连通性测试")
    try:
        response = requests.get(f"{CLOUD_SERVER_URL}/api/test", timeout=10)
        print(f"✅ 连接成功: {response.status_code}")
        print(f"📋 响应: {response.json()}")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
    
    print()
    
    # 测试2: 检查服务器实际返回的IP
    print("🌐 测试2: 上传测试并检查返回IP")
    test_content = b"%PDF-1.1\n1 0 obj\n<<\n/Length 44\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\n2 0 obj\n<<\n/Type /Catalog\n/Pages 1 0 R\n>>\nendobj\n3 0 obj\n<<\n/Type /Pages\n/Kids [1 0 R]\n/Count 1\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000074 00000 n\ntrailer\n<<\n/Size 4\n/Root 2 0 R\n>>\nstartxref\n%%EOF"
    
    try:
        with open('debug.pdf', 'wb') as f:
            f.write(test_content)
        
        with open('debug.pdf', 'rb') as f:
            files = {'file': ('debug.pdf', f, 'application/pdf')}
            response = requests.post(f'{CLOUD_SERVER_URL}/api/upload', files=files, timeout=30)
        
        print(f"📤 上传状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 完整响应: {result}")
            
            if result.get('success'):
                returned_url = result.get('url')
                print(f"🌐 服务器返回的URL: {returned_url}")
                
                # 提取URL中的IP
                import re
                match = re.search(r'http://([\d.]+):', returned_url)
                if match:
                    returned_ip = match.group(1)
                    print(f"📍 返回IP: {returned_ip}")
                    print(f"📍 配置IP: {CLOUD_SERVER_IP}")
                    
                    if returned_ip != CLOUD_SERVER_IP:
                        print("⚠️  IP不匹配！问题：")
                        print("   1. 服务器运行的不是当前文件")
                        print("   2. 可能有环境变量覆盖")
                        print("   3. 可能有多个服务器实例")
                    else:
                        print("✅ IP匹配正常")
                
        else:
            print(f"❌ 上传失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    finally:
        import os
        if os.path.exists('debug.pdf'):
            os.remove('debug.pdf')

if __name__ == "__main__":
    debug_server()