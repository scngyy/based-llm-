"""
测试云服务器上传功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_handler import upload_to_own_cloud_server

def test_upload():
    """测试上传到云服务器"""
    
    # 创建测试文件
    test_file = "test_document.pdf"
    print(f"测试上传文件: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        print("请在当前目录放置一个PDF文件进行测试")
        return
    
    # 调用上传函数
    result = upload_to_own_cloud_server(test_file)
    
    print(f"上传结果: {result}")
    
    if result["success"]:
        print("✅ 上传成功！")
        print(f"📁 文件URL: {result['url']}")
    else:
        print("❌ 上传失败！")
        print(f"📝 错误: {result['error']}")

if __name__ == "__main__":
    test_upload()