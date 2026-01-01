"""
Prompt上下文构建工具类
为知识抽取构建包含层级上下文的Prompt
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptBuilder:
    """
    Prompt构建器 - 第四步：构建Prompt上下文 (Prompt Context Building)
    为LLM知识抽取任务构建包含完整层级上下文的Prompt
    """
    
    def __init__(self, template_type: str = "knowledge_extraction"):
        """
        初始化Prompt构建器
        
        Args:
            template_type: Prompt模板类型
        """
        self.template_type = template_type
        
        # 预定义的Prompt模板
        self.templates = {
            "knowledge_extraction": self._get_knowledge_extraction_template(),
            "entity_relation": self._get_entity_relation_template(),
            "concept_understanding": self._get_concept_understanding_template(),
            "qa_generation": self._get_qa_generation_template(),
            "summarization": self._get_summarization_template()
        }
        
        # 当前模板
        self.current_template = self.templates.get(template_type, self.templates["knowledge_extraction"])
    
    def build_context_prompt(self, 
                           chunk: Dict[str, Any], 
                           task_description: Optional[str] = None,
                           additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        为单个chunk构建包含上下文的Prompt
        
        Args:
            chunk: 包含内容和元数据的chunk
            task_description: 任务描述（可选）
            additional_context: 额外上下文信息（可选）
            
        Returns:
            str: 构建好的Prompt
        """
        # 提取基本信息
        content = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        context_path = chunk.get("context_path", "")
        
        # 构建上下文部分
        context_section = self._build_context_section(chunk)
        
        # 构建任务描述部分
        task_section = self._build_task_section(task_description, additional_context)
        
        # 构建内容部分
        content_section = self._build_content_section(content)
        
        # 组装完整的Prompt
        prompt = self.current_template.format(
            context=context_section,
            task_description=task_section,
            content=content_section
        )
        
        return prompt
    
    def build_batch_prompts(self, 
                          chunks: List[Dict[str, Any]], 
                          task_description: Optional[str] = None,
                          additional_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        批量构建Prompt
        
        Args:
            chunks: chunk列表
            task_description: 任务描述（可选）
            additional_context: 额外上下文信息（可选）
            
        Returns:
            List[Dict[str, Any]]: 包含prompt和原始chunk信息的列表
        """
        prompts = []
        
        for i, chunk in enumerate(chunks):
            try:
                prompt = self.build_context_prompt(chunk, task_description, additional_context)
                
                prompt_info = {
                    "prompt_id": f"prompt_{i+1:04d}",
                    "chunk_id": chunk.get("chunk_id", f"chunk_{i+1:04d}"),
                    "prompt": prompt,
                    "prompt_length": len(prompt),
                    "token_estimate": self._estimate_tokens(prompt),
                    "original_chunk": chunk,
                    "metadata": {
                        "context_path": chunk.get("context_path", ""),
                        "content_length": chunk.get("content_length", 0),
                        "hierarchy_level": chunk.get("context_level", 0)
                    }
                }
                
                prompts.append(prompt_info)
                
            except Exception as e:
                logger.error(f"构建Prompt失败 (chunk {i+1}): {str(e)}")
                continue
        
        logger.info(f"成功构建 {len(prompts)} 个Prompts")
        return prompts
    
    def _build_context_section(self, chunk: Dict[str, Any]) -> str:
        """
        构建上下文部分
        
        Args:
            chunk: chunk信息
            
        Returns:
            str: 上下文部分文本
        """
        metadata = chunk.get("metadata", {})
        context_path = chunk.get("context_path", "")
        hierarchy_info = chunk.get("hierarchy_info", {})
        
        context_parts = []
        
        # 层级路径
        if context_path:
            context_parts.append(f"📍 文档层级路径: {context_path}")
        
        # 详细层级信息
        if hierarchy_info:
            path = hierarchy_info.get("path", [])
            level = hierarchy_info.get("level", 0)
            position = hierarchy_info.get("chunk_position", 0)
            total = hierarchy_info.get("total_chunks", 0)
            
            context_parts.append(f"📚 所属层级: 第{level}级")
            context_parts.append(f"📖 文档位置: 第{position}块，共{total}块")
            
            # 具体的标题信息
            for i, title in enumerate(path):
                context_parts.append(f"{'  ' * i}🏷️  {title}")
        
        # 额外的元数据
        for key, value in metadata.items():
            if key.startswith("Header ") and value:
                context_parts.append(f"📋 {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else "无特定上下文信息"
    
    def _build_task_section(self, task_description: Optional[str], additional_context: Optional[Dict[str, Any]]) -> str:
        """
        构建任务描述部分
        
        Args:
            task_description: 任务描述
            additional_context: 额外上下文
            
        Returns:
            str: 任务描述部分文本
        """
        if task_description:
            return task_description
        
        # 默认任务描述
        default_tasks = {
            "knowledge_extraction": "请基于上述上下文，从文本内容中提取知识点、实体和关系。重点关注：\n1. 核心概念定义\n2. 实体间的层次关系\n3. 属性和特征\n4. 过程和方法\n请以结构化的格式输出提取结果。",
            "entity_relation": "请从文本中识别实体和它们之间的关系，包括：\n1. 实体类型（概念、人物、地点、时间等）\n2. 实体属性\n3. 实体间的关系（属于、包含、依赖、因果等）\n请以三元组形式输出：(主体, 关系, 客体)。",
            "concept_understanding": "请深入理解文本中的核心概念，并解释：\n1. 概念的定义和内涵\n2. 概念的外延和实例\n3. 与其他概念的关系\n4. 在整个知识体系中的位置",
            "qa_generation": "基于文本内容和上下文，生成高质量的问题和答案对：\n1. 事实性问题\n2. 理解性问题\n3. 应用性问题\n4. 分析性问题\n请确保答案能在文本中找到依据。",
            "summarization": "请为这段文本生成一个简洁准确的摘要，突出：\n1. 主要观点\n2. 关键信息\n3. 与上下文的关联\n4. 重要细节"
        }
        
        task = default_tasks.get(self.template_type, default_tasks["knowledge_extraction"])
        
        # 添加额外上下文
        if additional_context:
            extra_info = "\n\n额外信息:\n"
            for key, value in additional_context.items():
                extra_info += f"- {key}: {value}\n"
            task += extra_info
        
        return task
    
    def _build_content_section(self, content: str) -> str:
        """
        构建内容部分
        
        Args:
            content: 原始内容
            
        Returns:
            str: 格式化的内容部分
        """
        if not content:
            return "无内容"
        
        # 简单的内容格式化
        formatted_content = content.strip()
        
        # 如果内容太长，进行截断提示
        if len(formatted_content) > 8000:
            formatted_content = formatted_content[:8000] + "\n\n[注意：内容已截断，完整内容请参考原始文档]"
        
        return formatted_content
    
    def _get_knowledge_extraction_template(self) -> str:
        """知识抽取模板"""
        return """# 知识抽取任务

## 📋 上下文信息
{context}

## 🎯 任务描述
{task_description}

## 📄 文本内容
```
{content}
```

## 💬 输出要求
请基于以上信息进行知识抽取，输出格式要求：
1. 结构清晰，层次分明
2. 包含实体、关系、属性
3. 标注信息来源和置信度
4. 保持JSON格式便于后续处理

请开始分析：
"""
    
    def _get_entity_relation_template(self) -> str:
        """实体关系抽取模板"""
        return """# 实体关系抽取任务

## 📋 上下文信息
{context}

## 🎯 任务描述
{task_description}

## 📄 文本内容
```
{content}
```

## 💬 输出要求
请以以下格式输出实体关系：
```json
{
  "entities": [
    {"id": "E1", "type": "概念", "name": "实体名称", "attributes": {...}},
    ...
  ],
  "relations": [
    {"subject": "E1", "predicate": "关系类型", "object": "E2", "confidence": 0.9},
    ...
  ]
}
```

请开始分析：
"""
    
    def _get_concept_understanding_template(self) -> str:
        """概念理解模板"""
        return """# 概念理解任务

## 📋 上下文信息
{context}

## 🎯 任务描述
{task_description}

## 📄 文本内容
```
{content}
```

## 💬 输出要求
请详细解释概念理解结果：
1. 核心概念定义
2. 概念特征和属性
3. 与其他概念的关系
4. 实际应用场景

请开始分析：
"""
    
    def _get_qa_generation_template(self) -> str:
        """问答生成模板"""
        return """# 问答生成任务

## 📋 上下文信息
{context}

## 🎯 任务描述
{task_description}

## 📄 文本内容
```
{content}
```

## 💬 输出要求
请生成以下格式的问答对：
```json
{
  "qa_pairs": [
    {
      "question": "问题内容",
      "answer": "答案内容",
      "type": "事实性/理解性/应用性/分析性",
      "difficulty": "简单/中等/困难"
    }
  ]
}
```

请开始生成：
"""
    
    def _get_summarization_template(self) -> str:
        """摘要生成模板"""
        return """# 文本摘要任务

## 📋 上下文信息
{context}

## 🎯 任务描述
{task_description}

## 📄 文本内容
```
{content}
```

## 💬 输出要求
请生成结构化摘要：
1. 主要观点总结
2. 关键信息提取
3. 与上下文的关联
4. 重要结论

请开始摘要：
"""
    
    def set_template_type(self, template_type: str):
        """
        设置模板类型
        
        Args:
            template_type: 模板类型
        """
        if template_type in self.templates:
            self.template_type = template_type
            self.current_template = self.templates[template_type]
            logger.info(f"已切换到模板类型: {template_type}")
        else:
            logger.error(f"未知的模板类型: {template_type}")
    
    def save_prompts(self, prompts: List[Dict[str, Any]], output_path: str):
        """
        保存prompts到文件
        
        Args:
            prompts: prompt列表
            output_path: 输出文件路径
        """
        # 准备保存的数据
        save_data = {
            "metadata": {
                "total_prompts": len(prompts),
                "template_type": self.template_type,
                "created_at": str(Path().absolute()),
                "total_tokens": sum(p["token_estimate"] for p in prompts)
            },
            "prompts": prompts
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Prompts已保存到: {output_path}")
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算token数量
        
        Args:
            text: 文本内容
            
        Returns:
            int: 估算的token数量
        """
        # 简单的token估算
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + int(english_words * 0.75)
    
    def get_prompt_statistics(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取prompt统计信息
        
        Args:
            prompts: prompt列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not prompts:
            return {"error": "没有可分析的prompts"}
        
        prompt_lengths = [p["prompt_length"] for p in prompts]
        token_estimates = [p["token_estimate"] for p in prompts]
        
        return {
            "total_prompts": len(prompts),
            "length_stats": {
                "min_length": min(prompt_lengths),
                "max_length": max(prompt_lengths),
                "avg_length": round(sum(prompt_lengths) / len(prompt_lengths), 2),
                "total_length": sum(prompt_lengths)
            },
            "token_stats": {
                "min_tokens": min(token_estimates),
                "max_tokens": max(token_estimates),
                "avg_tokens": round(sum(token_estimates) / len(token_estimates), 2),
                "total_tokens": sum(token_estimates)
            },
            "context_coverage": self._analyze_context_coverage(prompts)
        }
    
    def _analyze_context_coverage(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析上下文覆盖情况
        
        Args:
            prompts: prompt列表
            
        Returns:
            Dict[str, Any]: 上下文覆盖分析
        """
        hierarchy_levels = [p["metadata"]["hierarchy_level"] for p in prompts]
        
        return {
            "level_distribution": {
                f"level_{level}": hierarchy_levels.count(level) 
                for level in set(hierarchy_levels)
            },
            "with_context_path": sum(1 for p in prompts if p["metadata"]["context_path"]),
            "avg_hierarchy_level": round(sum(hierarchy_levels) / len(hierarchy_levels), 2)
        }


# 使用示例
if __name__ == "__main__":
    # 创建Prompt构建器
    builder = PromptBuilder(template_type="knowledge_extraction")
    
    # 示例用法
    try:
        # 示例chunk
        example_chunk = {
            "chunk_id": "chunk_0001",
            "content": "神经网络是一种模仿人脑结构的计算模型...",
            "metadata": {
                "Header 1": "第一章 深度学习基础",
                "Header 2": "1.1 神经网络概念"
            },
            "context_path": "第一章 深度学习基础 > 1.1 神经网络概念",
            "context_level": 2
        }
        
        # 构建prompt
        # prompt = builder.build_context_prompt(example_chunk)
        # print("构建的Prompt:")
        # print(prompt)
        
        pass
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}")