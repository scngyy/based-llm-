#!/usr/bin/env python3
"""
云服务器文件上传服务端点
服务器IP: 175.24.233.134
端口: 3389
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import time
import hashlib
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置 - 已配置为正确的服务器信息
UPLOAD_FOLDER = '/var/uploads/pdf'  # 上传目录
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
SERVER_IP = '175.24.233.134'  # 服务器IP
SERVER_PORT = 3389  # 服务器端口

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_file_id():
    """生成唯一文件ID"""
    return str(uuid.uuid4())

def calculate_file_hash(file_path):
    """计算文件MD5哈希"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/api/test', methods=['GET'])
def test():
    """测试服务状态"""
    return jsonify({
        "success": True,
        "message": "文件上传服务运行正常",
        "timestamp": int(time.time())
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "文件名为空"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "不支持的文件类型"}), 400
        
        # 生成文件ID和保存路径
        file_id = generate_file_id()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        save_filename = f"{file_id}.{file_extension}"
        save_path = os.path.join(UPLOAD_FOLDER, save_filename)
        
        # 保存文件
        file.save(save_path)
        
        # 计算文件哈希
        file_hash = calculate_file_hash(save_path)
        
        # 构建访问URL
        server_url = f"http://{SERVER_IP}:{SERVER_PORT}/api/files/{save_filename}"
        
        logger.info(f"文件上传成功: {file.filename} -> {save_filename}")
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "url": server_url,
            "file_hash": file_hash,
            "upload_time": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({"success": False, "error": f"上传失败: {str(e)}"}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    """获取文件"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"success": False, "error": "文件不存在"}), 404

@app.route('/api/status/<file_id>', methods=['GET'])
def check_status(file_id):
    """检查文件状态"""
    try:
        # 查找文件
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(file_id):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    return jsonify({
                        "success": True,
                        "file_id": file_id,
                        "exists": True,
                        "size": os.path.getsize(file_path),
                        "url": f"http://{SERVER_IP}:{SERVER_PORT}/api/files/{filename}"
                    })
        
        return jsonify({"success": False, "error": "文件不存在"}), 404
        
    except Exception as e:
        logger.error(f"检查文件状态失败: {str(e)}")
        return jsonify({"success": False, "error": f"检查失败: {str(e)}"}), 500

@app.route('/api/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    try:
        # 查找并删除文件
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(file_id):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"文件删除成功: {file_id}")
                    return jsonify({
                        "success": True,
                        "message": "文件删除成功",
                        "file_id": file_id
                    })
        
        return jsonify({"success": False, "error": "文件不存在"}), 404
        
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return jsonify({"success": False, "error": f"删除失败: {str(e)}"}), 500

@app.route('/api/list', methods=['GET'])
def list_files():
    """列出所有文件"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_id = filename.rsplit('.', 1)[0]
                files.append({
                    "file_id": file_id,
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "url": f"http://{SERVER_IP}:{SERVER_PORT}/api/files/{filename}",
                    "upload_time": os.path.getctime(file_path)
                })
        
        return jsonify({
            "success": True,
            "files": files,
            "total_count": len(files)
        })
        
    except Exception as e:
        logger.error(f"列出文件失败: {str(e)}")
        return jsonify({"success": False, "error": f"列出失败: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    """文件过大处理"""
    return jsonify({"success": False, "error": "文件过大，最大允许200MB"}), 413

@app.errorhandler(404)
def not_found(e):
    """404处理"""
    return jsonify({"success": False, "error": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(e):
    """500处理"""
    logger.error(f"服务器内部错误: {str(e)}")
    return jsonify({"success": False, "error": "服务器内部错误"}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 启动文件上传服务...")
    print(f"📁 上传目录: {UPLOAD_FOLDER}")
    print(f"🌐 服务器地址: http://{SERVER_IP}:{SERVER_PORT}")
    print("📋 可用接口:")
    print(f"   - GET  http://{SERVER_IP}:{SERVER_PORT}/api/test")
    print(f"   - POST http://{SERVER_IP}:{SERVER_PORT}/api/upload")
    print(f"   - GET  http://{SERVER_IP}:{SERVER_PORT}/api/files/<filename>")
    print(f"   - GET  http://{SERVER_IP}:{SERVER_PORT}/api/status/<file_id>")
    print(f"   - DELETE http://{SERVER_IP}:{SERVER_PORT}/api/delete/<file_id>")
    print(f"   - GET  http://{SERVER_IP}:{SERVER_PORT}/api/list")
    print("="*60)
    
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False)