"""
血糖数据API接口
Glucose Data API Endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models.glucose import (
    GlucoseRecordSchema, 
    GlucoseRecordResponseSchema, 
    GlucoseQuerySchema
)
from app.services.glucose_service import GlucoseService
from app.utils.decorators import validate_json
from app.utils.responses import success_response, error_response

# 创建命名空间
glucose_ns = Namespace('glucose', description='血糖数据管理')

# 定义API模型用于Swagger文档
glucose_input_model = glucose_ns.model('GlucoseInput', {
    'user_id': fields.String(required=True, description='用户ID'),
    'timestamp': fields.String(required=True, description='测量时间戳 (ISO8601格式)'),
    'glucose_value': fields.Float(required=True, description='血糖值'),
    'unit': fields.String(required=True, description='单位 (mmol/L 或 mg/dL)'),
    'device_id': fields.String(description='设备ID'),
    'note': fields.String(description='备注')
})

glucose_output_model = glucose_ns.model('GlucoseOutput', {
    'id': fields.String(description='记录ID'),
    'user_id': fields.String(description='用户ID'),
    'timestamp': fields.String(description='测量时间戳'),
    'glucose_value': fields.Float(description='血糖值'),
    'unit': fields.String(description='单位'),
    'device_id': fields.String(description='设备ID'),
    'note': fields.String(description='备注'),
    'created_at': fields.String(description='创建时间')
})

# 初始化服务和模式
glucose_service = GlucoseService()
glucose_schema = GlucoseRecordSchema()
glucose_response_schema = GlucoseRecordResponseSchema()
glucose_query_schema = GlucoseQuerySchema()


@glucose_ns.route('')
class GlucoseListResource(Resource):
    """血糖记录列表资源"""
    
    @glucose_ns.doc('create_glucose_record')
    @glucose_ns.expect(glucose_input_model)
    @validate_json
    def post(self):
        """
        创建血糖记录
        上传单条血糖测量数据
        """
        try:
            # 验证输入数据
            glucose_record = glucose_schema.load(request.json)
            
            # 保存记录
            result = glucose_service.create_record(glucose_record)
            
            # 返回响应
            response_data = glucose_response_schema.dump(result)
            return success_response(
                data=response_data,
                message="血糖记录创建成功",
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
                message="创建血糖记录失败",
                details=str(e),
                status_code=500
            )
    
    @glucose_ns.doc('get_glucose_records')
    def get(self):
        """
        获取血糖记录列表
        支持分页和筛选
        """
        try:
            # 验证查询参数
            query_params = glucose_query_schema.load(request.args)
            
            # 查询记录
            result = glucose_service.get_records(query_params)
            
            # 返回响应
            return success_response(
                data={
                    'records': glucose_response_schema.dump(result['records'], many=True),
                    'pagination': result['pagination']
                },
                message="查询成功"
            )
            
        except ValidationError as e:
            return error_response(
                message="查询参数验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="查询血糖记录失败",
                details=str(e),
                status_code=500
            )


@glucose_ns.route('/<string:record_id>')
class GlucoseResource(Resource):
    """单个血糖记录资源"""
    
    @glucose_ns.doc('get_glucose_record')
    def get(self, record_id):
        """获取单个血糖记录"""
        try:
            record = glucose_service.get_record_by_id(record_id)
            if not record:
                return error_response(
                    message="记录不存在",
                    status_code=404
                )
            
            response_data = glucose_response_schema.dump(record)
            return success_response(
                data=response_data,
                message="查询成功"
            )
            
        except Exception as e:
            return error_response(
                message="查询血糖记录失败",
                details=str(e),
                status_code=500
            )
    
    @glucose_ns.doc('update_glucose_record')
    @glucose_ns.expect(glucose_input_model)
    @validate_json
    def put(self, record_id):
        """更新血糖记录"""
        try:
            # 验证输入数据
            glucose_record = glucose_schema.load(request.json)
            
            # 更新记录
            result = glucose_service.update_record(record_id, glucose_record)
            if not result:
                return error_response(
                    message="记录不存在",
                    status_code=404
                )
            
            # 返回响应
            response_data = glucose_response_schema.dump(result)
            return success_response(
                data=response_data,
                message="血糖记录更新成功"
            )
            
        except ValidationError as e:
            return error_response(
                message="输入数据验证失败",
                details=e.messages,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="更新血糖记录失败",
                details=str(e),
                status_code=500
            )
    
    @glucose_ns.doc('delete_glucose_record')
    def delete(self, record_id):
        """删除血糖记录"""
        try:
            result = glucose_service.delete_record(record_id)
            if not result:
                return error_response(
                    message="记录不存在",
                    status_code=404
                )
            
            return success_response(
                message="血糖记录删除成功"
            )
            
        except Exception as e:
            return error_response(
                message="删除血糖记录失败",
                details=str(e),
                status_code=500
            )
