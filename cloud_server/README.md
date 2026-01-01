# 云服务器部署说明

## 服务器信息
- **公网IP**: 175.24.233.134
- **端口**: 3389
- **上传目录**: /var/uploads/pdf

## 部署步骤

### 1. 上传文件到服务器
```bash
# 复制cloud_server文件夹到服务器
scp -r cloud_server/ root@175.24.233.134:/opt/
```

### 2. 登录服务器部署
```bash
# SSH登录
ssh root@175.24.233.134

# 进入目录
cd /opt/cloud_server

# 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 3. 验证部署
```bash
# 检查服务状态
sudo systemctl status pdf-uploader

# 测试API
curl http://175.24.233.134:3389/api/test
```

## API接口

### 测试服务
```bash
GET http://175.24.233.134:3389/api/test
```

### 上传文件
```bash
POST http://175.24.233.134:3389/api/upload
Content-Type: multipart/form-data
```

### 获取文件
```bash
GET http://175.24.233.134:3389/api/files/<filename>
```

## 管理命令

```bash
# 查看服务状态
sudo systemctl status pdf-uploader

# 重启服务
sudo systemctl restart pdf-uploader

# 查看日志
sudo journalctl -u pdf-uploader -f

# 停止服务
sudo systemctl stop pdf-uploader
```

## 本地测试

在本地运行测试程序：
```bash
python test_connection.py
```

## 文件说明

- `server.py` - Flask服务器主程序
- `requirements.txt` - Python依赖包
- `deploy.sh` - 一键部署脚本
- `test_connection.py` - 本地连接测试程序