"""
简单测试 - 只需要调用一个函数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_handler import select_and_process_pdf

# 只需要调用这一个函数
result = select_and_process_pdf()

print(f"处理结果: {result}")