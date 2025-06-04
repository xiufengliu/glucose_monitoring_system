"""
血糖数据业务逻辑服务
Glucose Data Business Logic Service
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.errors import PyMongoError

from app import mongo
from app.models.glucose import GlucoseRecord


class GlucoseService:
    """血糖数据服务类"""
    
    def __init__(self):
        self.collection = mongo.db.glucose_records
    
    def create_record(self, glucose_record: GlucoseRecord) -> GlucoseRecord:
        """
        创建血糖记录
        
        Args:
            glucose_record: 血糖记录对象
            
        Returns:
            GlucoseRecord: 创建的血糖记录
            
        Raises:
            Exception: 数据库操作异常
        """
        try:
            # 转换为字典格式
            record_dict = glucose_record.to_dict()
            record_dict.pop('_id', None)  # 移除_id，让MongoDB自动生成
            
            # 插入数据库
            result = self.collection.insert_one(record_dict)
            
            # 返回创建的记录
            glucose_record._id = result.inserted_id
            return glucose_record
            
        except PyMongoError as e:
            raise Exception(f"数据库操作失败: {str(e)}")
    
    def get_record_by_id(self, record_id: str) -> Optional[GlucoseRecord]:
        """
        根据ID获取血糖记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[GlucoseRecord]: 血糖记录或None
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(record_id):
                return None
            
            # 查询记录
            record_dict = self.collection.find_one({'_id': ObjectId(record_id)})
            
            if record_dict:
                return GlucoseRecord.from_dict(record_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_records(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取血糖记录列表
        
        Args:
            query_params: 查询参数
            
        Returns:
            Dict: 包含记录列表和分页信息的字典
        """
        try:
            # 构建查询条件
            filter_dict = {'user_id': query_params['user_id']}
            
            # 时间范围筛选
            if query_params.get('start_date') or query_params.get('end_date'):
                timestamp_filter = {}
                if query_params.get('start_date'):
                    timestamp_filter['$gte'] = query_params['start_date']
                if query_params.get('end_date'):
                    timestamp_filter['$lte'] = query_params['end_date']
                filter_dict['timestamp'] = timestamp_filter
            
            # 设备筛选
            if query_params.get('device_id'):
                filter_dict['device_id'] = query_params['device_id']
            
            # 分页参数
            page = query_params.get('page', 1)
            per_page = query_params.get('per_page', 20)
            skip = (page - 1) * per_page
            
            # 排序参数
            sort_by = query_params.get('sort_by', 'timestamp')
            sort_order = 1 if query_params.get('sort_order', 'desc') == 'asc' else -1
            
            # 执行查询
            cursor = self.collection.find(filter_dict)
            total_count = self.collection.count_documents(filter_dict)
            
            # 应用排序和分页
            records_cursor = cursor.sort(sort_by, sort_order).skip(skip).limit(per_page)
            
            # 转换为对象列表
            records = [GlucoseRecord.from_dict(record) for record in records_cursor]
            
            # 计算分页信息
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'records': records,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def update_record(self, record_id: str, glucose_record: GlucoseRecord) -> Optional[GlucoseRecord]:
        """
        更新血糖记录
        
        Args:
            record_id: 记录ID
            glucose_record: 更新的血糖记录对象
            
        Returns:
            Optional[GlucoseRecord]: 更新后的记录或None
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(record_id):
                return None
            
            # 准备更新数据
            update_dict = glucose_record.to_dict()
            update_dict.pop('_id', None)
            update_dict['updated_at'] = datetime.utcnow()
            
            # 执行更新
            result = self.collection.find_one_and_update(
                {'_id': ObjectId(record_id)},
                {'$set': update_dict},
                return_document=True
            )
            
            if result:
                return GlucoseRecord.from_dict(result)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def delete_record(self, record_id: str) -> bool:
        """
        删除血糖记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(record_id):
                return False
            
            # 执行删除
            result = self.collection.delete_one({'_id': ObjectId(record_id)})
            
            return result.deleted_count > 0
            
        except PyMongoError as e:
            raise Exception(f"数据库删除失败: {str(e)}")
    
    def get_user_records_count(self, user_id: str) -> int:
        """
        获取用户血糖记录总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 记录总数
        """
        try:
            return self.collection.count_documents({'user_id': user_id})
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_latest_record(self, user_id: str, device_id: Optional[str] = None) -> Optional[GlucoseRecord]:
        """
        获取用户最新的血糖记录
        
        Args:
            user_id: 用户ID
            device_id: 设备ID (可选)
            
        Returns:
            Optional[GlucoseRecord]: 最新记录或None
        """
        try:
            filter_dict = {'user_id': user_id}
            if device_id:
                filter_dict['device_id'] = device_id
            
            record_dict = self.collection.find_one(
                filter_dict,
                sort=[('timestamp', -1)]
            )
            
            if record_dict:
                return GlucoseRecord.from_dict(record_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
