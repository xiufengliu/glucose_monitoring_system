"""
设备数据模型
Device Data Model
"""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load


class Device:
    """设备模型"""
    
    def __init__(self, device_id: str, user_id: str, device_name: str,
                 device_type: str, manufacturer: Optional[str] = None,
                 model: Optional[str] = None, firmware_version: Optional[str] = None,
                 is_active: bool = True, last_sync: Optional[datetime] = None,
                 _id: Optional[ObjectId] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        """
        初始化设备
        
        Args:
            device_id: 设备唯一标识
            user_id: 用户ID
            device_name: 设备名称
            device_type: 设备类型
            manufacturer: 制造商 (可选)
            model: 型号 (可选)
            firmware_version: 固件版本 (可选)
            is_active: 是否激活
            last_sync: 最后同步时间 (可选)
            _id: MongoDB文档ID (可选)
            created_at: 创建时间 (可选)
            updated_at: 更新时间 (可选)
        """
        self._id = _id
        self.device_id = device_id
        self.user_id = user_id
        self.device_name = device_name
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.model = model
        self.firmware_version = firmware_version
        self.is_active = is_active
        self.last_sync = last_sync
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            '_id': self._id,
            'device_id': self.device_id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'is_active': self.is_active,
            'last_sync': self.last_sync,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """从字典创建实例"""
        return cls(
            _id=data.get('_id'),
            device_id=data['device_id'],
            user_id=data['user_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            firmware_version=data.get('firmware_version'),
            is_active=data.get('is_active', True),
            last_sync=data.get('last_sync'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class DeviceRegistrationSchema(Schema):
    """设备注册验证模式"""
    
    device_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    device_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    device_type = fields.Str(
        required=True,
        validate=validate.OneOf(['glucose_meter', 'cgm', 'insulin_pump', 'mobile_app'])
    )
    manufacturer = fields.Str(validate=validate.Length(max=100), allow_none=True)
    model = fields.Str(validate=validate.Length(max=100), allow_none=True)
    firmware_version = fields.Str(validate=validate.Length(max=50), allow_none=True)


class DeviceResponseSchema(Schema):
    """设备响应模式"""
    
    id = fields.Str(attribute='_id', dump_only=True)
    device_id = fields.Str()
    user_id = fields.Str()
    device_name = fields.Str()
    device_type = fields.Str()
    manufacturer = fields.Str(allow_none=True)
    model = fields.Str(allow_none=True)
    firmware_version = fields.Str(allow_none=True)
    is_active = fields.Bool()
    last_sync = fields.DateTime(format='iso', allow_none=True)
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')


class DeviceStatusSchema(Schema):
    """设备状态模式"""
    
    device_id = fields.Str()
    is_active = fields.Bool()
    last_sync = fields.DateTime(format='iso', allow_none=True)
    battery_level = fields.Int(validate=validate.Range(min=0, max=100), allow_none=True)
    signal_strength = fields.Int(validate=validate.Range(min=0, max=100), allow_none=True)
    status_message = fields.Str(allow_none=True)
