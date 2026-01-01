import requests
import json

def test_175_24_233_134():
    print("🧪 测试云服务器 175.24.233.134:3389")
    
    try:
        # 测试连接
        response = requests.get("http://175.24.233.134:3389/api/test", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务器连接成功!")
            print(f"消息: {data.get('message')}")
            
            # 测试文件列表
            list_response = requests.get("http://175.24.233.134:3389/api/list", timeout=10)
            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get('success'):
                    files = list_data.get('files', [])
                    print(f"✅ 文件列表获取成功，共 {len(files)} 个文件:")
                    for file_info in files[:3]:  # 显示前3个
                        print(f"   - {file_info.get('filename')} ({file_info.get('size')} 字节)")
            else:
                print(f"❌ 文件列表失败: {list_data.get('error')}")
        else:
            print(f"❌ 服务器响应错误: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接被拒绝 - 请检查服务器状态和防火墙")
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_175_24_233_134()