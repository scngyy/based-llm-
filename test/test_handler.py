#!/usr/bin/env python3
"""
测试pdf_handler.py的核心功能（不使用GUI）
"""

import os
import sys

# 添加utils目录到路径
utils_dir = os.path.join(os.path.dirname(__file__), '..', 'utils')
sys.path.insert(0, utils_dir)

from pdf_handler import upload_to_own_cloud_server, process_pdf_with_path
from utils.config import *

def test_upload_only():
    """仅测试上传功能"""
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
    except Exception as e:
        print(f"上传失败: {str(e)}")

def test_process_with_path():
    """测试使用直接路径处理"""
    # 使用固定的测试文件路径
    test_pdf = "C:/Users/19154/Desktop/test.pdf"  # 请确保这个文件存在
    
    if not os.path.exists(test_pdf):
        print(f"测试文件不存在: {test_pdf}")
        print("请修改test_pdf变量指向一个存在的PDF文件")
        return
    
    print(f"测试处理文件: {test_pdf}")
    
    try:
        result = process_pdf_with_path(test_pdf)
        print("处理结果:")
        print(f"Success: {result.get('success', False)}")
        if result.get('success'):
            data = result.get('data', {})
            print(f"Markdown长度: {len(data.get('markdown_content', ''))}")
            print(f"分块数量: {len(data.get('chunks', []))}")
        else:
            print(f"错误: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 仅测试上传")
    print("2. 测试完整处理流程")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        test_upload_only()
    elif choice == "2":
        test_process_with_path()
    else:
        print("无效选择")