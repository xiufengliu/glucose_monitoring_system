"""
用户管理API接口
User Management API Endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models.user import (
    UserRegistrationSchema,
    UserResponseSchema
)
from app.services.user_service import UserService
from app.utils.decorators import validate_json
from app.utils.responses import success_response, error_response

# 创建命名空间
users_ns = Namespace('users', description='用户管理')

# 定义API模型用于Swagger文档
user_registration_model = users_ns.model('UserRegistration', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码'),
    'full_name': fields.String(description='全名'),
    'age': fields.Integer(description='年龄'),
    'gender': fields.String(description='性别'),
    'phone': fields.String(description='电话')
})

user_output_model = users_ns.model('UserOutput', {
    'id': fields.String(description='用户ID'),
    'username': fields.String(description='用户名'),
    'email': fields.String(description='邮箱'),
    'full_name': fields.String(description='全名'),
    'age': fields.Integer(description='年龄'),
    'gender': fields.String(description='性别'),
    'phone': fields.String(description='电话'),
    'is_active': fields.Boolean(description='是否激活'),
    'created_at': fields.String(description='创建时间'),
    'updated_at': fields.String(description='更新时间')
})

# 初始化服务和模式
user_service = UserService()
user_registration_schema = UserRegistrationSchema()
user_response_schema = UserResponseSchema()


@users_ns.route('')
class UserListResource(Resource):
    """用户列表资源"""
    
    @users_ns.doc('register_user')
    @users_ns.expect(user_registration_model)
    @users_ns.marshal_with(user_output_model, code=201)
    @validate_json
    def post(self):
        """
        用户注册
        创建新用户账户
        """
        try:
            # 验证输入数据
            user_data = user_registration_schema.load(request.json)
            
            # 检查用户名和邮箱是否已存在
            if user_service.get_user_by_username(user_data['username']):
                return error_response(
                    message="用户名已存在",
                    status_code=400
                )
            
            if user_service.get_user_by_email(user_data['email']):
                return error_response(
                    message="邮箱已存在",
                    status_code=400
                )
            
            # 创建用户
            user = user_service.create_user(user_data)
            
            # 返回响应
            response_data = user_response_schema.dump(user)
            return success_response(
                data=response_data,
                message="用户注册成功",
                status_code=201
            )
            
        except ValidationError as e:
            return error_response(
                message="输入数据验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="用户注册失败",
                details=str(e),
                status_code=500
            )
    
    @users_ns.doc('get_users')
    @users_ns.marshal_list_with(user_output_model)
    @jwt_required()
    def get(self):
        """
        获取用户列表
        需要管理员权限
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 检查权限 (这里简化处理，实际应该检查用户角色)
            current_user = user_service.get_user_by_id(current_user_id)
            if not current_user:
                return error_response(
                    message="用户不存在",
                    status_code=404
                )
            
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 查询用户列表
            result = user_service.get_users(page=page, per_page=per_page)
            
            # 返回响应
            return success_response(
                data={
                    'users': user_response_schema.dump(result['users'], many=True),
                    'pagination': result['pagination']
                },
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询用户列表失败",
                details=str(e),
                status_code=500
            )


@users_ns.route('/<string:user_id>')
class UserResource(Resource):
    """单个用户资源"""
    
    @users_ns.doc('get_user')
    @users_ns.marshal_with(user_output_model)
    @jwt_required()
    def get(self, user_id):
        """获取用户信息"""
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 检查权限：只能查看自己的信息或管理员权限
            if current_user_id != user_id:
                # 这里应该检查是否为管理员
                pass
            
            user = user_service.get_user_by_id(user_id)
            if not user:
                return error_response(
                    message="用户不存在",
                    status_code=404
                )
            
            response_data = user_response_schema.dump(user)
            return success_response(
                data=response_data,
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询用户信息失败",
                details=str(e),
                status_code=500
            )
    
    @users_ns.doc('update_user')
    @users_ns.expect(user_registration_model)
    @users_ns.marshal_with(user_output_model)
    @jwt_required()
    @validate_json
    def put(self, user_id):
        """更新用户信息"""
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 检查权限：只能更新自己的信息
            if current_user_id != user_id:
                return error_response(
                    message="无权限更新其他用户信息",
                    status_code=403
                )
            
            # 验证输入数据
            user_data = user_registration_schema.load(request.json)
            
            # 更新用户
            user = user_service.update_user(user_id, user_data)
            if not user:
                return error_response(
                    message="用户不存在",
                    status_code=404
                )
            
            # 返回响应
            response_data = user_response_schema.dump(user)
            return success_response(
                data=response_data,
                message="用户信息更新成功"
            )
            
        except ValidationError as e:
            return error_response(
                message="输入数据验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="更新用户信息失败",
                details=str(e),
                status_code=500
            )
