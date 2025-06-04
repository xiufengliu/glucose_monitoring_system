"""
血糖记录数据模型
Glucose Record Data Model
"""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load, ValidationError


class GlucoseRecord:
    """血糖记录模型"""
    
    def __init__(self, user_id: str, timestamp: datetime, glucose_value: float, 
                 unit: str, device_id: Optional[str] = None, note: Optional[str] = None,
                 _id: Optional[ObjectId] = None, created_at: Optional[datetime] = None):
        """
        初始化血糖记录
        
        Args:
            user_id: 用户ID
            timestamp: 测量时间戳
            glucose_value: 血糖值
            unit: 单位 (mmol/L 或 mg/dL)
            device_id: 设备ID (可选)
            note: 备注 (可选)
            _id: MongoDB文档ID (可选)
            created_at: 创建时间 (可选)
        """
        self._id = _id
        self.user_id = user_id
        self.timestamp = timestamp
        self.glucose_value = glucose_value
        self.unit = unit
        self.device_id = device_id
        self.note = note
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'glucose_value': self.glucose_value,
            'unit': self.unit,
            'device_id': self.device_id,
            'note': self.note,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GlucoseRecord':
        """从字典创建实例"""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            timestamp=data['timestamp'],
            glucose_value=data['glucose_value'],
            unit=data['unit'],
            device_id=data.get('device_id'),
            note=data.get('note'),
            created_at=data.get('created_at')
        )


class GlucoseRecordSchema(Schema):
    """血糖记录验证模式"""
    
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    timestamp = fields.DateTime(required=True, format='iso')
    glucose_value = fields.Float(
        required=True,
        validate=validate.Range(min=0.1, max=50.0)
    )
    unit = fields.Str(
        required=True,
        validate=validate.OneOf(['mmol/L', 'mg/dL'])
    )
    device_id = fields.Str(validate=validate.Length(max=100), allow_none=True)
    note = fields.Str(validate=validate.Length(max=500), allow_none=True)
    
    @post_load
    def make_glucose_record(self, data, **kwargs):
        """创建GlucoseRecord实例"""
        return GlucoseRecord(**data)


class GlucoseRecordResponseSchema(Schema):
    """血糖记录响应模式"""

    id = fields.Method("get_id", dump_only=True)
    user_id = fields.Str()
    timestamp = fields.DateTime(format='iso')
    glucose_value = fields.Float()
    unit = fields.Str()
    device_id = fields.Str(allow_none=True)
    note = fields.Str(allow_none=True)
    created_at = fields.DateTime(format='iso')

    def get_id(self, obj):
        """获取字符串格式的ID"""
        if hasattr(obj, '_id') and obj._id:
            return str(obj._id)
        return None


class GlucoseQuerySchema(Schema):
    """血糖查询参数模式"""
    
    user_id = fields.Str(required=True)
    start_date = fields.DateTime(format='iso', allow_none=True)
    end_date = fields.DateTime(format='iso', allow_none=True)
    device_id = fields.Str(allow_none=True)
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)
    sort_by = fields.Str(validate=validate.OneOf(['timestamp', 'glucose_value', 'created_at']), load_default='timestamp')
    sort_order = fields.Str(validate=validate.OneOf(['asc', 'desc']), load_default='desc')
