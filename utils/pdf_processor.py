"""
PDF预处理器统一函数
调用四个处理步骤完成PDF处理
"""

import os
import time
from .config import *
from . import pdf_to_url
from . import pdf_parser
from . import markdown_cleaner
from . import chunk_splitter
from . import prompt_builder

def process_pdf_file(pdf_file_path):
    """
    处理PDF文件的统一函数
    
    Args:
        pdf_file_path: PDF文件路径
        
    Returns:
        dict: 处理结果
    """
    try:
        start_time = time.time()
        
        # 检查文件是否存在
        if not os.path.exists(pdf_file_path):
            return {
                "success": False,
                "message": f"文件不存在: {pdf_file_path}"
            }
        
        print(f"开始处理PDF: {pdf_file_path}")
        
        # 步骤1: PDF转URL
        print("步骤1: 转换PDF为URL...")
        converter = pdf_to_url.PDFToURLConverter()
        url_result = converter.convert_to_url(pdf_file_path)
        
        if not url_result["success"]:
            return {
                "success": False,
                "message": f"PDF转URL失败: {url_result['error']}"
            }
        
        pdf_url = url_result["url"]
        print(f"PDF URL: {pdf_url}")
        
        # 步骤2: PDF解析
        print("步骤2: 解析PDF...")
        parser = pdf_parser.PDFParser(MINERU_API_TOKEN)
        parse_result = parser.parse_pdf_to_markdown(pdf_url, OUTPUT_DIR)
        
        if not parse_result["success"]:
            return {
                "success": False,
                "message": f"PDF解析失败: {parse_result['error']}"
            }
        
        markdown_content = parse_result["markdown_content"]
        print(f"解析完成，内容长度: {len(markdown_content)}")
        
        # 步骤3: Markdown清洗
        if ENABLE_CLEANING:
            print("步骤3: 清洗Markdown...")
            cleaner = markdown_cleaner.MarkdownCleaner()
            clean_result = cleaner.clean_markdown(markdown_content)
            
            if clean_result["success"]:
                markdown_content = clean_result["cleaned_content"]
                print("清洗完成")
            else:
                print(f"清洗失败: {clean_result['error']}")
        
        # 步骤4: 内容切分
        chunks = []
        if ENABLE_SPLITTING:
            print("步骤4: 切分内容...")
            splitter = chunk_splitter.ChunkSplitter(CHUNK_SIZE, CHUNK_OVERLAP)
            split_result = splitter.split_content(markdown_content, {})
            
            if split_result["success"]:
                chunks = split_result["chunks"]
                print(f"切分完成，生成 {len(chunks)} 个块")
            else:
                print(f"切分失败: {split_result['error']}")
                chunks = [{"content": markdown_content, "index": 0}]
        else:
            chunks = [{"content": markdown_content, "index": 0}]
        
        # 步骤5: Prompt构建
        prompts = []
        if ENABLE_PROMPT_BUILDING:
            print("步骤5: 构建Prompt...")
            builder = prompt_builder.PromptBuilder(MAX_CONTEXT_LENGTH)
            prompt_result = builder.build_prompts(chunks, "")
            
            if prompt_result["success"]:
                prompts = prompt_result["prompts"]
                print(f"Prompt构建完成，生成 {len(prompts)} 个prompt")
            else:
                print(f"Prompt构建失败: {prompt_result['error']}")
                prompts = [{"content": markdown_content, "type": "raw"}]
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": "PDF处理完成",
            "data": {
                "pdf_url": pdf_url,
                "markdown_content": markdown_content,
                "chunks": chunks,
                "prompts": prompts,
                "processing_time": processing_time,
                "output_dir": OUTPUT_DIR
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"处理过程中发生错误: {str(e)}"
        }