#!/bin/bash

# 云服务器部署脚本
# 服务器: 175.24.233.134:3389

echo "🚀 部署PDF文件上传服务..."
echo "服务器: 175.24.233.134:3389"

# 创建上传目录
echo "📁 创建上传目录..."
sudo mkdir -p /var/uploads/pdf
sudo chmod 755 /var/uploads/pdf
sudo chown $USER:$USER /var/uploads/pdf

# 安装依赖
echo "📦 安装依赖..."
python3 -m pip install "Flask>=1.1.0,<2.3.0"
python3 -m pip install "requests>=2.25.0"

# 配置防火墙
echo "🔥 配置防火墙..."
sudo firewall-cmd --permanent --add-port=3389/tcp
sudo firewall-cmd --reload

# 创建systemd服务
echo "⚙️ 创建系统服务..."
sudo tee /etc/systemd/system/pdf-uploader.service > /dev/null <<EOF
[Unit]
Description=PDF File Uploader Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "🚀 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable pdf-uploader
sudo systemctl start pdf-uploader

# 检查状态
echo "📊 检查服务状态..."
sleep 3
sudo systemctl status pdf-uploader --no-pager

# 测试API
echo "🧪 测试API..."
curl -s http://175.24.233.134:3389/api/test

echo ""
echo "✅ 部署完成！"
echo "🌐 服务地址: http://175.24.233.134:3389"
echo "📋 API接口: http://175.24.233.134:3389/api/test"