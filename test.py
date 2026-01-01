"""
测试PDF预处理
只需要调用一个函数
"""

from utils.pdf_processor import process_pdf_file

def test():
    # 替换为你的PDF文件路径
    pdf_path = "test_document.pdf"
    
    print("开始测试PDF处理...")
    result = process_pdf_file(pdf_path)
    
    if result["success"]:
        print("✅ 处理成功!")
        data = result["data"]
        print(f"Markdown长度: {len(data['markdown_content'])}")
        print(f"分块数量: {len(data['chunks'])}")
        print(f"Prompt数量: {len(data['prompts'])}")
        print(f"处理时间: {data['processing_time']:.2f}秒")
    else:
        print(f"❌ 处理失败: {result['message']}")

if __name__ == "__main__":
    test()