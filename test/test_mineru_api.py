"""
测试MinerU API是否能正常工作
"""

import sys
import os
import requests
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import *

def test_mineru_api():
    """测试MinerU API"""
    
    # 使用一个公开可访问的PDF
    test_urls = [
        "https://arxiv.org/pdf/2301.07041.pdf",  # 公开论文
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",  # 简单PDF
    ]
    
    for i, test_url in enumerate(test_urls):
        print(f"\n=== 测试 {i+1}: {test_url} ===")
        
        try:
            # 直接调用MinerU API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MINERU_API_TOKEN}"
            }
            
            # 提交任务
            task_data = {
                "url": test_url,
                "model_version": "vlm",
                "is_ocr": False,
                "enable_formula": True,
                "enable_table": True,
                "language": "ch"
            }
            
            print("📤 提交解析任务...")
            submit_response = requests.post(
                "https://mineru.net/api/v4/extract/task",
                json=task_data,
                headers=headers,
                timeout=30
            )
            
            print(f"提交响应状态码: {submit_response.status_code}")
            print(f"提交响应: {submit_response.text}")
            
            if submit_response.status_code == 200:
                result = submit_response.json()
                if "data" in result and "task_id" in result["data"]:
                    task_id = result["data"]["task_id"]
                    print(f"✅ 任务ID: {task_id}")
                    
                    # 等待完成
                    print("⏳ 等待处理完成...")
                    for attempt in range(5):  # 最多等待5次
                        time.sleep(10)
                        
                        status_response = requests.get(
                            f"https://mineru.net/api/v4/extract/task/{task_id}",
                            headers=headers,
                            timeout=30
                        )
                        
                        print(f"📋 状态检查 {attempt+1}: {status_response.status_code}")
                        if status_response.status_code == 200:
                            status_result = status_response.json()
                            print(f"状态: {status_result.text}")
                            
                            if "data" in status_result:
                                task_status = status_result["data"].get("status")
                                print(f"任务状态: {task_status}")
                                
                                if task_status == "success":
                                    print("✅ 处理成功！")
                                    break
                                elif task_status in ["failed", "error"]:
                                    print("❌ 处理失败！")
                                    break
                        else:
                            print(f"❌ 状态检查失败: {status_response.status_code}")
                            break
                else:
                    print("❌ 提交响应格式错误")
            else:
                print(f"❌ 提交失败: {submit_response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_mineru_api()