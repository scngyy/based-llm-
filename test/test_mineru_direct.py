"""
直接测试MinerU API使用公开PDF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mineru_parser import parse_pdf_with_mineru
from utils.config import *

def test():
    """测试直接使用公开PDF"""
    
    # 使用MinerU官方示例PDF
    public_pdf = "https://cdn-mineru.openxlab.org.cn/demo/pdf/demo.pdf"
    
    print(f"🔍 测试解析公开PDF: {public_pdf}")
    print(f"🔑 使用API Token: {MINERU_API_TOKEN[:20]}...")
    
    result = parse_pdf_with_mineru(public_pdf)
    
    print(f"✅ 解析结果: {result['success']}")
    if result['success']:
        content = result['markdown_content']
        print(f"📄 内容长度: {len(content)}")
        print(f"📝 前100字符: {content[:100]}...")
    else:
        print(f"❌ 错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    test()