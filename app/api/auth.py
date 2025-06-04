"""
认证API接口
Authentication API Endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError

from app.models.user import UserLoginSchema
from app.services.user_service import UserService
from app.utils.decorators import validate_json
from app.utils.responses import success_response, error_response

# 创建命名空间
auth_ns = Namespace('auth', description='用户认证')

# 定义API模型用于Swagger文档
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='访问令牌'),
    'refresh_token': fields.String(description='刷新令牌'),
    'expires_in': fields.Integer(description='过期时间(秒)'),
    'token_type': fields.String(description='令牌类型')
})

# 初始化服务和模式
user_service = UserService()
login_schema = UserLoginSchema()

# 用于存储已撤销的令牌 (生产环境应使用Redis)
revoked_tokens = set()


@auth_ns.route('/login')
class LoginResource(Resource):
    """用户登录资源"""
    
    @auth_ns.doc('user_login')
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model)
    @validate_json
    def post(self):
        """
        用户登录
        验证用户凭据并返回JWT令牌
        """
        try:
            # 验证输入数据
            login_data = login_schema.load(request.json)
            
            # 验证用户凭据
            user = user_service.authenticate_user(
                login_data['username'], 
                login_data['password']
            )
            
            if not user:
                return error_response(
                    message="用户名或密码错误",
                    status_code=401
                )
            
            if not user.is_active:
                return error_response(
                    message="用户账户已被禁用",
                    status_code=401
                )
            
            # 创建JWT令牌
            access_token = create_access_token(identity=str(user._id))
            refresh_token = create_refresh_token(identity=str(user._id))
            
            # 返回响应
            return success_response(
                data={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': 86400,  # 24小时
                    'token_type': 'Bearer',
                    'user': {
                        'id': str(user._id),
                        'username': user.username,
                        'email': user.email
                    }
                },
                message="登录成功"
            )
            
        except ValidationError as e:
            return error_response(
                message="输入数据验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="登录失败",
                details=str(e),
                status_code=500
            )


@auth_ns.route('/refresh')
class RefreshResource(Resource):
    """令牌刷新资源"""
    
    @auth_ns.doc('refresh_token')
    @auth_ns.marshal_with(token_model)
    @jwt_required(refresh=True)
    def post(self):
        """
        刷新访问令牌
        使用刷新令牌获取新的访问令牌
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 检查用户是否存在且激活
            user = user_service.get_user_by_id(current_user_id)
            if not user or not user.is_active:
                return error_response(
                    message="用户不存在或已被禁用",
                    status_code=401
                )
            
            # 创建新的访问令牌
            new_access_token = create_access_token(identity=current_user_id)
            
            # 返回响应
            return success_response(
                data={
                    'access_token': new_access_token,
                    'expires_in': 86400,  # 24小时
                    'token_type': 'Bearer'
                },
                message="令牌刷新成功"
            )
            
        except Exception as e:
            return error_response(
                message="令牌刷新失败",
                details=str(e),
                status_code=500
            )


@auth_ns.route('/logout')
class LogoutResource(Resource):
    """用户登出资源"""
    
    @auth_ns.doc('user_logout')
    @jwt_required()
    def post(self):
        """
        用户登出
        撤销当前访问令牌
        """
        try:
            # 获取当前令牌
            jti = get_jwt()['jti']  # JWT ID
            
            # 将令牌添加到撤销列表
            revoked_tokens.add(jti)
            
            return success_response(
                message="登出成功"
            )
            
        except Exception as e:
            return error_response(
                message="登出失败",
                details=str(e),
                status_code=500
            )


@auth_ns.route('/me')
class ProfileResource(Resource):
    """用户资料资源"""
    
    @auth_ns.doc('get_profile')
    @jwt_required()
    def get(self):
        """
        获取当前用户信息
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取用户信息
            user = user_service.get_user_by_id(current_user_id)
            if not user:
                return error_response(
                    message="用户不存在",
                    status_code=404
                )
            
            # 返回用户信息（不包含敏感数据）
            return success_response(
                data={
                    'id': str(user._id),
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'age': user.age,
                    'gender': user.gender,
                    'phone': user.phone,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                },
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="获取用户信息失败",
                details=str(e),
                status_code=500
            )


# JWT令牌撤销检查回调
def check_if_token_revoked(jwt_header, jwt_payload):
    """检查令牌是否已被撤销"""
    jti = jwt_payload['jti']
    return jti in revoked_tokens
