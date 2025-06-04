"""
应用配置文件
Application Configuration
"""

import os
from datetime import timedelta


class Config:
    """基础配置类"""

    # Flask基础配置
    SECRET_KEY = 'dev-secret-key-change-in-production'

    # MongoDB配置
    MONGO_URI = 'mongodb://localhost:27017/glucose_db'

    # JWT配置
    JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # CORS配置
    CORS_ORIGINS = ['*']

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/glucose_api.log'
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 数据验证配置
    MAX_GLUCOSE_VALUE = 50.0  # mmol/L
    MIN_GLUCOSE_VALUE = 0.1   # mmol/L
    SUPPORTED_UNITS = ['mmol/L', 'mg/dL']
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True
    TESTING = False

    # 开发环境数据库
    MONGO_URI = 'mongodb://localhost:27017/glucose_dev'

    # 开发环境日志
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""

    DEBUG = False
    TESTING = True

    # 测试数据库
    MONGO_URI = 'mongodb://localhost:27017/glucose_test'

    # 测试环境JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    # 禁用CSRF保护
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False
    TESTING = False

    # 生产环境配置
    SECRET_KEY = 'production-secret-key-change-this'
    JWT_SECRET_KEY = 'production-jwt-secret-key-change-this'
    MONGO_URI = 'mongodb://localhost:27017/glucose_production'

    # 生产环境安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 生产环境日志
    LOG_LEVEL = 'WARNING'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
