"""
装饰器工具函数
Decorator Utility Functions
"""

from functools import wraps
from flask import request
from app.utils.responses import error_response


def validate_json(f):
    """
    验证请求是否包含有效的JSON数据
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return error_response(
                message="请求必须包含JSON数据",
                status_code=400
            )
        
        if request.get_json() is None:
            return error_response(
                message="无效的JSON格式",
                status_code=400
            )
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_fields(*required_fields):
    """
    验证请求JSON中是否包含必需字段
    
    Args:
        required_fields: 必需字段列表
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response(
                    message="请求必须包含JSON数据",
                    status_code=400
                )
            
            json_data = request.get_json()
            if json_data is None:
                return error_response(
                    message="无效的JSON格式",
                    status_code=400
                )
            
            missing_fields = []
            for field in required_fields:
                if field not in json_data or json_data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return error_response(
                    message="缺少必需字段",
                    details={"missing_fields": missing_fields},
                    status_code=400
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_content_type(content_type='application/json'):
    """
    验证请求的Content-Type
    
    Args:
        content_type: 期望的Content-Type
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_type != content_type:
                return error_response(
                    message=f"Content-Type必须为{content_type}",
                    status_code=400
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def rate_limit(max_requests=100, per_seconds=3600):
    """
    简单的速率限制装饰器
    注意：这是一个简化版本，生产环境应使用Redis等外部存储
    
    Args:
        max_requests: 最大请求次数
        per_seconds: 时间窗口（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 这里应该实现真正的速率限制逻辑
            # 简化版本直接通过
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_request(f):
    """
    记录请求日志的装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这里可以添加请求日志记录逻辑
        # 例如记录请求时间、IP地址、用户代理等
        return f(*args, **kwargs)
    
    return decorated_function
