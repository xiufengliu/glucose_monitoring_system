"""
配置文件加载器
Configuration File Loader
"""

import configparser
import os
from datetime import timedelta


class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self, config_file='config.ini'):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            print(f"警告: 配置文件 {self.config_file} 不存在，使用默认配置")
    
    def get(self, section, key, fallback=None, value_type=str):
        """
        获取配置值
        
        Args:
            section: 配置段
            key: 配置键
            fallback: 默认值
            value_type: 值类型 (str, int, float, bool)
            
        Returns:
            配置值
        """
        try:
            if value_type == bool:
                return self.config.getboolean(section, key, fallback=fallback)
            elif value_type == int:
                return self.config.getint(section, key, fallback=fallback)
            elif value_type == float:
                return self.config.getfloat(section, key, fallback=fallback)
            else:
                return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_database_config(self, environment='development'):
        """获取数据库配置"""
        return {
            'MONGO_URI': self.get(environment, 'mongo_uri', 
                                 fallback='mongodb://localhost:27017/glucose_dev')
        }
    
    def get_jwt_config(self, environment='development'):
        """获取JWT配置"""
        access_token_minutes = self.get(environment, 'jwt_access_token_expires_minutes', 
                                       fallback=1440, value_type=int)  # 24小时
        
        return {
            'JWT_SECRET_KEY': self.get(environment, 'jwt_secret_key', 
                                      fallback='jwt-secret-key-change-in-production'),
            'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=access_token_minutes),
            'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30)
        }
    
    def get_app_config(self, environment='development'):
        """获取应用配置"""
        return {
            'SECRET_KEY': self.get(environment, 'secret_key', 
                                  fallback='dev-secret-key-change-in-production'),
            'DEBUG': self.get(environment, 'debug', fallback=True, value_type=bool),
            'TESTING': self.get(environment, 'testing', fallback=False, value_type=bool),
            'LOG_LEVEL': self.get(environment, 'log_level', fallback='INFO'),
            'LOG_FILE': self.get(environment, 'log_file', fallback='logs/glucose_api.log')
        }
    
    def get_server_config(self, environment='development'):
        """获取服务器配置"""
        return {
            'host': self.get(environment, 'host', fallback='0.0.0.0'),
            'port': self.get(environment, 'port', fallback=5000, value_type=int),
            'debug': self.get(environment, 'debug', fallback=True, value_type=bool)
        }


# 全局配置加载器实例
config_loader = ConfigLoader()
