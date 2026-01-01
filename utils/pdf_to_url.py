"""
PDF转URL工具 - 将本地PDF文件转换为可访问的URL
支持多种上传服务和本地服务器方案
"""

import os
import requests
import logging
import tempfile
import threading
import time
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToURLConverter:
    """PDF转URL转换器"""
    
    def __init__(self, preferred_service: str = "temp.sh"):
        """
        初始化转换器
        
        Args:
            preferred_service: 首选的上传服务
        """
        self.preferred_service = preferred_service
        logger.info(f"PDF转URL转换器已初始化，首选服务: {preferred_service}")
    
    def convert_to_url(self, pdf_path: str, fallback: bool = True) -> Dict[str, Any]:
        """
        将PDF文件转换为URL
        
        Args:
            pdf_path: PDF文件路径
            fallback: 是否使用备用方案
            
        Returns:
            转换结果字典
        """
        try:
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {pdf_path}"
                }
            
            # 检查文件大小
            file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
            logger.info(f"处理PDF文件: {pdf_path}, 大小: {file_size:.2f} MB")
            
            # 尝试各种上传服务
            services = ["temp.sh", "file.io", "0x0.st", "transfer.sh"]
            
            for service in services:
                try:
                    if service == "temp.sh":
                        result = self._upload_to_temp_sh(pdf_path)
                    elif service == "file.io":
                        result = self._upload_to_file_io(pdf_path)
                    elif service == "0x0.st":
                        result = self._upload_to_0x0_st(pdf_path)
                    elif service == "transfer.sh":
                        result = self._upload_to_transfer_sh(pdf_path)
                    
                    if result["success"]:
                        logger.info(f"成功上传到 {service}: {result['url']}")
                        return result
                except Exception as e:
                    logger.warning(f"上传到 {service} 失败: {str(e)}")
                    continue
            
            return {
                "success": False,
                "error": "所有上传服务都失败"
            }
                
        except Exception as e:
            logger.error(f"PDF转URL失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_to_temp_sh(self, pdf_path: str) -> Dict[str, Any]:
        """上传到temp.sh"""
        url = "https://temp.sh/upload"
        
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, files=files, headers=headers, timeout=1200)
            response.raise_for_status()
            
            # 检查响应格式
            response_text = response.text.strip()
            
            if response_text.startswith('http'):
                # 直接返回URL
                return {
                    "success": True,
                    "url": response_text,
                    "service": "temp.sh",
                    "expires_in": "24小时"
                }
            else:
                raise Exception(f"响应格式异常: {response_text[:100]}")
    
    def _upload_to_file_io(self, pdf_path: str) -> Dict[str, Any]:
        """上传到file.io"""
        url = "https://file.io"
        
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {'expires': '1d'}  # 1天过期
            
            response = requests.post(url, files=files, data=data, timeout=600)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                return {
                    "success": True,
                    "url": result['link'],
                    "service": "file.io",
                    "expires_in": "1天"
                }
            else:
                raise Exception(result.get('message', '上传失败'))
    
    def _upload_to_0x0_st(self, pdf_path: str) -> Dict[str, Any]:
        """上传到0x0.st"""
        url = "https://0x0.st"
        
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, files=files, headers=headers, timeout=600)
            response.raise_for_status()
            
            if response.text.startswith('http'):
                return {
                    "success": True,
                    "url": response.text.strip(),
                    "service": "0x0.st",
                    "expires_in": "30天"
                }
            else:
                raise Exception(f"上传失败: {response.text}")
    
    def _upload_to_transfer_sh(self, pdf_path: str) -> Dict[str, Any]:
        """上传到transfer.sh"""
        filename = os.path.basename(pdf_path)
        url = f"https://transfer.sh/{filename}"
        
        with open(pdf_path, 'rb') as f:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.put(url, data=f, headers=headers, timeout=600)
            response.raise_for_status()
            
            if response.text.startswith('http'):
                return {
                    "success": True,
                    "url": response.text.strip(),
                    "service": "transfer.sh",
                    "expires_in": "14天"
                }
            else:
                raise Exception(f"上传失败: {response.text}")
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源")