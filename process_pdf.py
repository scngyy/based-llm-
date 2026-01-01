"""
PDF处理主接口
只需要调用这一个函数
"""

from utils.pdf_handler import select_and_process_pdf

def main():
    """
    主函数 - 一个函数搞定所有
    """
    print("PDF预处理器 - 一键处理")
    print("选择PDF文件后自动处理...")
    print()
    
    # 只需要调用这一个函数
    result = select_and_process_pdf()
    
    print("\n处理完成！")
    return result

if __name__ == "__main__":
    main()