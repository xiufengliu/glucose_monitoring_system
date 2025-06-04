# 故障排除指南 (Troubleshooting Guide)

## 常见安装问题

### 1. bcrypt 安装失败

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement bcrypt==4.0.1
ERROR: No matching distribution found for bcrypt==4.0.1
```

**解决方案**:

#### 方案 1: 使用最小依赖
```bash
pip install -r requirements-minimal.txt
```

#### 方案 2: 手动安装 bcrypt
```bash
# 对于 Ubuntu/Debian
sudo apt-get install build-essential libffi-dev python3-dev
pip install bcrypt

# 对于 CentOS/RHEL
sudo yum install gcc openssl-devel libffi-devel python3-devel
pip install bcrypt

# 对于 macOS
brew install libffi
pip install bcrypt

# 对于 Windows
# 确保安装了 Microsoft C++ Build Tools
pip install bcrypt
```

#### 方案 3: 使用预编译版本
```bash
pip install --only-binary=bcrypt bcrypt
```

### 2. cryptography 安装失败

**错误信息**:
```
Failed building wheel for cryptography
```

**解决方案**:
```bash
# 升级 pip 和 setuptools
pip install --upgrade pip setuptools

# 安装系统依赖
# Ubuntu/Debian:
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# CentOS/RHEL:
sudo yum install gcc openssl-devel libffi-devel python3-devel

# 然后重新安装
pip install cryptography
```

### 3. MongoDB 连接问题

**错误信息**:
```
pymongo.errors.ServerSelectionTimeoutError: [Errno 111] Connection refused
```

**解决方案**:

#### 使用 Docker 启动 MongoDB
```bash
docker run -d -p 27017:27017 --name glucose-mongo mongo:6.0
```

#### 检查 MongoDB 状态
```bash
# 检查 MongoDB 是否运行
docker ps | grep mongo

# 查看 MongoDB 日志
docker logs glucose-mongo
```

#### 修改连接配置
编辑 `.env` 文件:
```bash
MONGO_URI=mongodb://localhost:27017/glucose_db
```

### 4. 端口占用问题

**错误信息**:
```
OSError: [Errno 98] Address already in use
```

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5000

# 杀死占用进程
kill -9 <PID>

# 或者使用不同端口
export FLASK_PORT=5001
python run.py
```

### 5. 权限问题

**错误信息**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
```bash
# 给脚本执行权限
chmod +x scripts/setup.sh scripts/test.sh

# 创建日志目录
mkdir -p logs
chmod 755 logs
```

## 环境特定问题

### Python 版本兼容性

**最低要求**: Python 3.8+

**检查版本**:
```bash
python3 --version
```

**升级 Python** (Ubuntu):
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev
```

### 虚拟环境问题

**创建虚拟环境失败**:
```bash
# 确保安装了 venv 模块
sudo apt install python3-venv

# 手动创建虚拟环境
python3 -m venv venv
source venv/bin/activate
```

### Docker 相关问题

#### Docker 未安装
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加用户到 docker 组
sudo usermod -aG docker $USER
```

#### Docker Compose 版本问题
```bash
# 检查版本
docker-compose --version

# 升级 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 快速修复命令

### 完全重新安装
```bash
# 删除虚拟环境
rm -rf venv

# 重新运行安装脚本
./scripts/setup.sh
```

### 使用最小配置运行
```bash
# 创建最小环境文件
cat > .env << EOF
FLASK_CONFIG=development
MONGO_URI=mongodb://localhost:27017/glucose_db
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
EOF

# 安装最小依赖
pip install -r requirements-minimal.txt

# 启动应用
python run.py
```

### 测试安装
```bash
# 测试 Python 导入
python3 -c "
import flask
import pymongo
import marshmallow
import bcrypt
print('所有依赖导入成功!')
"

# 测试应用启动
python3 -c "
from app import create_app
app = create_app('testing')
print('应用创建成功!')
"
```

## 获取帮助

如果以上解决方案都无法解决问题，请：

1. **检查系统信息**:
```bash
python3 --version
pip --version
uname -a
```

2. **收集错误日志**:
```bash
pip install -r requirements.txt > install.log 2>&1
```

3. **创建 Issue**: 在 GitHub 仓库中创建 Issue，包含：
   - 操作系统信息
   - Python 版本
   - 完整的错误信息
   - 已尝试的解决方案

4. **联系支持**: 提供详细的环境信息和错误日志
