"""
统计分析业务逻辑服务
Statistics and Analytics Business Logic Service
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
import statistics

from app import mongo


class StatisticsService:
    """统计服务类"""
    
    def __init__(self):
        self.glucose_collection = mongo.db.glucose_records
    
    def get_glucose_statistics(self, user_id: str, start_date: datetime, 
                             end_date: datetime, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取血糖统计信息
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            device_id: 设备ID (可选)
            
        Returns:
            Dict: 统计信息
        """
        try:
            # 构建查询条件
            filter_dict = {
                'user_id': user_id,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }
            
            if device_id:
                filter_dict['device_id'] = device_id
            
            # 获取所有记录
            records = list(self.glucose_collection.find(filter_dict))
            
            if not records:
                return {
                    'total_records': 0,
                    'avg_glucose': None,
                    'max_glucose': None,
                    'min_glucose': None,
                    'std_glucose': None,
                    'normal_count': 0,
                    'high_count': 0,
                    'low_count': 0,
                    'time_range': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }
            
            # 提取血糖值
            glucose_values = [record['glucose_value'] for record in records]
            
            # 计算基本统计
            total_records = len(records)
            avg_glucose = statistics.mean(glucose_values)
            max_glucose = max(glucose_values)
            min_glucose = min(glucose_values)
            std_glucose = statistics.stdev(glucose_values) if len(glucose_values) > 1 else 0
            
            # 血糖范围分类 (基于mmol/L)
            normal_count = 0
            high_count = 0
            low_count = 0
            
            for value in glucose_values:
                if value < 3.9:  # 低血糖
                    low_count += 1
                elif value > 7.8:  # 高血糖
                    high_count += 1
                else:  # 正常范围
                    normal_count += 1
            
            return {
                'total_records': total_records,
                'avg_glucose': round(avg_glucose, 2),
                'max_glucose': max_glucose,
                'min_glucose': min_glucose,
                'std_glucose': round(std_glucose, 2),
                'normal_count': normal_count,
                'high_count': high_count,
                'low_count': low_count,
                'normal_percentage': round((normal_count / total_records) * 100, 1),
                'high_percentage': round((high_count / total_records) * 100, 1),
                'low_percentage': round((low_count / total_records) * 100, 1),
                'time_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
        except Exception as e:
            raise Exception(f"统计计算失败: {str(e)}")
    
    def get_glucose_trends(self, user_id: str, start_date: datetime, 
                          end_date: datetime, granularity: str = 'day',
                          device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取血糖趋势数据
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            granularity: 时间粒度 ('day', 'week', 'month')
            device_id: 设备ID (可选)
            
        Returns:
            List[Dict]: 趋势数据列表
        """
        try:
            # 构建聚合管道
            match_stage = {
                'user_id': user_id,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }
            
            if device_id:
                match_stage['device_id'] = device_id
            
            # 根据粒度设置分组格式
            if granularity == 'day':
                date_format = '%Y-%m-%d'
                group_id = {
                    'year': {'$year': '$timestamp'},
                    'month': {'$month': '$timestamp'},
                    'day': {'$dayOfMonth': '$timestamp'}
                }
            elif granularity == 'week':
                date_format = '%Y-W%U'
                group_id = {
                    'year': {'$year': '$timestamp'},
                    'week': {'$week': '$timestamp'}
                }
            else:  # month
                date_format = '%Y-%m'
                group_id = {
                    'year': {'$year': '$timestamp'},
                    'month': {'$month': '$timestamp'}
                }
            
            pipeline = [
                {'$match': match_stage},
                {
                    '$group': {
                        '_id': group_id,
                        'avg_glucose': {'$avg': '$glucose_value'},
                        'max_glucose': {'$max': '$glucose_value'},
                        'min_glucose': {'$min': '$glucose_value'},
                        'record_count': {'$sum': 1},
                        'first_timestamp': {'$min': '$timestamp'}
                    }
                },
                {'$sort': {'first_timestamp': 1}}
            ]
            
            # 执行聚合查询
            results = list(self.glucose_collection.aggregate(pipeline))
            
            # 格式化结果
            trends = []
            for result in results:
                if granularity == 'day':
                    date_str = f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}"
                elif granularity == 'week':
                    date_str = f"{result['_id']['year']}-W{result['_id']['week']:02d}"
                else:  # month
                    date_str = f"{result['_id']['year']}-{result['_id']['month']:02d}"
                
                trends.append({
                    'date': date_str,
                    'avg_glucose': round(result['avg_glucose'], 2),
                    'max_glucose': result['max_glucose'],
                    'min_glucose': result['min_glucose'],
                    'record_count': result['record_count']
                })
            
            return trends
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
        except Exception as e:
            raise Exception(f"趋势分析失败: {str(e)}")
    
    def get_glucose_distribution(self, user_id: str, start_date: datetime, 
                               end_date: datetime, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取血糖分布数据
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            device_id: 设备ID (可选)
            
        Returns:
            Dict: 分布数据
        """
        try:
            # 构建查询条件
            filter_dict = {
                'user_id': user_id,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }
            
            if device_id:
                filter_dict['device_id'] = device_id
            
            # 定义血糖范围
            ranges = [
                {'name': '严重低血糖', 'min': 0, 'max': 2.8, 'color': '#ff4444'},
                {'name': '低血糖', 'min': 2.8, 'max': 3.9, 'color': '#ff8800'},
                {'name': '正常', 'min': 3.9, 'max': 7.8, 'color': '#00cc44'},
                {'name': '轻度高血糖', 'min': 7.8, 'max': 11.1, 'color': '#ffaa00'},
                {'name': '高血糖', 'min': 11.1, 'max': 50, 'color': '#ff4444'}
            ]
            
            # 获取所有记录
            records = list(self.glucose_collection.find(filter_dict))
            total_records = len(records)
            
            if total_records == 0:
                return {
                    'total_records': 0,
                    'ranges': [{'name': r['name'], 'count': 0, 'percentage': 0, 'color': r['color']} for r in ranges]
                }
            
            # 统计各范围的记录数
            distribution = []
            for range_info in ranges:
                count = sum(1 for record in records 
                           if range_info['min'] <= record['glucose_value'] < range_info['max'])
                percentage = (count / total_records) * 100
                
                distribution.append({
                    'name': range_info['name'],
                    'min': range_info['min'],
                    'max': range_info['max'],
                    'count': count,
                    'percentage': round(percentage, 1),
                    'color': range_info['color']
                })
            
            return {
                'total_records': total_records,
                'ranges': distribution
            }
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
        except Exception as e:
            raise Exception(f"分布分析失败: {str(e)}")
    
    def get_glucose_patterns(self, user_id: str, start_date: datetime, 
                           end_date: datetime, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取血糖模式分析
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            device_id: 设备ID (可选)
            
        Returns:
            Dict: 模式分析数据
        """
        try:
            # 构建聚合管道，按小时分组
            match_stage = {
                'user_id': user_id,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }
            
            if device_id:
                match_stage['device_id'] = device_id
            
            pipeline = [
                {'$match': match_stage},
                {
                    '$group': {
                        '_id': {'$hour': '$timestamp'},
                        'avg_glucose': {'$avg': '$glucose_value'},
                        'max_glucose': {'$max': '$glucose_value'},
                        'min_glucose': {'$min': '$glucose_value'},
                        'record_count': {'$sum': 1}
                    }
                },
                {'$sort': {'_id': 1}}
            ]
            
            # 执行聚合查询
            results = list(self.glucose_collection.aggregate(pipeline))
            
            # 格式化结果
            hourly_patterns = []
            for result in results:
                hour = result['_id']
                hourly_patterns.append({
                    'hour': hour,
                    'time_label': f"{hour:02d}:00",
                    'avg_glucose': round(result['avg_glucose'], 2),
                    'max_glucose': result['max_glucose'],
                    'min_glucose': result['min_glucose'],
                    'record_count': result['record_count']
                })
            
            # 分析时段模式
            time_periods = {
                'dawn': {'hours': [4, 5, 6, 7], 'name': '黎明时段', 'records': []},
                'morning': {'hours': [8, 9, 10, 11], 'name': '上午时段', 'records': []},
                'afternoon': {'hours': [12, 13, 14, 15, 16, 17], 'name': '下午时段', 'records': []},
                'evening': {'hours': [18, 19, 20, 21], 'name': '晚上时段', 'records': []},
                'night': {'hours': [22, 23, 0, 1, 2, 3], 'name': '夜间时段', 'records': []}
            }
            
            # 将小时数据分配到时段
            for pattern in hourly_patterns:
                hour = pattern['hour']
                for period_key, period_info in time_periods.items():
                    if hour in period_info['hours']:
                        period_info['records'].append(pattern)
            
            # 计算各时段统计
            period_stats = {}
            for period_key, period_info in time_periods.items():
                if period_info['records']:
                    avg_glucose = statistics.mean([r['avg_glucose'] for r in period_info['records']])
                    total_records = sum([r['record_count'] for r in period_info['records']])
                    
                    period_stats[period_key] = {
                        'name': period_info['name'],
                        'avg_glucose': round(avg_glucose, 2),
                        'record_count': total_records,
                        'hours': period_info['hours']
                    }
                else:
                    period_stats[period_key] = {
                        'name': period_info['name'],
                        'avg_glucose': None,
                        'record_count': 0,
                        'hours': period_info['hours']
                    }
            
            return {
                'hourly_patterns': hourly_patterns,
                'period_stats': period_stats
            }
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
        except Exception as e:
            raise Exception(f"模式分析失败: {str(e)}")
