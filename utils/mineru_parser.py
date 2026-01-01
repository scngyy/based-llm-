"""
MinerU API官方解析器
按照官方文档实现
"""

import requests
import time
import logging
from typing import Dict, Any
from utils.config import MINERU_API_TOKEN

logger = logging.getLogger(__name__)

class MineruParser:
    """MinerU API解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.api_token = MINERU_API_TOKEN
        self.api_base = "https://mineru.net/api/v4"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
    
    def create_task(self, file_path: str) -> Dict[str, Any]:
        """
        创建解析任务
        
        Args:
            file_path: PDF文件路径或URL
            
        Returns:
            任务创建结果
        """
        try:
            # 创建任务数据
            data = {
                "url": file_path,  # 直接使用URL或文件路径
                "model_version": "vlm",
                "is_ocr": False,
                "enable_formula": True,
                "enable_table": True,
                "language": "ch"
            }
            
            logger.info(f"创建MinerU解析任务: {file_path}")
            
            response = requests.post(
                "https://mineru.net/api/v4/extract/task",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    task_id = result["data"]["task_id"]
                    logger.info(f"任务创建成功: {task_id}")
                    return {
                        "success": True,
                        "task_id": task_id,
                        "message": "任务创建成功"
                    }
                else:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"任务创建失败: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
            else:
                logger.error(f"任务创建HTTP错误: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP错误: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"创建任务异常: {str(e)}")
            return {
                "success": False,
                "error": f"异常: {str(e)}"
            }
    
    def get_task_result(self, task_id: str, max_wait_time: int = 600, poll_interval: int = 10) -> Dict[str, Any]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            任务结果
        """
        try:
            logger.info(f"开始获取任务结果: {task_id}")
            
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                response = requests.get(
                    f"https://mineru.net/api/v4/extract/task/{task_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 0:
                        data = result.get("data", {})
                        state = data.get("state")
                        
                        logger.info(f"任务状态: {state}")
                        
                        if state == "done":
                            full_zip_url = data.get("full_zip_url")
                            logger.info(f"任务完成: {full_zip_url}")
                            
                            # 下载并解析结果
                            return self._download_and_extract_result(full_zip_url)
                            
                        elif state == "failed":
                            err_msg = data.get("err_msg", "解析失败")
                            logger.error(f"任务失败: {err_msg}")
                            return {
                                "success": False,
                                "error": err_msg
                            }
                            
                        elif state in ["pending", "running"]:
                            # 继续等待
                            progress = data.get("extract_progress", {})
                            pages_done = progress.get("extracted_pages", 0)
                            pages_total = progress.get("total_pages", 0)
                            logger.info(f"进度: {pages_done}/{pages_total} 页")
                            
                            time.sleep(poll_interval)
                        else:
                            logger.warning(f"未知状态: {state}")
                            time.sleep(poll_interval)
                    else:
                        logger.error(f"查询结果错误: {result}")
                        return {
                            "success": False,
                            "error": result.get("msg", "未知错误")
                        }
                else:
                    logger.error(f"查询结果HTTP错误: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"HTTP错误: {response.status_code}"
                    }
            
            logger.error("任务超时")
            return {
                "success": False,
                "error": "任务超时"
            }
            
        except Exception as e:
            logger.error(f"获取结果异常: {str(e)}")
            return {
                "success": False,
                "error": f"异常: {str(e)}"
            }
    
    def _download_and_extract_result(self, full_zip_url: str) -> Dict[str, Any]:
        """
        下载并解压结果
        
        Args:
            full_zip_url: 压缩包URL
            
        Returns:
            解析结果
        """
        try:
            logger.info(f"下载结果: {full_zip_url}")
            
            response = requests.get(full_zip_url, timeout=60)
            if response.status_code == 200:
                # 解压zip并读取markdown内容
                import zipfile
                import io
                
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('.md'):
                            with zip_ref.open(file_info) as md_file:
                                markdown_content = md_file.read().decode('utf-8')
                                logger.info(f"Markdown内容长度: {len(markdown_content)}")
                                
                                return {
                                    "success": True,
                                    "markdown_content": markdown_content,
                                    "message": "解析完成"
                                }
            
            logger.error("未找到Markdown文件")
            return {
                "success": False,
                "error": "未找到Markdown文件"
            }
            
        except Exception as e:
            logger.error(f"下载解析异常: {str(e)}")
            return {
                "success": False,
                "error": f"下载解析失败: {str(e)}"
            }

def parse_pdf_with_mineru(file_path: str) -> Dict[str, Any]:
    """
    使用MinerU API解析PDF
    
    Args:
        file_path: PDF文件路径或URL
        
    Returns:
        解析结果
    """
    parser = MineruParser()
    
    # 1. 创建任务
    task_result = parser.create_task(file_path)
    if not task_result["success"]:
        return task_result
    
    # 2. 获取结果
    result = parser.get_task_result(task_result["task_id"])
    
    if result["success"]:
        return {
            "success": True,
            "markdown_content": result["markdown_content"],
            "message": "PDF解析完成"
        }
    else:
        return result