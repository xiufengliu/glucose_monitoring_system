"""
设备管理业务逻辑服务
Device Management Business Logic Service
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.errors import PyMongoError

from app import mongo
from app.models.device import Device


class DeviceService:
    """设备服务类"""
    
    def __init__(self):
        self.collection = mongo.db.devices
    
    def register_device(self, device_data: Dict[str, Any]) -> Device:
        """
        注册设备
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            Device: 创建的设备对象
            
        Raises:
            Exception: 数据库操作异常
        """
        try:
            # 创建设备对象
            device = Device(
                device_id=device_data['device_id'],
                user_id=device_data['user_id'],
                device_name=device_data['device_name'],
                device_type=device_data['device_type'],
                manufacturer=device_data.get('manufacturer'),
                model=device_data.get('model'),
                firmware_version=device_data.get('firmware_version')
            )
            
            # 转换为字典格式
            device_dict = device.to_dict()
            device_dict.pop('_id', None)  # 移除_id，让MongoDB自动生成
            
            # 插入数据库
            result = self.collection.insert_one(device_dict)
            
            # 返回创建的设备
            device._id = result.inserted_id
            return device
            
        except PyMongoError as e:
            raise Exception(f"数据库操作失败: {str(e)}")
    
    def get_device_by_id(self, device_record_id: str) -> Optional[Device]:
        """
        根据记录ID获取设备
        
        Args:
            device_record_id: 设备记录ID
            
        Returns:
            Optional[Device]: 设备对象或None
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(device_record_id):
                return None
            
            # 查询设备
            device_dict = self.collection.find_one({'_id': ObjectId(device_record_id)})
            
            if device_dict:
                return Device.from_dict(device_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_device_by_device_id(self, device_id: str) -> Optional[Device]:
        """
        根据设备ID获取设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            Optional[Device]: 设备对象或None
        """
        try:
            device_dict = self.collection.find_one({'device_id': device_id})
            
            if device_dict:
                return Device.from_dict(device_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_user_devices(self, user_id: str, page: int = 1, per_page: int = 20,
                        device_type: Optional[str] = None, 
                        is_active: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取用户设备列表
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            device_type: 设备类型筛选
            is_active: 激活状态筛选
            
        Returns:
            Dict: 包含设备列表和分页信息的字典
        """
        try:
            # 构建查询条件
            filter_dict = {'user_id': user_id}
            
            if device_type:
                filter_dict['device_type'] = device_type
            
            if is_active is not None:
                filter_dict['is_active'] = is_active
            
            # 分页参数
            skip = (page - 1) * per_page
            
            # 执行查询
            cursor = self.collection.find(filter_dict)
            total_count = self.collection.count_documents(filter_dict)
            
            # 应用分页和排序
            devices_cursor = cursor.sort('created_at', -1).skip(skip).limit(per_page)
            
            # 转换为对象列表
            devices = [Device.from_dict(device) for device in devices_cursor]
            
            # 计算分页信息
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'devices': devices,
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
    
    def update_device(self, device_id: str, device_data: Dict[str, Any]) -> Optional[Device]:
        """
        更新设备信息
        
        Args:
            device_id: 设备ID
            device_data: 更新的设备数据
            
        Returns:
            Optional[Device]: 更新后的设备对象或None
        """
        try:
            # 准备更新数据
            update_dict = {}
            
            # 只更新提供的字段
            updatable_fields = ['device_name', 'manufacturer', 'model', 'firmware_version']
            for field in updatable_fields:
                if field in device_data:
                    update_dict[field] = device_data[field]
            
            # 更新时间戳
            update_dict['updated_at'] = datetime.utcnow()
            
            # 执行更新
            result = self.collection.find_one_and_update(
                {'device_id': device_id},
                {'$set': update_dict},
                return_document=True
            )
            
            if result:
                return Device.from_dict(result)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def deactivate_device(self, device_id: str) -> bool:
        """
        停用设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 是否操作成功
        """
        try:
            # 执行停用
            result = self.collection.update_one(
                {'device_id': device_id},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def update_last_sync(self, device_id: str) -> bool:
        """
        更新设备最后同步时间
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 是否操作成功
        """
        try:
            # 更新最后同步时间
            result = self.collection.update_one(
                {'device_id': device_id},
                {'$set': {'last_sync': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备状态
        
        Args:
            device_id: 设备ID
            
        Returns:
            Dict: 设备状态信息
        """
        try:
            device = self.get_device_by_device_id(device_id)
            
            if not device:
                raise Exception("设备不存在")
            
            # 计算设备状态
            now = datetime.utcnow()
            last_sync = device.last_sync
            
            # 判断设备是否在线（简单逻辑：5分钟内有同步）
            is_online = False
            if last_sync:
                time_diff = (now - last_sync).total_seconds()
                is_online = time_diff < 300  # 5分钟
            
            return {
                'device_id': device.device_id,
                'is_active': device.is_active,
                'is_online': is_online,
                'last_sync': last_sync.isoformat() if last_sync else None,
                'device_type': device.device_type,
                'status_message': '在线' if is_online else '离线'
            }
            
        except Exception as e:
            raise Exception(f"获取设备状态失败: {str(e)}")
    
    def get_device_count(self, user_id: Optional[str] = None) -> int:
        """
        获取设备总数
        
        Args:
            user_id: 用户ID (可选，用于获取特定用户的设备数)
            
        Returns:
            int: 设备总数
        """
        try:
            filter_dict = {}
            if user_id:
                filter_dict['user_id'] = user_id
            
            return self.collection.count_documents(filter_dict)
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
