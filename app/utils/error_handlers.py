"""
全局错误处理器
Global Error Handlers
"""

from flask import Flask
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from pymongo.errors import PyMongoError
from app.utils.responses import error_response


def register_error_handlers(app: Flask):
    """
    注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """处理Marshmallow验证错误"""
        return error_response(
            message="数据验证失败",
            details=e.messages,
            status_code=400
        )
    
    @app.errorhandler(PyMongoError)
    def handle_mongo_error(e):
        """处理MongoDB错误"""
        return error_response(
            message="数据库操作失败",
            details=str(e),
            status_code=500
        )
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """处理400错误"""
        return error_response(
            message="请求格式错误",
            details=str(e.description),
            status_code=400
        )
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """处理401错误"""
        return error_response(
            message="未授权访问",
            details=str(e.description),
            status_code=401
        )
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """处理403错误"""
        return error_response(
            message="禁止访问",
            details=str(e.description),
            status_code=403
        )
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """处理404错误"""
        return error_response(
            message="资源不存在",
            details=str(e.description),
            status_code=404
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理405错误"""
        return error_response(
            message="请求方法不允许",
            details=str(e.description),
            status_code=405
        )
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        """处理422错误"""
        return error_response(
            message="无法处理的实体",
            details=str(e.description),
            status_code=422
        )
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(e):
        """处理429错误"""
        return error_response(
            message="请求频率超限",
            details=str(e.description),
            status_code=429
        )
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理500错误"""
        return error_response(
            message="服务器内部错误",
            details="请联系系统管理员",
            status_code=500
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理其他HTTP异常"""
        return error_response(
            message=e.name,
            details=str(e.description),
            status_code=e.code
        )
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """处理未捕获的异常"""
        # 在生产环境中，应该记录详细的错误日志
        app.logger.error(f"未处理的异常: {str(e)}", exc_info=True)
        
        return error_response(
            message="服务器内部错误",
            details="请联系系统管理员",
            status_code=500
        )
