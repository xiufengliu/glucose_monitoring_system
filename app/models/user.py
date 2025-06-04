"""
用户数据模型
User Data Model
"""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load
import bcrypt


class User:
    """用户模型"""
    
    def __init__(self, username: str, email: str, password_hash: str,
                 full_name: Optional[str] = None, age: Optional[int] = None,
                 gender: Optional[str] = None, phone: Optional[str] = None,
                 is_active: bool = True, _id: Optional[ObjectId] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        """
        初始化用户
        
        Args:
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            full_name: 全名 (可选)
            age: 年龄 (可选)
            gender: 性别 (可选)
            phone: 电话 (可选)
            is_active: 是否激活
            _id: MongoDB文档ID (可选)
            created_at: 创建时间 (可选)
            updated_at: 更新时间 (可选)
        """
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建实例"""
        return cls(
            _id=data.get('_id'),
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            full_name=data.get('full_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class UserRegistrationSchema(Schema):
    """用户注册验证模式"""
    
    username = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=50, error="用户名长度必须在3-50字符之间")
    )
    email = fields.Email(required=True, error="请输入有效的邮箱地址")
    password = fields.Str(
        required=True, 
        validate=validate.Length(min=6, max=128, error="密码长度必须在6-128字符之间")
    )
    full_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    age = fields.Int(validate=validate.Range(min=1, max=150), allow_none=True)
    gender = fields.Str(
        validate=validate.OneOf(['male', 'female', 'other'], error="性别必须是male、female或other"),
        allow_none=True
    )
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)


class UserLoginSchema(Schema):
    """用户登录验证模式"""
    
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserResponseSchema(Schema):
    """用户响应模式"""
    
    id = fields.Str(attribute='_id', dump_only=True)
    username = fields.Str()
    email = fields.Str()
    full_name = fields.Str(allow_none=True)
    age = fields.Int(allow_none=True)
    gender = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')
