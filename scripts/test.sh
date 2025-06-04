#!/bin/bash

# 血糖监测云端系统测试脚本
# Glucose Monitoring Cloud System Test Script

set -e

echo "=== 血糖监测云端系统测试脚本 ==="
echo "=== Glucose Monitoring Cloud System Test Script ==="
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
else
    echo "错误: 未找到虚拟环境，请先运行 scripts/setup.sh"
    exit 1
fi

# 设置测试环境变量
export FLASK_CONFIG=testing
export FLASK_APP=run.py

echo "当前环境: $FLASK_CONFIG"
echo ""

# 运行单元测试
echo "运行单元测试..."
echo "===================="

# 运行所有测试
pytest tests/ -v --tb=short

# 运行测试覆盖率
echo ""
echo "生成测试覆盖率报告..."
echo "========================"
pytest tests/ --cov=app --cov-report=html --cov-report=term

echo ""
echo "测试覆盖率报告已生成到 htmlcov/ 目录"
echo "打开 htmlcov/index.html 查看详细报告"

# 运行代码质量检查
echo ""
echo "运行代码质量检查..."
echo "===================="

# 检查代码格式
echo "检查代码格式 (flake8)..."
flake8 app/ --max-line-length=100 --ignore=E203,W503

# 检查代码风格
echo "检查代码风格 (black)..."
black --check app/ tests/

# 检查导入排序
echo "检查导入排序 (isort)..."
isort --check-only app/ tests/

echo ""
echo "=== 测试完成 ==="
echo ""
echo "如果所有测试都通过，您的应用已准备就绪！"
echo ""
echo "运行应用:"
echo "  python run.py"
echo ""
echo "或使用生产环境:"
echo "  export FLASK_CONFIG=production"
echo "  python run.py"
