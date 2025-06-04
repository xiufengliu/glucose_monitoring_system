"""
pytest配置文件
pytest Configuration File
"""

import pytest
from app import create_app, mongo


@pytest.fixture
def app():
    """创建测试应用实例"""
    app = create_app('testing')
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建CLI测试运行器"""
    return app.test_cli_runner()


@pytest.fixture
def clean_db(app):
    """清理测试数据库"""
    with app.app_context():
        # 清空所有集合
        mongo.db.users.delete_many({})
        mongo.db.devices.delete_many({})
        mongo.db.glucose_records.delete_many({})
        
        yield
        
        # 测试后清理
        mongo.db.users.delete_many({})
        mongo.db.devices.delete_many({})
        mongo.db.glucose_records.delete_many({})


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'full_name': '测试用户',
        'age': 30,
        'gender': 'male'
    }


@pytest.fixture
def sample_glucose_data():
    """示例血糖数据"""
    return {
        'user_id': 'test_user_id',
        'timestamp': '2025-06-03T20:18:00Z',
        'glucose_value': 6.5,
        'unit': 'mmol/L',
        'device_id': 'sensor456',
        'note': 'after dinner'
    }


@pytest.fixture
def sample_device_data():
    """示例设备数据"""
    return {
        'device_id': 'sensor456',
        'user_id': 'test_user_id',
        'device_name': '血糖仪001',
        'device_type': 'glucose_meter',
        'manufacturer': '厂商名称',
        'model': '型号ABC',
        'firmware_version': '1.0.0'
    }
