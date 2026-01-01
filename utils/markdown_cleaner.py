"""
Markdown结构化清洗工具类
清理和优化从PDF转换而来的Markdown内容
"""

import re
import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import requests
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkdownCleaner:
    """
    Markdown清洗器 - 第二步：结构化清洗 (Cleaning)
    清理PDF转换产生的噪音，优化文本质量，支持多模态增强
    """
    
    def __init__(self, image_output_dir: str = "output/images"):
        """
        初始化Markdown清洗器
        
        Args:
            image_output_dir: 图片输出目录
        """
        self.image_output_dir = Path(image_output_dir)
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 常见的噪音模式
        self.noise_patterns = [
            r'[_]{2,}',  # 多个下划线
            r'[~]{2,}',  # 多个波浪号
            r'[\s]{3,}',  # 多个空格
            r'\n{3,}',  # 多个换行
            r'page\s*\d+',  # 页码标识（不区分大小写）
            r'第\s*\d+\s*页',  # 中文页码
            r'^\s*[-*+]\s*$',  # 空的列表项
        ]
        
        # 断词连字符模式
        self.hyphen_pattern = re.compile(r'(\w+)-\s*\n\s*(\w+)')
        
        # OCR常见错误模式
        self.ocr_error_patterns = {
            'rn': 'm',  # OCR常见错误
            'vv': 'w',
            'cl': 'd',
            '1i': 'li',
        }
    
    def clean_markdown(self, markdown_path: str, output_path: Optional[str] = None) -> str:
        """
        清洗Markdown文件
        
        Args:
            markdown_path: 输入Markdown文件路径
            output_path: 输出文件路径（可选，默认为原文件名_cleaned.md）
            
        Returns:
            str: 清洗后的文件路径
        """
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown文件不存在: {markdown_path}")
        
        # 读取原文件
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 执行清洗步骤
        cleaned_content = self._apply_cleaning_steps(content)
        
        # 设置输出路径
        if output_path is None:
            input_path = Path(markdown_path)
            output_path = str(input_path.parent / f"{input_path.stem}_cleaned.md")
        
        # 保存清洗后的内容
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        logger.info(f"Markdown清洗完成: {output_path}")
        return output_path
    
    def _apply_cleaning_steps(self, content: str) -> str:
        """
        应用所有清洗步骤
        
        Args:
            content: 原始内容
            
        Returns:
            str: 清洗后的内容
        """
        # 1. 移除无意义字符和噪音
        content = self._remove_noise(content)
        
        # 2. 合并断词
        content = self._fix_hyphenation(content)
        
        # 3. 修复OCR错误
        content = self._fix_ocr_errors(content)
        
        # 4. 标准化空白字符
        content = self._normalize_whitespace(content)
        
        # 5. 修复表格格式
        content = self._fix_table_format(content)
        
        # 6. 修复公式格式
        content = self._fix_formula_format(content)
        
        # 7. 移除重复的空标题
        content = self._remove_empty_headers(content)
        
        return content
    
    def _remove_noise(self, content: str) -> str:
        """移除噪音字符"""
        for pattern in self.noise_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        return content
    
    def _fix_hyphenation(self, content: str) -> str:
        """合并断词"""
        return self.hyphen_pattern.sub(r'\1\2', content)
    
    def _fix_ocr_errors(self, content: str) -> str:
        """修复OCR常见错误"""
        for wrong, correct in self.ocr_error_patterns.items():
            # 使用词边界确保只替换完整单词
            content = re.sub(rf'\b{wrong}\b', correct, content)
        return content
    
    def _normalize_whitespace(self, content: str) -> str:
        """标准化空白字符"""
        # 将多个空格替换为单个空格
        content = re.sub(r' {2,}', ' ', content)
        # 将多个换行替换为最多两个换行
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()
    
    def _fix_table_format(self, content: str) -> str:
        """修复表格格式"""
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检测表格行
            if '|' in line and '-' in line:
                # 找到表格的开始和结束
                table_start = i
                table_end = i
                
                # 向下查找表格结束
                j = i + 1
                while j < len(lines) and '|' in lines[j]:
                    table_end = j
                    j += 1
                
                # 提取表格内容
                table_lines = lines[table_start:table_end + 1]
                fixed_table = self._fix_table_structure(table_lines)
                fixed_lines.extend(fixed_table)
                
                i = table_end + 1
            else:
                fixed_lines.append(lines[i])
                i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_table_structure(self, table_lines: List[str]) -> List[str]:
        """修复表格结构"""
        fixed_lines = []
        
        for line in table_lines:
            if '|' in line:
                # 标准化表格行格式
                cells = [cell.strip() for cell in line.split('|')]
                # 移除首尾的空单元格
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                
                # 重建表格行
                fixed_line = '| ' + ' | '.join(cells) + ' |'
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        return fixed_lines
    
    def _fix_formula_format(self, content: str) -> str:
        """修复公式格式"""
        # 确保公式格式正确
        # 单行公式
        content = re.sub(r'\$([^$]+)\$', r'$\1$', content)
        # 多行公式
        content = re.sub(r'\$\$([^$]+)\$\$', r'$$\n\1\n$$', content)
        return content
    
    def _remove_empty_headers(self, content: str) -> str:
        """移除空的标题"""
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 检测标题行
            if line.startswith('#'):
                # 检查是否为空标题
                header_text = re.sub(r'^#+\s*', '', line).strip()
                if header_text:  # 只保留非空标题
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def extract_images(self, markdown_path: str, describe_with_ai: bool = False) -> Dict[str, str]:
        """
        从Markdown中提取图片信息
        
        Args:
            markdown_path: Markdown文件路径
            describe_with_ai: 是否使用AI生成图片描述
            
        Returns:
            Dict[str, str]: 图片路径到描述的映射
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有图片引用
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        matches = re.findall(image_pattern, content)
        
        image_descriptions = {}
        
        for alt_text, image_path in matches:
            if describe_with_ai:
                # 这里可以集成AI图片描述功能
                description = self._generate_image_description(image_path, alt_text)
            else:
                description = alt_text or f"图片: {image_path}"
            
            image_descriptions[image_path] = description
        
        return image_descriptions
    
    def _generate_image_description(self, image_path: str, alt_text: str) -> str:
        """
        生成图片描述（预留接口）
        
        Args:
            image_path: 图片路径
            alt_text: 原始alt文本
            
        Returns:
            str: 生成的描述
        """
        # 这里可以集成GPT-4V、Qwen-VL等多模态模型
        # 目前返回增强的alt文本
        if alt_text:
            return f"[AI增强] {alt_text}"
        else:
            return "[AI增强] 图片内容描述待生成"
    
    def enhance_images_in_markdown(self, markdown_path: str, image_descriptions: Dict[str, str]) -> str:
        """
        在Markdown中增强图片描述
        
        Args:
            markdown_path: Markdown文件路径
            image_descriptions: 图片描述映射
            
        Returns:
            str: 增强后的Markdown文件路径
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换图片引用
        for image_path, description in image_descriptions.items():
            # 查找并替换图片引用
            pattern = rf'!\[([^\]]*)\]\({re.escape(image_path)}\)'
            replacement = f'![{description}]({image_path})'
            content = re.sub(pattern, replacement, content)
        
        # 保存增强后的文件
        output_path = str(Path(markdown_path).parent / f"{Path(markdown_path).stem}_enhanced.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"图片增强完成: {output_path}")
        return output_path
    
    def get_cleaning_stats(self, original_path: str, cleaned_path: str) -> Dict[str, any]:
        """
        获取清洗统计信息
        
        Args:
            original_path: 原始文件路径
            cleaned_path: 清洗后文件路径
            
        Returns:
            Dict[str, any]: 统计信息
        """
        with open(original_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(cleaned_path, 'r', encoding='utf-8') as f:
            cleaned_content = f.read()
        
        return {
            "original_size": len(original_content),
            "cleaned_size": len(cleaned_content),
            "size_reduction": len(original_content) - len(cleaned_content),
            "size_reduction_percent": round((1 - len(cleaned_content) / len(original_content)) * 100, 2),
            "original_lines": original_content.count('\n') + 1,
            "cleaned_lines": cleaned_content.count('\n') + 1,
            "lines_removed": (original_content.count('\n') + 1) - (cleaned_content.count('\n') + 1)
        }


# 使用示例
if __name__ == "__main__":
    # 创建清洗器实例
    cleaner = MarkdownCleaner()
    
    # 示例用法
    try:
        # 清洗Markdown文件
        # cleaned_path = cleaner.clean_markdown("example.md")
        # print(f"清洗完成: {cleaned_path}")
        
        # 获取统计信息
        # stats = cleaner.get_cleaning_stats("example.md", cleaned_path)
        # print("清洗统计:", stats)
        
        pass
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}")