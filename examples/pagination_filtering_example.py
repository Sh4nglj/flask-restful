import sys
import os
# 将当前项目目录添加到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_restful import Api, Resource, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from flask_restful import paginate, filterable

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# 定义模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    age = db.Column(db.Integer)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'created_at': self.created_at.isoformat()
        }

# 创建数据库表
with app.app_context():
    db.create_all()

    # 添加测试数据
    if User.query.count() == 0:
        for i in range(1, 100):
            user = User(
                name=f'User {i}',
                email=f'user{i}@example.com',
                age=20 + (i % 50),
                status='active' if i % 2 == 0 else 'inactive'
            )
            db.session.add(user)
        db.session.commit()

    if Product.query.count() == 0:
        categories = ['electronics', 'clothing', 'books', 'home']
        for i in range(1, 500):
            product = Product(
                name=f'Product {i}',
                price=10.99 + (i % 100),
                category=categories[i % 4],
                stock=100 + (i % 50)
            )
            db.session.add(product)
        db.session.commit()

# 定义资源
class UserListResource(Resource):
    @filterable(allowed_fields=['name', 'email', 'age', 'status', 'created_at'])
    @paginate
    def get(self):
        # 返回查询对象和模型
        return User.query, User

class ProductListResource(Resource):
    @filterable(allowed_fields=['name', 'price', 'category', 'stock', 'created_at'])
    @paginate
    def get(self):
        return Product.query, Product

# 添加资源到API
api.add_resource(UserListResource, '/users')
api.add_resource(ProductListResource, '/products')

if __name__ == '__main__':
    app.run(debug=True)