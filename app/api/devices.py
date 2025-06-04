"""
设备管理API接口
Device Management API Endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models.device import (
    DeviceRegistrationSchema,
    DeviceResponseSchema,
    DeviceStatusSchema
)
from app.services.device_service import DeviceService
from app.utils.decorators import validate_json
from app.utils.responses import success_response, error_response

# 创建命名空间
devices_ns = Namespace('devices', description='设备管理')

# 定义API模型用于Swagger文档
device_registration_model = devices_ns.model('DeviceRegistration', {
    'device_id': fields.String(required=True, description='设备ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'device_name': fields.String(required=True, description='设备名称'),
    'device_type': fields.String(required=True, description='设备类型'),
    'manufacturer': fields.String(description='制造商'),
    'model': fields.String(description='型号'),
    'firmware_version': fields.String(description='固件版本')
})

device_output_model = devices_ns.model('DeviceOutput', {
    'id': fields.String(description='设备记录ID'),
    'device_id': fields.String(description='设备ID'),
    'user_id': fields.String(description='用户ID'),
    'device_name': fields.String(description='设备名称'),
    'device_type': fields.String(description='设备类型'),
    'manufacturer': fields.String(description='制造商'),
    'model': fields.String(description='型号'),
    'firmware_version': fields.String(description='固件版本'),
    'is_active': fields.Boolean(description='是否激活'),
    'last_sync': fields.String(description='最后同步时间'),
    'created_at': fields.String(description='创建时间'),
    'updated_at': fields.String(description='更新时间')
})

device_status_model = devices_ns.model('DeviceStatus', {
    'device_id': fields.String(description='设备ID'),
    'is_active': fields.Boolean(description='是否激活'),
    'last_sync': fields.String(description='最后同步时间'),
    'battery_level': fields.Integer(description='电池电量'),
    'signal_strength': fields.Integer(description='信号强度'),
    'status_message': fields.String(description='状态消息')
})

# 初始化服务和模式
device_service = DeviceService()
device_registration_schema = DeviceRegistrationSchema()
device_response_schema = DeviceResponseSchema()
device_status_schema = DeviceStatusSchema()


@devices_ns.route('')
class DeviceListResource(Resource):
    """设备列表资源"""
    
    @devices_ns.doc('register_device')
    @devices_ns.expect(device_registration_model)
    @devices_ns.marshal_with(device_output_model, code=201)
    @jwt_required()
    @validate_json
    def post(self):
        """
        注册设备
        为用户注册新的监测设备
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 验证输入数据
            device_data = device_registration_schema.load(request.json)
            
            # 检查权限：只能为自己注册设备
            if device_data['user_id'] != current_user_id:
                return error_response(
                    message="只能为自己注册设备",
                    status_code=403
                )
            
            # 检查设备ID是否已存在
            if device_service.get_device_by_device_id(device_data['device_id']):
                return error_response(
                    message="设备ID已存在",
                    status_code=400
                )
            
            # 注册设备
            device = device_service.register_device(device_data)
            
            # 返回响应
            response_data = device_response_schema.dump(device)
            return success_response(
                data=response_data,
                message="设备注册成功",
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
                message="设备注册失败",
                details=str(e),
                status_code=500
            )
    
    @devices_ns.doc('get_devices')
    @devices_ns.marshal_list_with(device_output_model)
    @jwt_required()
    def get(self):
        """
        获取设备列表
        获取当前用户的所有设备
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            device_type = request.args.get('device_type')
            is_active = request.args.get('is_active', type=bool)
            
            # 查询设备列表
            result = device_service.get_user_devices(
                user_id=current_user_id,
                page=page,
                per_page=per_page,
                device_type=device_type,
                is_active=is_active
            )
            
            # 返回响应
            return success_response(
                data={
                    'devices': device_response_schema.dump(result['devices'], many=True),
                    'pagination': result['pagination']
                },
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询设备列表失败",
                details=str(e),
                status_code=500
            )


@devices_ns.route('/<string:device_id>')
class DeviceResource(Resource):
    """单个设备资源"""
    
    @devices_ns.doc('get_device')
    @devices_ns.marshal_with(device_output_model)
    @jwt_required()
    def get(self, device_id):
        """获取设备信息"""
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            device = device_service.get_device_by_device_id(device_id)
            if not device:
                return error_response(
                    message="设备不存在",
                    status_code=404
                )
            
            # 检查权限：只能查看自己的设备
            if device.user_id != current_user_id:
                return error_response(
                    message="无权限查看此设备",
                    status_code=403
                )
            
            response_data = device_response_schema.dump(device)
            return success_response(
                data=response_data,
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询设备信息失败",
                details=str(e),
                status_code=500
            )
    
    @devices_ns.doc('update_device')
    @devices_ns.expect(device_registration_model)
    @devices_ns.marshal_with(device_output_model)
    @jwt_required()
    @validate_json
    def put(self, device_id):
        """更新设备信息"""
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 验证输入数据
            device_data = device_registration_schema.load(request.json)
            
            # 检查设备是否存在
            device = device_service.get_device_by_device_id(device_id)
            if not device:
                return error_response(
                    message="设备不存在",
                    status_code=404
                )
            
            # 检查权限：只能更新自己的设备
            if device.user_id != current_user_id:
                return error_response(
                    message="无权限更新此设备",
                    status_code=403
                )
            
            # 更新设备
            updated_device = device_service.update_device(device_id, device_data)
            
            # 返回响应
            response_data = device_response_schema.dump(updated_device)
            return success_response(
                data=response_data,
                message="设备信息更新成功"
            )
            
        except ValidationError as e:
            return error_response(
                message="输入数据验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="更新设备信息失败",
                details=str(e),
                status_code=500
            )


@devices_ns.route('/<string:device_id>/status')
class DeviceStatusResource(Resource):
    """设备状态资源"""
    
    @devices_ns.doc('get_device_status')
    @devices_ns.marshal_with(device_status_model)
    @jwt_required()
    def get(self, device_id):
        """获取设备状态"""
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 检查设备权限
            device = device_service.get_device_by_device_id(device_id)
            if not device:
                return error_response(
                    message="设备不存在",
                    status_code=404
                )
            
            if device.user_id != current_user_id:
                return error_response(
                    message="无权限查看此设备状态",
                    status_code=403
                )
            
            # 获取设备状态
            status = device_service.get_device_status(device_id)
            
            return success_response(
                data=status,
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询设备状态失败",
                details=str(e),
                status_code=500
            )
