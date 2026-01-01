"""
层级感知文档切分工具类
基于Markdown标题层级进行智能切分，保留上下文信息
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

# 尝试导入LangChain相关模块
try:
    from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain未安装，将使用简化版本的切分器")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkSplitter:
    """
    文档切分器 - 第三步：层级感知切分 (Hierarchy-Aware Chunking)
    基于Markdown标题层级进行智能切分，保留上下文路径
    """
    
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200,
                 headers_to_split_on: Optional[List[Tuple[str, str]]] = None):
        """
        初始化文档切分器
        
        Args:
            chunk_size: 每个chunk的最大字符数
            chunk_overlap: chunk之间的重叠字符数
            headers_to_split_on: 标题层级定义，默认为标准Markdown标题
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 默认标题层级定义
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header 1"),      # 章
            ("##", "Header 2"),     # 节
            ("###", "Header 3"),    # 小节
            ("####", "Header 4"),   # 子小节
        ]
        
        # 初始化LangChain切分器（如果可用）
        if LANGCHAIN_AVAILABLE:
            self.markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on
            )
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            logger.warning("LangChain不可用，使用内置简化切分器")
    
    def split_markdown(self, markdown_path: str, output_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        切分Markdown文档
        
        Args:
            markdown_path: Markdown文件路径
            output_path: 输出文件路径（可选）
            
        Returns:
            List[Dict[str, Any]]: 切分后的chunk列表
        """
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown文件不存在: {markdown_path}")
        
        # 读取Markdown内容
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 执行切分
        chunks = self._split_content(markdown_content)
        
        # 保存结果（如果指定了输出路径）
        if output_path:
            self._save_chunks(chunks, output_path)
        
        logger.info(f"文档切分完成，共生成 {len(chunks)} 个chunks")
        return chunks
    
    def _split_content(self, content: str) -> List[Dict[str, Any]]:
        """
        切分内容
        
        Args:
            content: Markdown内容
            
        Returns:
            List[Dict[str, Any]]: 切分后的chunk列表
        """
        if LANGCHAIN_AVAILABLE:
            return self._split_with_langchain(content)
        else:
            return self._split_with_builtin(content)
    
    def _split_with_langchain(self, content: str) -> List[Dict[str, Any]]:
        """
        使用LangChain进行切分
        
        Args:
            content: Markdown内容
            
        Returns:
            List[Dict[str, Any]]: 切分后的chunk列表
        """
        # 第一步：按标题层级切分
        header_splits = self.markdown_splitter.split_text(content)
        
        # 第二步：对过长的部分进行递归切分
        final_chunks = []
        for split in header_splits:
            if len(split.page_content) > self.chunk_size:
                # 使用递归切分器进一步切分
                sub_splits = self.text_splitter.split_documents([split])
                final_chunks.extend(sub_splits)
            else:
                final_chunks.append(split)
        
        # 转换为统一格式
        result = []
        for i, chunk in enumerate(final_chunks):
            result.append({
                "chunk_id": f"chunk_{i+1:04d}",
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "content_length": len(chunk.page_content),
                "token_estimate": self._estimate_tokens(chunk.page_content)
            })
        
        return result
    
    def _split_with_builtin(self, content: str) -> List[Dict[str, Any]]:
        """
        使用内置切分器（当LangChain不可用时）
        
        Args:
            content: Markdown内容
            
        Returns:
            List[Dict[str, Any]]: 切分后的chunk列表
        """
        # 简化版的切分逻辑
        lines = content.split('\n')
        chunks = []
        current_chunk = ""
        current_metadata = {}
        
        for line in lines:
            # 检测标题
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2)
                
                # 更新metadata
                header_key = f"Header {header_level}"
                current_metadata[header_key] = header_text
                
                # 如果当前chunk不为空且超过大小限制，保存它
                if current_chunk and len(current_chunk) >= self.chunk_size:
                    chunks.append(self._create_builtin_chunk(current_chunk, current_metadata))
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
            else:
                current_chunk += line + "\n"
                
                # 检查是否需要切分
                if len(current_chunk) >= self.chunk_size:
                    # 找到合适的切分点（如段落边界）
                    split_point = self._find_split_point(current_chunk)
                    if split_point > 0:
                        chunk_content = current_chunk[:split_point].strip()
                        chunks.append(self._create_builtin_chunk(chunk_content, current_metadata.copy()))
                        current_chunk = current_chunk[split_point:].strip() + "\n"
        
        # 处理最后一个chunk
        if current_chunk.strip():
            chunks.append(self._create_builtin_chunk(current_chunk, current_metadata))
        
        return chunks
    
    def _find_split_point(self, content: str) -> int:
        """
        找到合适的切分点
        
        Args:
            content: 要切分的内容
            
        Returns:
            int: 切分点位置
        """
        # 寻找最近的段落边界
        paragraph_end = content.rfind('\n\n', 0, self.chunk_size - self.chunk_overlap)
        if paragraph_end > 0:
            return paragraph_end
        
        # 如果没有找到段落边界，寻找句子边界
        sentence_end = max(
            content.rfind('. ', 0, self.chunk_size - self.chunk_overlap),
            content.rfind('。', 0, self.chunk_size - self.chunk_overlap),
            content.rfind('！', 0, self.chunk_size - self.chunk_overlap),
            content.rfind('？', 0, self.chunk_size - self.chunk_overlap)
        )
        if sentence_end > 0:
            return sentence_end + 1
        
        # 最后的选择：在chunk_size - overlap处强制切分
        return self.chunk_size - self.chunk_overlap
    
    def _create_builtin_chunk(self, content: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        创建内置格式的chunk
        
        Args:
            content: chunk内容
            metadata: 元数据
            
        Returns:
            Dict[str, Any]: chunk对象
        """
        return {
            "chunk_id": f"chunk_{hash(content) % 10000:04d}",
            "content": content.strip(),
            "metadata": metadata,
            "content_length": len(content),
            "token_estimate": self._estimate_tokens(content)
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算token数量（简化版本）
        
        Args:
            text: 文本内容
            
        Returns:
            int: 估算的token数量
        """
        # 简单估算：中文字符按1个token计算，英文单词按0.75个token计算
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + int(english_words * 0.75)
    
    def _save_chunks(self, chunks: List[Dict[str, Any]], output_path: str):
        """
        保存chunks到文件
        
        Args:
            chunks: chunk列表
            output_path: 输出文件路径
        """
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Chunks已保存到: {output_path}")
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取chunk统计信息
        
        Args:
            chunks: chunk列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not chunks:
            return {"error": "没有可分析的chunks"}
        
        content_lengths = [chunk["content_length"] for chunk in chunks]
        token_estimates = [chunk["token_estimate"] for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "content_stats": {
                "min_length": min(content_lengths),
                "max_length": max(content_lengths),
                "avg_length": round(sum(content_lengths) / len(content_lengths), 2),
                "total_length": sum(content_lengths)
            },
            "token_stats": {
                "min_tokens": min(token_estimates),
                "max_tokens": max(token_estimates),
                "avg_tokens": round(sum(token_estimates) / len(token_estimates), 2),
                "total_tokens": sum(token_estimates)
            },
            "metadata_coverage": self._analyze_metadata_coverage(chunks)
        }
    
    def _analyze_metadata_coverage(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析元数据覆盖情况
        
        Args:
            chunks: chunk列表
            
        Returns:
            Dict[str, Any]: 元数据覆盖分析
        """
        metadata_keys = set()
        for chunk in chunks:
            metadata_keys.update(chunk.get("metadata", {}).keys())
        
        coverage = {}
        for key in metadata_keys:
            count = sum(1 for chunk in chunks if key in chunk.get("metadata", {}))
            coverage[key] = {
                "count": count,
                "percentage": round(count / len(chunks) * 100, 2)
            }
        
        return coverage
    
    def create_context_aware_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        创建上下文感知的chunks
        
        Args:
            chunks: 原始chunk列表
            
        Returns:
            List[Dict[str, Any]]: 增强后的chunk列表
        """
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            # 构建上下文路径
            metadata = chunk.get("metadata", {})
            context_path = []
            
            # 按层级顺序构建路径
            for level in range(1, 5):
                header_key = f"Header {level}"
                if header_key in metadata:
                    context_path.append(metadata[header_key])
                else:
                    break
            
            # 添加上下文信息到chunk
            enhanced_chunk = chunk.copy()
            enhanced_chunk["context_path"] = " > ".join(context_path)
            enhanced_chunk["context_level"] = len(context_path)
            enhanced_chunk["hierarchy_info"] = {
                "path": context_path,
                "level": len(context_path),
                "chunk_position": i + 1,
                "total_chunks": len(chunks)
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks


# 使用示例
if __name__ == "__main__":
    # 创建切分器实例
    splitter = ChunkSplitter(chunk_size=1000, chunk_overlap=200)
    
    # 示例用法
    try:
        # 切分Markdown文件
        # chunks = splitter.split_markdown("example.md", "chunks.json")
        # print(f"切分完成，共 {len(chunks)} 个chunks")
        
        # 获取统计信息
        # stats = splitter.get_chunk_statistics(chunks)
        # print("统计信息:", stats)
        
        pass
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}")