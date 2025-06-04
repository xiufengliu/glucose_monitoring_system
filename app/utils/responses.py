"""
API响应工具函数
API Response Utility Functions
"""

from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = "操作成功", 
                    status_code: int = 200) -> tuple:
    """
    成功响应格式化
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        tuple: (响应体, 状态码)
    """
    response = {
        "status": "success",
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response, status_code


def error_response(message: str = "操作失败", details: Any = None, 
                  status_code: int = 400) -> tuple:
    """
    错误响应格式化
    
    Args:
        message: 错误消息
        details: 错误详情
        status_code: HTTP状态码
        
    Returns:
        tuple: (响应体, 状态码)
    """
    response = {
        "status": "error",
        "message": message
    }
    
    if details is not None:
        response["details"] = details
    
    return response, status_code


def paginated_response(data: list, pagination: Dict[str, Any], 
                      message: str = "查询成功") -> tuple:
    """
    分页响应格式化
    
    Args:
        data: 数据列表
        pagination: 分页信息
        message: 响应消息
        
    Returns:
        tuple: (响应体, 状态码)
    """
    response = {
        "status": "success",
        "message": message,
        "data": {
            "records": data,
            "pagination": pagination
        }
    }
    
    return response, 200


def validation_error_response(errors: Dict[str, Any]) -> tuple:
    """
    验证错误响应格式化
    
    Args:
        errors: 验证错误字典
        
    Returns:
        tuple: (响应体, 状态码)
    """
    return error_response(
        message="输入数据验证失败",
        details=errors,
        status_code=400
    )


def not_found_response(resource: str = "资源") -> tuple:
    """
    资源未找到响应格式化
    
    Args:
        resource: 资源名称
        
    Returns:
        tuple: (响应体, 状态码)
    """
    return error_response(
        message=f"{resource}不存在",
        status_code=404
    )


def unauthorized_response(message: str = "未授权访问") -> tuple:
    """
    未授权响应格式化
    
    Args:
        message: 错误消息
        
    Returns:
        tuple: (响应体, 状态码)
    """
    return error_response(
        message=message,
        status_code=401
    )


def forbidden_response(message: str = "禁止访问") -> tuple:
    """
    禁止访问响应格式化
    
    Args:
        message: 错误消息
        
    Returns:
        tuple: (响应体, 状态码)
    """
    return error_response(
        message=message,
        status_code=403
    )


def internal_error_response(message: str = "服务器内部错误") -> tuple:
    """
    服务器内部错误响应格式化
    
    Args:
        message: 错误消息
        
    Returns:
        tuple: (响应体, 状态码)
    """
    return error_response(
        message=message,
        status_code=500
    )
