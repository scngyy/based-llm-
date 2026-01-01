"""
测试公开PDF的解析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_parser import PDFParser
from utils.config import *

def test_public_pdf():
    """测试解析公开PDF"""
    
    # 使用一个公开的PDF URL进行测试
    public_pdf_url = "https://arxiv.org/pdf/2301.07041.pdf"
    
    print(f"测试解析公开PDF: {public_pdf_url}")
    
    try:
        parser = PDFParser(OUTPUT_DIR, MINERU_API_TOKEN)
        
        print("开始解析...")
        markdown_file = parser.parse_pdf_to_markdown(public_pdf_url)
        
        print(f"✅ 解析成功！文件保存到: {markdown_file}")
        
        # 读取内容
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 内容长度: {len(content)} 字符")
        print(f"📝 前200字符: {content[:200]}...")
        
    except Exception as e:
        print(f"❌ 解析失败: {str(e)}")

if __name__ == "__main__":
    test_public_pdf()