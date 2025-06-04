"""
用户管理业务逻辑服务
User Management Business Logic Service
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.errors import PyMongoError

from app import mongo
from app.models.user import User


class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.collection = mongo.db.users
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        创建用户
        
        Args:
            user_data: 用户数据字典
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            Exception: 数据库操作异常
        """
        try:
            # 密码哈希
            password_hash = User.hash_password(user_data['password'])
            
            # 创建用户对象
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                full_name=user_data.get('full_name'),
                age=user_data.get('age'),
                gender=user_data.get('gender'),
                phone=user_data.get('phone')
            )
            
            # 转换为字典格式
            user_dict = user.to_dict()
            user_dict.pop('_id', None)  # 移除_id，让MongoDB自动生成
            
            # 插入数据库
            result = self.collection.insert_one(user_dict)
            
            # 返回创建的用户
            user._id = result.inserted_id
            return user
            
        except PyMongoError as e:
            raise Exception(f"数据库操作失败: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(user_id):
                return None
            
            # 查询用户
            user_dict = self.collection.find_one({'_id': ObjectId(user_id)})
            
            if user_dict:
                return User.from_dict(user_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            user_dict = self.collection.find_one({'username': username})
            
            if user_dict:
                return User.from_dict(user_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            user_dict = self.collection.find_one({'email': email})
            
            if user_dict:
                return User.from_dict(user_dict)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 认证成功返回用户对象，否则返回None
        """
        try:
            user = self.get_user_by_username(username)
            
            if user and user.check_password(password):
                return user
            return None
            
        except Exception as e:
            raise Exception(f"用户认证失败: {str(e)}")
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新的用户数据
            
        Returns:
            Optional[User]: 更新后的用户对象或None
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(user_id):
                return None
            
            # 准备更新数据
            update_dict = {}
            
            # 只更新提供的字段
            updatable_fields = ['full_name', 'age', 'gender', 'phone']
            for field in updatable_fields:
                if field in user_data:
                    update_dict[field] = user_data[field]
            
            # 如果提供了新密码，进行哈希处理
            if 'password' in user_data:
                update_dict['password_hash'] = User.hash_password(user_data['password'])
            
            # 更新时间戳
            update_dict['updated_at'] = datetime.utcnow()
            
            # 执行更新
            result = self.collection.find_one_and_update(
                {'_id': ObjectId(user_id)},
                {'$set': update_dict},
                return_document=True
            )
            
            if result:
                return User.from_dict(result)
            return None
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        停用用户账户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否操作成功
        """
        try:
            # 验证ObjectId格式
            if not ObjectId.is_valid(user_id):
                return False
            
            # 执行停用
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            raise Exception(f"数据库更新失败: {str(e)}")
    
    def get_users(self, page: int = 1, per_page: int = 20, 
                  is_active: Optional[bool] = None) -> Dict[str, Any]:
        """
        获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            is_active: 是否激活状态筛选
            
        Returns:
            Dict: 包含用户列表和分页信息的字典
        """
        try:
            # 构建查询条件
            filter_dict = {}
            if is_active is not None:
                filter_dict['is_active'] = is_active
            
            # 分页参数
            skip = (page - 1) * per_page
            
            # 执行查询
            cursor = self.collection.find(filter_dict)
            total_count = self.collection.count_documents(filter_dict)
            
            # 应用分页和排序
            users_cursor = cursor.sort('created_at', -1).skip(skip).limit(per_page)
            
            # 转换为对象列表
            users = [User.from_dict(user) for user in users_cursor]
            
            # 计算分页信息
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'users': users,
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
    
    def get_user_count(self) -> int:
        """
        获取用户总数
        
        Returns:
            int: 用户总数
        """
        try:
            return self.collection.count_documents({})
        except PyMongoError as e:
            raise Exception(f"数据库查询失败: {str(e)}")
