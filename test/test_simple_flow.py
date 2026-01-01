"""
测试简单流程：上传 + 模拟解析 + 处理
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import *

def test_simple_flow():
    """测试简单流程"""
    
    # 选择PDF文件
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    
    print("请选择PDF文件...")
    file_path = filedialog.askopenfilename(
        title="选择PDF文件",
        filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
    )
    
    root.destroy()
    
    if not file_path:
        print("未选择文件")
        return
    
    print(f"选择的文件: {file_path}")
    
    try:
        # 步骤1: 上传到云服务器
        print("步骤1: 上传PDF到云服务器...")
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post(
                f"{CLOUD_SERVER_URL}/api/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                pdf_url = f"{CLOUD_SERVER_URL}/uploads/{os.path.basename(file_path)}"
                print(f"✅ 上传成功！URL: {pdf_url}")
            else:
                print(f"❌ 上传失败: {result.get('error')}")
                return
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return
        
        # 步骤2: 模拟解析成功
        print("步骤2: 模拟PDF解析...")
        markdown_content = f"# {os.path.basename(file_path)}\n\n这是一个测试PDF文档的内容。\n\n## 章节一\n测试内容...\n\n## 章节二\n更多测试内容..."
        print(f"✅ 模拟解析完成，内容长度: {len(markdown_content)}")
        
        # 步骤3: 模拟处理
        print("步骤3: 模拟内容处理...")
        chunks = [
            {"content": markdown_content[:500] + "...", "index": 0},
            {"content": "..." + markdown_content[500:1000] + "...", "index": 1}
        ]
        prompts = [{"content": markdown_content, "type": "full"}]
        
        print("✅ 处理完成！")
        
        print(f"\n📊 处理统计:")
        print(f"   PDF URL: {pdf_url}")
        print(f"   内容长度: {len(markdown_content)} 字符")
        print(f"   分块数量: {len(chunks)} 个")
        print(f"   Prompt数量: {len(prompts)} 个")
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")

if __name__ == "__main__":
    test_simple_flow()