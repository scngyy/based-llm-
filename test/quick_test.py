"""
快速测试 - 直接测试API
"""

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_handler import select_and_process_pdf

# 直接调用函数测试
print("快速测试PDF处理...")
result = select_and_process_pdf()
print(f"最终结果: {result}")