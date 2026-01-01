"""
测试PDF处理函数
测试一个函数完成选择PDF和处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_handler import select_and_process_pdf

def test():
    """测试PDF处理函数"""
    print("=" * 60)
    print("PDF处理器测试")
    print("=" * 60)
    print()
    
    # 调用一个函数完成选择PDF和处理
    result = select_and_process_pdf()
    
    print("\n" + "=" * 60)
    print("处理结果")
    print("=" * 60)
    
    if result["success"]:
        print("✅ 处理成功!")
        print(f"📝 消息: {result['message']}")
        
        data = result["data"]
        print(f"\n📊 处理统计:")
        print(f"   文件路径: {data['file_path']}")
        print(f"   PDF URL: {data['pdf_url']}")
        print(f"   Markdown长度: {len(data['markdown_content'])} 字符")
        print(f"   分块数量: {len(data['chunks'])} 个")
        print(f"   Prompt数量: {len(data['prompts'])} 个")
        print(f"   处理时间: {data['processing_time']:.2f} 秒")
        print(f"   输出目录: {data['output_dir']}")
        
        # 显示前100个字符的内容示例
        if data['markdown_content']:
            print(f"\n📄 内容示例 (前100字符):")
            print(f"   {data['markdown_content'][:100]}...")
        
        # 显示第一个分块
        if data['chunks']:
            print(f"\n🔢 第一个分块示例 (前100字符):")
            chunk_content = data['chunks'][0].get('content', '')
            print(f"   {chunk_content[:100]}...")
        
        # 显示第一个Prompt
        if data['prompts']:
            print(f"\n💬 第一个Prompt示例 (前100字符):")
            prompt_content = data['prompts'][0].get('content', '')
            print(f"   {prompt_content[:100]}...")
        
    else:
        print("❌ 处理失败!")
        print(f"📝 错误信息: {result['message']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test()