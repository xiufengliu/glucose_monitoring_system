"""
Flask应用工厂模式
Flask Application Factory Pattern
"""

from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api

# 全局扩展实例
mongo = PyMongo()
jwt = JWTManager()
cors = CORS()


def create_app(config_name='development'):
    """
    应用工厂函数
    Application Factory Function

    Args:
        config_name (str): 配置环境名称 ('development', 'testing', 'production')

    Returns:
        Flask: 配置好的Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    mongo.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # 创建API实例
    api = Api(
        app,
        version='1.0',
        title='血糖监测云端系统 API',
        description='Glucose Monitoring Cloud System RESTful API',
        doc='/docs/',
        prefix='/api'
    )
    
    # 注册蓝图和命名空间
    from app.api.glucose import glucose_ns
    from app.api.users import users_ns
    from app.api.auth import auth_ns
    from app.api.devices import devices_ns
    from app.api.statistics import statistics_ns
    
    api.add_namespace(glucose_ns, path='/glucose')
    api.add_namespace(users_ns, path='/users')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(devices_ns, path='/devices')
    api.add_namespace(statistics_ns, path='/statistics')
    
    # 注册错误处理器
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # 注册健康检查路由
    @app.route('/')
    def health_check():
        """健康检查接口"""
        return {'status': 'ok', 'message': 'Glucose Monitoring API is running'}, 200

    @app.route('/db-status')
    def db_status():
        """数据库连接状态检查"""
        try:
            # 测试MongoDB连接
            mongo.db.command('ping')
            return {
                'status': 'ok',
                'message': 'Database connection successful',
                'database': app.config['MONGO_URI']
            }, 200
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Database connection failed',
                'error': str(e),
                'database': app.config['MONGO_URI']
            }, 500

    @app.route('/test-glucose', methods=['POST'])
    def test_glucose():
        """测试血糖数据接口（不需要数据库）"""
        try:
            from flask import request
            data = request.get_json()

            # 基本验证
            required_fields = ['user_id', 'timestamp', 'glucose_value', 'unit']
            for field in required_fields:
                if field not in data:
                    return {
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }, 400

            # 模拟成功响应
            return {
                'status': 'success',
                'message': '血糖记录创建成功（测试模式）',
                'data': {
                    'id': 'test_id_12345',
                    'user_id': data['user_id'],
                    'timestamp': data['timestamp'],
                    'glucose_value': data['glucose_value'],
                    'unit': data['unit'],
                    'device_id': data.get('device_id'),
                    'note': data.get('note'),
                    'created_at': '2025-06-04T14:30:00Z'
                }
            }, 201

        except Exception as e:
            return {
                'status': 'error',
                'message': 'Test endpoint error',
                'error': str(e)
            }, 500
    
    # 注册CLI命令
    from app.utils.cli import register_cli_commands
    register_cli_commands(app)
    
    return app
