import time
import sys
import os
# 将当前项目目录添加到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_restful import paginate, filterable

# 创建测试应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_performance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# 定义测试模型
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.Integer)
    category = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

# 创建数据库表
with app.app_context():
    db.create_all()

# 定义测试资源
class TestResource(Resource):
    @filterable(allowed_fields=['name', 'value', 'category', 'created_at'])
    @paginate
    def get(self):
        return TestModel.query, TestModel

# 添加资源到API
api.add_resource(TestResource, '/test')

def test_performance(data_sizes):
    """测试不同数据量下的查询性能"""
    results = []
    
    for size in data_sizes:
        print(f"Testing with {size} records...")
        
        # 清空表并插入新数据
        with app.app_context():
            db.session.query(TestModel).delete()
            
            # 插入测试数据
            for i in range(size):
                item = TestModel(
                    name=f'Item {i}',
                    value=i,
                    category=f'Category {i % 10}'
                )
                db.session.add(item)
            db.session.commit()
        
        # 测试基本分页
        client = app.test_client()
        start_time = time.time()
        response = client.get('/test?page=1&per_page=20')
        end_time = time.time()
        basic_time = end_time - start_time
        
        # 测试带过滤的查询
        start_time = time.time()
        response = client.get('/test?filter[value][gte]=100&filter[value][lte]=200&sort=value')
        end_time = time.time()
        filter_time = end_time - start_time
        
        # 测试带排序的查询
        start_time = time.time()
        response = client.get('/test?sort=-created_at&page=5&per_page=10')
        end_time = time.time()
        sort_time = end_time - start_time
        
        results.append({
            'data_size': size,
            'basic_pagination': basic_time,
            'filtered_query': filter_time,
            'sorted_query': sort_time
        })
        
        print(f"  Basic pagination: {basic_time:.4f}s")
        print(f"  Filtered query: {filter_time:.4f}s")
        print(f"  Sorted query: {sort_time:.4f}s")
    
    return results

def main():
    # 测试不同数据量
    data_sizes = [1000, 5000, 10000, 20000, 50000]
    
    print("Starting performance tests...")
    results = test_performance(data_sizes)
    
    print("\n" + "="*50)
    print("Performance Test Results")
    print("="*50)
    print(f"{'Data Size':<12} {'Basic Pagination':<18} {'Filtered Query':<16} {'Sorted Query':<14}")
    print("-"*50)
    
    for result in results:
        size = result['data_size']
        basic = result['basic_pagination']
        filtered = result['filtered_query']
        sorted_ = result['sorted_query']
        print(f"{size:<12} {basic:.4f}s{'':<10} {filtered:.4f}s{'':<8} {sorted_:.4f}s")
    
    print("="*50)

if __name__ == '__main__':
    main()