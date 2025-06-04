#!/bin/bash

# 血糖监测云端系统安装脚本
# Glucose Monitoring Cloud System Setup Script

set -e

echo "=== 血糖监测云端系统安装脚本 ==="
echo "=== Glucose Monitoring Cloud System Setup ==="
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 检查是否安装了pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip"
    exit 1
fi

# 创建虚拟环境
echo "创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "虚拟环境创建完成"
else
    echo "虚拟环境已存在"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装Python依赖包..."
if pip install -r requirements.txt; then
    echo "依赖安装成功"
else
    echo "标准依赖安装失败，尝试使用最小依赖..."
    pip install -r requirements-minimal.txt
    echo "最小依赖安装完成"
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs
mkdir -p uploads
mkdir -p docker/mongodb/init

# 复制环境配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置您的环境变量"
else
    echo "环境配置文件已存在"
fi

# 检查MongoDB连接
echo "检查MongoDB连接..."
if command -v mongosh &> /dev/null; then
    if mongosh --eval "db.runCommand('ping')" --quiet; then
        echo "MongoDB连接正常"
    else
        echo "警告: MongoDB连接失败，请确保MongoDB服务正在运行"
        echo "您可以使用以下命令启动MongoDB:"
        echo "  docker run -d -p 27017:27017 --name glucose-mongo mongo:6.0"
    fi
elif command -v mongo &> /dev/null; then
    if mongo --eval "db.runCommand('ping')" --quiet; then
        echo "MongoDB连接正常"
    else
        echo "警告: MongoDB连接失败，请确保MongoDB服务正在运行"
    fi
else
    echo "警告: 未找到MongoDB客户端，无法测试连接"
    echo "请确保MongoDB服务正在运行在 localhost:27017"
fi

# 初始化数据库
echo "初始化数据库..."
export FLASK_APP=run.py
flask init-db

echo ""
echo "=== 安装完成 ==="
echo ""
echo "下一步操作:"
echo "1. 编辑 .env 文件配置您的环境变量"
echo "2. 启动MongoDB服务 (如果尚未启动)"
echo "3. 运行应用:"
echo "   python run.py"
echo ""
echo "或使用Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo "API文档地址: http://localhost:5000/docs"
echo "健康检查地址: http://localhost:5000/"
echo ""
echo "创建管理员用户:"
echo "   flask create-admin"
echo ""
echo "查看系统统计:"
echo "   flask show-stats"
echo ""
echo "安装完成！"
