#!/usr/bin/env python3
"""
血糖监测云端系统启动入口
Glucose Monitoring Cloud System Entry Point
"""

import os
from app import create_app

# 创建Flask应用实例 - 默认使用开发环境配置
config_name = 'development'  # 可以改为 'testing' 或 'production'
app = create_app(config_name)

if __name__ == '__main__':
    # 服务器配置
    host = '0.0.0.0'
    port = 5000
    debug = True

    print(f"Starting Glucose Monitoring API Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Environment: {config_name}")
    print(f"MongoDB URI: {app.config['MONGO_URI']}")

    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
