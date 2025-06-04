"""
CLI命令工具
CLI Command Utilities
"""

import click
from flask import Flask
from app import mongo
from app.models.user import User
from app.services.user_service import UserService


def register_cli_commands(app: Flask):
    """
    注册CLI命令
    
    Args:
        app: Flask应用实例
    """
    
    @app.cli.command()
    def init_db():
        """初始化数据库"""
        click.echo("正在初始化数据库...")
        
        try:
            # 创建索引
            with app.app_context():
                # 用户集合索引
                mongo.db.users.create_index("username", unique=True)
                mongo.db.users.create_index("email", unique=True)
                
                # 血糖记录集合索引
                mongo.db.glucose_records.create_index([("user_id", 1), ("timestamp", -1)])
                mongo.db.glucose_records.create_index("device_id")
                
                # 设备集合索引
                mongo.db.devices.create_index("device_id", unique=True)
                mongo.db.devices.create_index([("user_id", 1), ("device_type", 1)])
                
            click.echo("数据库初始化完成！")
            
        except Exception as e:
            click.echo(f"数据库初始化失败: {str(e)}")
    
    @app.cli.command()
    @click.option('--username', prompt='用户名', help='管理员用户名')
    @click.option('--email', prompt='邮箱', help='管理员邮箱')
    @click.option('--password', prompt='密码', hide_input=True, help='管理员密码')
    def create_admin(username, email, password):
        """创建管理员用户"""
        click.echo("正在创建管理员用户...")
        
        try:
            with app.app_context():
                user_service = UserService()
                
                # 检查用户是否已存在
                if user_service.get_user_by_username(username):
                    click.echo("用户名已存在！")
                    return
                
                if user_service.get_user_by_email(email):
                    click.echo("邮箱已存在！")
                    return
                
                # 创建管理员用户
                user_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'full_name': '系统管理员'
                }
                
                user = user_service.create_user(user_data)
                click.echo(f"管理员用户创建成功！用户ID: {user._id}")
                
        except Exception as e:
            click.echo(f"创建管理员用户失败: {str(e)}")
    
    @app.cli.command()
    def show_stats():
        """显示系统统计信息"""
        click.echo("正在获取系统统计信息...")
        
        try:
            with app.app_context():
                # 用户统计
                user_count = mongo.db.users.count_documents({})
                active_user_count = mongo.db.users.count_documents({"is_active": True})
                
                # 设备统计
                device_count = mongo.db.devices.count_documents({})
                active_device_count = mongo.db.devices.count_documents({"is_active": True})
                
                # 血糖记录统计
                glucose_count = mongo.db.glucose_records.count_documents({})
                
                click.echo("\n=== 系统统计信息 ===")
                click.echo(f"用户总数: {user_count}")
                click.echo(f"活跃用户: {active_user_count}")
                click.echo(f"设备总数: {device_count}")
                click.echo(f"活跃设备: {active_device_count}")
                click.echo(f"血糖记录总数: {glucose_count}")
                
        except Exception as e:
            click.echo(f"获取统计信息失败: {str(e)}")
    
    @app.cli.command()
    def clear_data():
        """清空所有数据（谨慎使用）"""
        if click.confirm('确定要清空所有数据吗？此操作不可恢复！'):
            try:
                with app.app_context():
                    mongo.db.users.delete_many({})
                    mongo.db.devices.delete_many({})
                    mongo.db.glucose_records.delete_many({})
                    
                click.echo("所有数据已清空！")
                
            except Exception as e:
                click.echo(f"清空数据失败: {str(e)}")
        else:
            click.echo("操作已取消。")
    
    @app.cli.command()
    @click.option('--collection', help='要检查的集合名称')
    def check_indexes(collection):
        """检查数据库索引"""
        click.echo("正在检查数据库索引...")
        
        try:
            with app.app_context():
                collections = [collection] if collection else ['users', 'devices', 'glucose_records']
                
                for coll_name in collections:
                    click.echo(f"\n=== {coll_name} 集合索引 ===")
                    indexes = mongo.db[coll_name].list_indexes()
                    
                    for index in indexes:
                        click.echo(f"索引名: {index['name']}")
                        click.echo(f"键: {index['key']}")
                        if 'unique' in index:
                            click.echo(f"唯一: {index['unique']}")
                        click.echo("---")
                
        except Exception as e:
            click.echo(f"检查索引失败: {str(e)}")
