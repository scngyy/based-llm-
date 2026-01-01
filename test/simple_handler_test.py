#!/usr/bin/env python3
"""
简单的pdf_handler测试
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from pdf_handler import upload_to_own_cloud_server

def test_upload():
    """测试上传功能"""
    # 使用固定的测试文件路径
    test_pdf = "C:/Users/19154/Desktop/test.pdf"  # 请确保这个文件存在
    
    if not os.path.exists(test_pdf):
        print(f"测试文件不存在: {test_pdf}")
        print("请修改test_pdf变量指向一个存在的PDF文件")
        return
    
    print(f"测试上传文件: {test_pdf}")
    
    try:
        result = upload_to_own_cloud_server(test_pdf)
        print("上传结果:", result)
        
        if result.get("success"):
            print(f"✅ 上传成功，URL: {result.get('url')}")
        else:
            print(f"❌ 上传失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 上传异常: {str(e)}")

if __name__ == "__main__":
    print("测试上传到云服务器...")
    test_upload()