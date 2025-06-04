"""
血糖数据API测试
Glucose Data API Tests
"""

import pytest
import json
from datetime import datetime


class TestGlucoseAPI:
    """血糖数据API测试类"""
    
    def test_create_glucose_record_success(self, client, clean_db, sample_glucose_data):
        """测试成功创建血糖记录"""
        response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['glucose_value'] == 6.5
        assert data['data']['unit'] == 'mmol/L'
    
    def test_create_glucose_record_missing_required_field(self, client, clean_db):
        """测试缺少必填字段"""
        incomplete_data = {
            'user_id': 'test_user_id',
            'timestamp': '2025-06-03T20:18:00Z',
            # 缺少glucose_value
            'unit': 'mmol/L'
        }
        
        response = client.post(
            '/api/glucose',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'glucose_value' in str(data['details'])
    
    def test_create_glucose_record_invalid_glucose_value(self, client, clean_db, sample_glucose_data):
        """测试无效的血糖值"""
        sample_glucose_data['glucose_value'] = -1.0  # 负值
        
        response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_create_glucose_record_invalid_unit(self, client, clean_db, sample_glucose_data):
        """测试无效的单位"""
        sample_glucose_data['unit'] = 'invalid_unit'
        
        response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_create_glucose_record_invalid_timestamp(self, client, clean_db, sample_glucose_data):
        """测试无效的时间戳格式"""
        sample_glucose_data['timestamp'] = 'invalid_timestamp'
        
        response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_get_glucose_records_success(self, client, clean_db):
        """测试成功获取血糖记录列表"""
        # 先创建一些测试数据
        test_data = {
            'user_id': 'test_user_id',
            'timestamp': '2025-06-03T20:18:00Z',
            'glucose_value': 6.5,
            'unit': 'mmol/L'
        }
        
        client.post(
            '/api/glucose',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # 查询记录
        response = client.get('/api/glucose?user_id=test_user_id')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'records' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_glucose_records_missing_user_id(self, client, clean_db):
        """测试缺少用户ID参数"""
        response = client.get('/api/glucose')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_get_glucose_records_with_pagination(self, client, clean_db):
        """测试分页查询"""
        # 创建多条测试数据
        for i in range(5):
            test_data = {
                'user_id': 'test_user_id',
                'timestamp': f'2025-06-0{i+1}T20:18:00Z',
                'glucose_value': 6.0 + i * 0.1,
                'unit': 'mmol/L'
            }
            
            client.post(
                '/api/glucose',
                data=json.dumps(test_data),
                content_type='application/json'
            )
        
        # 分页查询
        response = client.get('/api/glucose?user_id=test_user_id&page=1&per_page=3')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']['records']) <= 3
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['per_page'] == 3
    
    def test_get_glucose_record_by_id_success(self, client, clean_db, sample_glucose_data):
        """测试根据ID获取血糖记录"""
        # 先创建记录
        create_response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        record_id = create_data['data']['id']
        
        # 根据ID查询
        response = client.get(f'/api/glucose/{record_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['id'] == record_id
    
    def test_get_glucose_record_by_id_not_found(self, client, clean_db):
        """测试查询不存在的记录"""
        fake_id = '507f1f77bcf86cd799439011'
        response = client.get(f'/api/glucose/{fake_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_update_glucose_record_success(self, client, clean_db, sample_glucose_data):
        """测试成功更新血糖记录"""
        # 先创建记录
        create_response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        record_id = create_data['data']['id']
        
        # 更新记录
        update_data = sample_glucose_data.copy()
        update_data['glucose_value'] = 7.0
        update_data['note'] = 'updated note'
        
        response = client.put(
            f'/api/glucose/{record_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['glucose_value'] == 7.0
        assert data['data']['note'] == 'updated note'
    
    def test_delete_glucose_record_success(self, client, clean_db, sample_glucose_data):
        """测试成功删除血糖记录"""
        # 先创建记录
        create_response = client.post(
            '/api/glucose',
            data=json.dumps(sample_glucose_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        record_id = create_data['data']['id']
        
        # 删除记录
        response = client.delete(f'/api/glucose/{record_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # 验证记录已删除
        get_response = client.get(f'/api/glucose/{record_id}')
        assert get_response.status_code == 404
