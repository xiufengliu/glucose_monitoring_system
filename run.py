"""
血糖监测云端系统启动入口
Glucose Monitoring Cloud System Entry Point
"""

import os
from app import create_app

# 创建Flask应用实例
app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    # 开发环境配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 80))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Glucose Monitoring API Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Environment: {os.getenv('FLASK_CONFIG', 'development')}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
