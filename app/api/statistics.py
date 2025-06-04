"""
统计分析API接口
Statistics and Analytics API Endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from app.services.statistics_service import StatisticsService
from app.utils.responses import success_response, error_response

# 创建命名空间
statistics_ns = Namespace('statistics', description='数据统计与分析')

# 定义API模型用于Swagger文档
statistics_model = statistics_ns.model('Statistics', {
    'total_records': fields.Integer(description='总记录数'),
    'avg_glucose': fields.Float(description='平均血糖值'),
    'max_glucose': fields.Float(description='最高血糖值'),
    'min_glucose': fields.Float(description='最低血糖值'),
    'std_glucose': fields.Float(description='血糖标准差'),
    'normal_count': fields.Integer(description='正常范围记录数'),
    'high_count': fields.Integer(description='偏高记录数'),
    'low_count': fields.Integer(description='偏低记录数'),
    'time_range': fields.Raw(description='时间范围')
})

trend_model = statistics_ns.model('Trend', {
    'date': fields.String(description='日期'),
    'avg_glucose': fields.Float(description='平均血糖值'),
    'max_glucose': fields.Float(description='最高血糖值'),
    'min_glucose': fields.Float(description='最低血糖值'),
    'record_count': fields.Integer(description='记录数量')
})

# 初始化服务
statistics_service = StatisticsService()


@statistics_ns.route('/summary')
class StatisticsSummaryResource(Resource):
    """统计摘要资源"""
    
    @statistics_ns.doc('get_statistics_summary')
    @statistics_ns.marshal_with(statistics_model)
    @jwt_required()
    def get(self):
        """
        获取血糖统计摘要
        包括平均值、最值、分布等统计信息
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            device_id = request.args.get('device_id')
            
            # 解析日期参数
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)  # 默认30天
            
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
            
            # 获取统计数据
            stats = statistics_service.get_glucose_statistics(
                user_id=current_user_id,
                start_date=start_date,
                end_date=end_date,
                device_id=device_id
            )
            
            return success_response(
                data=stats,
                message="统计查询成功"
            )
            
        except ValueError as e:
            return error_response(
                message="日期格式错误",
                details=str(e),
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="统计查询失败",
                details=str(e),
                status_code=500
            )


@statistics_ns.route('/trends')
class TrendsResource(Resource):
    """趋势分析资源"""
    
    @statistics_ns.doc('get_glucose_trends')
    @statistics_ns.marshal_list_with(trend_model)
    @jwt_required()
    def get(self):
        """
        获取血糖趋势分析
        按时间维度聚合血糖数据
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            granularity = request.args.get('granularity', 'day')  # day, week, month
            device_id = request.args.get('device_id')
            
            # 验证粒度参数
            if granularity not in ['day', 'week', 'month']:
                return error_response(
                    message="粒度参数必须是day、week或month",
                    status_code=400
                )
            
            # 解析日期参数
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
            
            # 获取趋势数据
            trends = statistics_service.get_glucose_trends(
                user_id=current_user_id,
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
                device_id=device_id
            )
            
            return success_response(
                data=trends,
                message="趋势查询成功"
            )
            
        except ValueError as e:
            return error_response(
                message="日期格式错误",
                details=str(e),
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="趋势查询失败",
                details=str(e),
                status_code=500
            )


@statistics_ns.route('/distribution')
class DistributionResource(Resource):
    """分布分析资源"""
    
    @statistics_ns.doc('get_glucose_distribution')
    @jwt_required()
    def get(self):
        """
        获取血糖分布分析
        按血糖范围统计记录分布
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            device_id = request.args.get('device_id')
            
            # 解析日期参数
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
            
            # 获取分布数据
            distribution = statistics_service.get_glucose_distribution(
                user_id=current_user_id,
                start_date=start_date,
                end_date=end_date,
                device_id=device_id
            )
            
            return success_response(
                data=distribution,
                message="分布查询成功"
            )
            
        except ValueError as e:
            return error_response(
                message="日期格式错误",
                details=str(e),
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="分布查询失败",
                details=str(e),
                status_code=500
            )


@statistics_ns.route('/patterns')
class PatternsResource(Resource):
    """模式分析资源"""
    
    @statistics_ns.doc('get_glucose_patterns')
    @jwt_required()
    def get(self):
        """
        获取血糖模式分析
        分析一天中不同时段的血糖模式
        """
        try:
            # 获取当前用户身份
            current_user_id = get_jwt_identity()
            
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            device_id = request.args.get('device_id')
            
            # 解析日期参数
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
            
            # 获取模式数据
            patterns = statistics_service.get_glucose_patterns(
                user_id=current_user_id,
                start_date=start_date,
                end_date=end_date,
                device_id=device_id
            )
            
            return success_response(
                data=patterns,
                message="模式查询成功"
            )
            
        except ValueError as e:
            return error_response(
                message="日期格式错误",
                details=str(e),
                status_code=400
            )
        except Exception as e:
            return error_response(
                message="模式查询失败",
                details=str(e),
                status_code=500
            )
