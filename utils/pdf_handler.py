"""
PDF处理统一接口
一个函数完成选择PDF和处理
"""

import os
import sys
import requests
import tkinter as tk
from tkinter import filedialog
from utils.config import *

# 添加utils目录到路径
utils_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, utils_dir)

def upload_to_own_cloud_server(pdf_path):
    """
    上传PDF到自己的云服务器
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        dict: 上传结果
    """
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(
                f"{CLOUD_SERVER_URL}/api/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # 使用服务器返回的实际URL
                return {
                    "success": True,
                    "url": result.get("url", "")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "上传失败")
                }
        else:
            return {
                "success": False,
                "error": f"HTTP错误: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"上传异常: {str(e)}"
        }

try:
    import pdf_to_url
    import pdf_parser
    import markdown_cleaner
    import chunk_splitter
    import prompt_builder
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保utils文件夹包含所有必需的处理模块")

def select_and_process_pdf():
    """
    一个函数完成：选择PDF文件并处理
    
    Returns:
        dict: 处理结果
    """
    # 创建隐藏的root窗口用于文件选择
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 选择PDF文件
    print("请选择PDF文件...")
    file_path = filedialog.askopenfilename(
        title="选择PDF文件",
        filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
    )
    
    root.destroy()  # 销毁窗口
    
    if not file_path:
        return {
            "success": False,
            "message": "未选择文件"
        }
    
    if not os.path.exists(file_path):
        return {
            "success": False,
            "message": f"文件不存在: {file_path}"
        }
    
    print(f"选择的文件: {file_path}")
    
    try:
        import time
        start_time = time.time()
        
        # 步骤1: PDF转URL（上传到自己的云服务器）
        print("步骤1: 上传PDF到云服务器...")
        if USE_OWN_CLOUD_SERVER:
            # 使用自己的云服务器
            import requests
            url_result = upload_to_own_cloud_server(file_path)
        else:
            # 使用第三方服务
            converter = pdf_to_url.PDFToURLConverter()
            url_result = converter.convert_to_url(file_path)
        
        if not url_result.get("success", False):
            return {
                "success": False,
                "message": f"PDF转URL失败: {url_result.get('error', '未知错误')}"
            }
        
        pdf_url = url_result["url"]
        print(f"✅ PDF URL: {pdf_url}")
        
        # 步骤2: PDF解析
        print("步骤2: 解析PDF...")
        parser = pdf_parser.PDFParser(OUTPUT_DIR, MINERU_API_TOKEN)
        
        try:
            # 直接调用API解析方法
            markdown_file_path = parser.parse_pdf_to_markdown(pdf_url)
            
            # 读取解析结果
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                
            print(f"✅ 解析完成，内容长度: {len(markdown_content)}")
            
        except Exception as e:
            return {
                "success": False,
                "message": f"PDF解析失败: {str(e)}"
            }
        
        # 步骤3: Markdown清洗
        if ENABLE_CLEANING:
            print("步骤3: 清洗Markdown...")
            cleaner = markdown_cleaner.MarkdownCleaner()
            
            # 创建临时文件进行清洗
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(markdown_content)
                temp_file_path = temp_file.name
            
            try:
                # 清洗文件
                cleaned_file_path = cleaner.clean_markdown(temp_file_path)
                
                # 读取清洗后的内容
                with open(cleaned_file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                print("✅ 清洗完成")
            except Exception as e:
                print(f"⚠️ 清洗失败，使用原始内容: {str(e)}")
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                # 删除清洗后的临时文件（如果存在）
                if 'cleaned_file_path' in locals() and os.path.exists(cleaned_file_path):
                    os.unlink(cleaned_file_path)
        
        # 步骤4: 内容切分
        chunks = []
        if ENABLE_SPLITTING:
            print("步骤4: 切分内容...")
            splitter = chunk_splitter.ChunkSplitter(CHUNK_SIZE, CHUNK_OVERLAP)
            split_result = splitter.split_content(markdown_content, {})
            
            if split_result.get("success", False):
                chunks = split_result["chunks"]
                print(f"✅ 切分完成，生成 {len(chunks)} 个块")
            else:
                print(f"⚠️ 切分失败，使用完整内容: {split_result.get('error', '未知错误')}")
                chunks = [{"content": markdown_content, "index": 0}]
        else:
            chunks = [{"content": markdown_content, "index": 0}]
        
        # 步骤5: Prompt构建
        prompts = []
        if ENABLE_PROMPT_BUILDING:
            print("步骤5: 构建Prompt...")
            builder = prompt_builder.PromptBuilder(MAX_CONTEXT_LENGTH)
            prompt_result = builder.build_prompts(chunks, "")
            
            if prompt_result.get("success", False):
                prompts = prompt_result["prompts"]
                print(f"✅ Prompt构建完成，生成 {len(prompts)} 个prompt")
            else:
                print(f"⚠️ Prompt构建失败，使用原始内容: {prompt_result.get('error', '未知错误')}")
                prompts = [{"content": markdown_content, "type": "raw"}]
        
        processing_time = time.time() - start_time
        
        print(f"\n🎉 PDF处理完成！耗时: {processing_time:.2f}秒")
        
        return {
            "success": True,
            "message": "PDF处理完成",
            "data": {
                "file_path": file_path,
                "pdf_url": pdf_url,
                "markdown_content": markdown_content,
                "chunks": chunks,
                "prompts": prompts,
                "processing_time": processing_time,
                "output_dir": OUTPUT_DIR
            }
        }
        
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg
        }