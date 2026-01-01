"""
PDF智能解析工具类（修复版）
使用MinerU (Magic-PDF) API 将PDF转换为结构化Markdown
"""

import os
import logging
import requests
import time
import json
import zipfile
import io
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """
    PDF解析器 - 第一步：智能解析 (PDF -> Markdown)
    使用MinerU (Magic-PDF) API进行PDF到Markdown的转换
    """
    
    def __init__(self, output_dir: str = "output/markdown", api_token: Optional[str] = None):
        """
        初始化PDF解析器
        
        Args:
            output_dir: Markdown文件输出目录
            api_token: MinerU API Token (可选，也可通过环境变量设置)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # MinerU API配置
        default_token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIyMzYwMDkyMyIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NzE5MTM0NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiNmRmMWZhNmMtMDk2ZC00MGQwLTlmYWYtN2E4M2M3NmNiZjY2IiwiZW1haWwiOiIiLCJleHAiOjE3Njg0MDA5NDZ9.1IpNQ9madLeuqXxB-FjZcNPVhtyl5yy8iZibKRSpH7AaQ6ebgBEbf8E5032kjxaN46KRaF4Xiu36haWZco1ZUA"
        
        self.api_token = api_token or os.getenv("MINERU_API_TOKEN") or default_token
        self.api_base_url = "https://mineru.net/api/v4"
        
        # 检查API Token是否可用
        if self.api_token:
            self.api_available = True
            logger.info("MinerU API已配置")
        else:
            self.api_available = False
            logger.warning("MinerU API Token未配置")
    
    def parse_pdf_to_markdown(self, 
                            pdf_path: str, 
                            output_filename: Optional[str] = None,
                            config: Optional[Dict[str, Any]] = None) -> str:
        """
        将PDF解析为Markdown文件
        
        Args:
            pdf_path: PDF文件路径或URL
            output_filename: 输出Markdown文件名（可选）
            config: 解析配置（可选）
            
        Returns:
            str: 输出的Markdown文件路径
        """
        # 检查输入类型并验证
        is_local_file = os.path.exists(pdf_path)
        is_url = pdf_path.startswith(('http://', 'https://'))
        
        if is_local_file:
            logger.info(f"处理本地PDF文件: {pdf_path}")
            # 本地文件检查
            if not pdf_path.lower().endswith('.pdf'):
                raise ValueError(f"文件格式错误: {pdf_path} 不是PDF文件")
            
            # 重要提示：MinerU API不支持本地文件
            logger.warning("⚠️  重要提醒: MinerU API只支持在线URL，不支持本地文件路径")
            logger.info("🔧 解决方案:")
            logger.info("1. 将PDF上传到云存储获取分享链接")
            logger.info("2. 使用在线PDF进行测试")
            logger.info("3. 使用快速测试工具: python quick_test.py")
            logger.info("4. 使用图形界面工具: python simple_test.py")
            logger.info(f"📝 示例URL: https://cdn-mineru.openxlab.org.cn/demo/example.pdf")
            
        elif is_url:
            logger.info(f"处理在线PDF文件: {pdf_path}")
        else:
            # 既不是本地文件也不是URL
            logger.error(f"无效的输入: {pdf_path}")
            raise ValueError(f"输入必须是本地PDF文件路径或有效的HTTP(S) URL: {pdf_path}")
        
        # 设置默认输出文件名
        if output_filename is None:
            if is_url:
                # 如果是URL，从URL中提取文件名
                parsed_url = urlparse(pdf_path)
                filename = os.path.basename(parsed_url.path) or "downloaded_pdf"
                pdf_name = Path(filename).stem
            else:
                # 如果是本地路径，提取文件名
                pdf_name = Path(pdf_path).stem
            output_filename = f"{pdf_name}.md"
        
        # 防止使用API Token作为文件名
        if len(output_filename) > 100 or '.' not in output_filename or output_filename.startswith('eyJ'):
            output_filename = "parsed_document.md"
        
        output_path = self.output_dir / output_filename
        
        # 默认配置（根据官方API文档）
        default_config = {
            "url": pdf_path,
            "model_version": "vlm",  # vlm 或 pipeline
            "is_ocr": False,  # 是否启动OCR功能
            "enable_formula": True,  # 是否开启公式识别
            "enable_table": True,  # 是否开启表格识别
            "language": "ch"  # 指定文档语言，默认 ch（中文）
        }
        
        # 支持用户自定义配置
        if config:
            # 确保url字段存在
            config["url"] = pdf_path
            default_config.update(config)
        
        try:
            if self.api_available:
                return self._parse_with_mineru_api(pdf_path, output_path, default_config)
            else:
                logger.error("MinerU API不可用，请配置API Token")
                raise ImportError("MinerU API Token未配置")
                
        except Exception as e:
            logger.error(f"PDF解析失败: {str(e)}")
            
            # 如果是URL错误，提供更详细的解决方案
            if "not a valid URL" in str(e):
                logger.error("")
                logger.error("❌ MinerU API错误: 'field url is not a valid URL'")
                logger.error("")
                logger.error("🔧 详细解决方案:")
                logger.error("方案1: 使用在线PDF URL")
                logger.error("  - 将PDF上传到云存储（如：阿里云OSS、腾讯云COS等）")
                logger.error("  - 获取公开访问的URL链接")
                logger.error("  - 使用该URL进行解析")
                logger.error("")
                logger.error("方案2: 使用示例PDF测试")
                logger.error(f"  - 示例URL: https://cdn-mineru.openxlab.org.cn/demo/example.pdf")
                logger.error("")
                logger.error("方案3: 使用快速测试工具")
                logger.error("  - 运行: python quick_test.py")
                logger.error("")
                logger.error("方案4: 使用图形界面工具")
                logger.error("  - 运行: python simple_test.py")
                logger.error("  - 该工具提供更好的本地文件处理指导")
                
            raise
    
    def _parse_with_mineru_api(self, pdf_path: str, output_path: Path, config: Dict[str, Any]) -> str:
        """
        使用MinerU API进行PDF解析
        
        Args:
            pdf_path: PDF文件路径或URL
            output_path: 输出路径
            config: 解析配置
            
        Returns:
            str: 输出文件路径
        """
        logger.info(f"开始使用MinerU API解析PDF: {pdf_path}")
        
        try:
            # 步骤1：提交解析任务
            task_id = self._submit_extraction_task(config)
            
            # 步骤2：等待解析完成并获取结果
            markdown_content = self._wait_for_completion(task_id)
            
            # 步骤3：保存结果到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown文件已保存到: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"MinerU API解析失败: {str(e)}")
            raise
    
    def _submit_extraction_task(self, config: Dict[str, Any]) -> str:
        """
        提交PDF解析任务到MinerU API
        
        Args:
            config: 解析配置
            
        Returns:
            str: 任务ID
        """
        # API端点：提交任务
        url = f"{self.api_base_url}/extract/task"
        
        # 请求头：包含认证信息
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # 发送POST请求提交任务
        response = requests.post(url, headers=headers, json=config, timeout=30)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
        
        # 解析响应
        result = response.json()
        
        # 根据官方文档，检查响应格式
        if result.get("code") != 0:
            raise Exception(f"API返回错误: {result.get('msg', '未知错误')}")
        
        if "data" not in result or "task_id" not in result["data"]:
            raise Exception(f"API响应格式异常: {result}")
        
        task_id = result["data"]["task_id"]
        logger.info(f"任务已提交，任务ID: {task_id}")
        
        return task_id
    
    def _wait_for_completion(self, task_id: str, max_wait_time: int = 600, poll_interval: int = 10) -> str:
        """
        等待PDF解析任务完成
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒，10分钟）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            str: Markdown内容
        """
        # API端点：查询任务状态
        url = f"{self.api_base_url}/extract/task/{task_id}"
        
        # 请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        start_time = time.time()
        attempt = 0
        
        logger.info(f"开始等待任务完成，最大等待时间: {max_wait_time}秒")
        
        while time.time() - start_time < max_wait_time:
            attempt += 1
            elapsed = int(time.time() - start_time)
            
            # 查询任务状态
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"查询失败，状态码: {response.status_code}")
                time.sleep(poll_interval)
                continue
            
            result = response.json()
            
            # 根据官方文档检查响应
            if result.get("code") != 0:
                logger.warning(f"API返回错误: {result.get('msg', '未知错误')}")
                time.sleep(poll_interval)
                continue
            
            if "data" not in result:
                logger.warning(f"响应中无data字段: {result}")
                time.sleep(poll_interval)
                continue
            
            task_data = result["data"]
            state = task_data.get("state", "unknown")
            
            # 根据官方文档，状态值：done, pending, running, failed, converting
            logger.info(f"[{elapsed}s] 尝试 {attempt} - 任务状态: {state}")
            
            if state == "done":
                # 任务成功完成，获取Markdown内容
                if "full_zip_url" in task_data:
                    # API返回压缩包链接，需要下载并解压
                    zip_url = task_data["full_zip_url"]
                    logger.info(f"任务完成，下载解析结果: {zip_url}")
                    
                    # 确保是直接的下载链接，不是页面链接
                    if not zip_url.startswith(('http://', 'https://')):
                        logger.error(f"❌ 无效的下载链接格式: {zip_url}")
                        raise Exception(f"无效的下载链接格式: {zip_url}")
                    
                    markdown_content = self._download_and_extract(zip_url)
                    return markdown_content
                else:
                    logger.warning(f"任务完成但无结果字段: {list(task_data.keys())}")
                    raise Exception("任务完成但未找到解析结果")
                
            elif state == "failed":
                # 任务失败
                error_msg = task_data.get("err_msg", "未知错误")
                logger.error(f"❌ 任务失败: {error_msg}")
                raise Exception(f"任务失败: {error_msg}")
                
            elif state in ["pending", "running", "converting"]:
                # 任务仍在处理中，继续等待
                if state == "running" and "extract_progress" in task_data:
                    progress = task_data["extract_progress"]
                    extracted = progress.get("extracted_pages", 0)
                    total = progress.get("total_pages", 0)
                    logger.info(f"⏳ 解析进度: {extracted}/{total} 页")
                
                logger.info(f"任务处理中，{poll_interval}秒后重试...")
                time.sleep(poll_interval)
                continue
                
            else:
                # 未知状态
                logger.warning(f"⚠️ 未知任务状态: {state}")
                logger.debug(f"完整任务数据: {json.dumps(task_data, indent=2, ensure_ascii=False)}")
                time.sleep(poll_interval)
        
        # 超时
        elapsed = int(time.time() - start_time)
        raise Exception(f"⏰ 任务处理超时，已等待 {elapsed} 秒（最大等待时间: {max_wait_time}秒）")
    
    def _download_and_extract(self, zip_url: str) -> str:
        """
        下载并解压MinerU返回的压缩包
        
        Args:
            zip_url: 压缩包下载链接
            
        Returns:
            str: Markdown内容
        """
        try:
            # 下载压缩包
            logger.info(f"正在下载压缩包: {zip_url}")
            response = requests.get(zip_url, timeout=60)
            response.raise_for_status()
            
            # 解压压缩包
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # 查找Markdown文件
                markdown_files = [f for f in zip_ref.namelist() if f.endswith('.md')]
                
                if not markdown_files:
                    # 如果没有.md文件，查找.txt文件
                    text_files = [f for f in zip_ref.namelist() if f.endswith('.txt')]
                    if text_files:
                        markdown_files = text_files
                
                if not markdown_files:
                    # 列出所有文件用于调试
                    logger.warning(f"压缩包中的文件: {zip_ref.namelist()}")
                    raise Exception("压缩包中未找到Markdown或文本文件")
                
                # 读取第一个Markdown文件
                markdown_file = markdown_files[0]
                with zip_ref.open(markdown_file) as f:
                    content = f.read().decode('utf-8')
                
                logger.info(f"成功解压并读取文件: {markdown_file}")
                return content
                
        except Exception as e:
            logger.error(f"下载或解压失败: {str(e)}")
            raise
    
    def test_api_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.api_available:
            logger.error("API Token未配置")
            return False
        
        try:
            # 使用示例PDF测试API连接
            test_url = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
            
            url = f"{self.api_base_url}/extract/task"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            data = {
                "url": test_url,
                "model_version": "vlm"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0 and "data" in result and "task_id" in result["data"]:
                    logger.info("API连接测试成功")
                    return True
            
            logger.error(f"API连接测试失败，状态码: {response.status_code}")
            return False
                
        except Exception as e:
            logger.error(f"API连接测试异常: {str(e)}")
            return False