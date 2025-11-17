from __future__ import absolute_import
import unittest
from flask import Flask
import flask_restful


class TestXMLRepresentation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = flask_restful.Api(self.app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {
                    'foo': 'bar',
                    'baz': 123,
                    'bool': True,
                    'null_val': None
                }
        
        self.api.add_resource(TestResource, '/')
    
    def test_xml_basic(self):
        """Test basic XML output"""
        with self.app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/xml')
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'bar', res.data)
            self.assertIn(b'</foo>', res.data)
            self.assertIn(b'<baz>', res.data)
            self.assertIn(b'123', res.data)
            self.assertIn(b'</baz>', res.data)
            self.assertIn(b'<bool>', res.data)
            self.assertIn(b'true', res.data)
            self.assertIn(b'</bool>', res.data)
            self.assertIn(b'<null_val>', res.data)
            self.assertIn(b'<null />', res.data)
            self.assertIn(b'</null_val>', res.data)
    
    def test_text_xml(self):
        """Test text/xml output"""
        with self.app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/xml')
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'bar', res.data)
            self.assertIn(b'</foo>', res.data)
    
    def test_accept_xml(self):
        """Test application/xml accept header"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/xml')
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'bar', res.data)
    
    def test_accept_text_xml(self):
        """Test text/xml accept header"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/xml')
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'bar', res.data)
    
    def test_accept_xml_nested(self):
        """Test XML output with nested structures"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': {'bar': 'baz'}}
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'<bar>', res.data)
            self.assertIn(b'baz', res.data)
            self.assertIn(b'</bar>', res.data)
            self.assertIn(b'</foo>', res.data)
    
    def test_accept_xml_list(self):
        """Test XML output with list structures"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class Foo(flask_restful.Resource):
            def get(self):
                return {'items': [1, 2, 3]}
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<items>', res.data)
            self.assertIn(b'1', res.data)
            self.assertIn(b'2', res.data)
            self.assertIn(b'3', res.data)
            self.assertIn(b'</items>', res.data)
    
    def test_accept_xml_mixed(self):
        """Test XML output with mixed structures"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': {'bar': [1, 2, {'baz': 'qux'}]}}
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'<bar>', res.data)
            self.assertIn(b'1', res.data)
            self.assertIn(b'2', res.data)
            self.assertIn(b'<baz>', res.data)
            self.assertIn(b'qux', res.data)
            self.assertIn(b'</baz>', res.data)
            self.assertIn(b'</bar>', res.data)
            self.assertIn(b'</foo>', res.data)
    
    def test_xml_nested(self):
        """Test nested XML output"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {
                    'user': {
                        'name': 'test',
                        'email': 'test@example.com'
                    }
                }
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<user>', res.data)
            self.assertIn(b'<name>', res.data)
            self.assertIn(b'test', res.data)
            self.assertIn(b'</name>', res.data)
            self.assertIn(b'<email>', res.data)
            self.assertIn(b'test@example.com', res.data)
            self.assertIn(b'</email>', res.data)
            self.assertIn(b'</user>', res.data)
    
    def test_xml_list(self):
        """Test XML output for lists"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {
                    'items': [1, 2, 3, 4, 5]
                }
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<items>', res.data)
            self.assertIn(b'1', res.data)
            self.assertIn(b'2', res.data)
            self.assertIn(b'3', res.data)
            self.assertIn(b'4', res.data)
            self.assertIn(b'5', res.data)
            self.assertIn(b'</items>', res.data)
    
    def test_xml_mixed(self):
        """Test XML output for mixed types"""
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {
                    'foo': {
                        'bar': [1, 2, {
                            'baz': 'qux'
                        }]
                    }
                }
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'<bar>', res.data)
            self.assertIn(b'1', res.data)
            self.assertIn(b'2', res.data)
            self.assertIn(b'<baz>', res.data)
            self.assertIn(b'qux', res.data)
            self.assertIn(b'</baz>', res.data)
            self.assertIn(b'</bar>', res.data)
            self.assertIn(b'</foo>', res.data)
    
    def test_accept_xml_special_chars(self):
        """Test application/xml with special characters"""
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': '<bar>&"baz\'</bar>'}
        
        app = Flask(__name__)
        api = flask_restful.Api(app)
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'&lt;bar&gt;&amp;', res.data)
            self.assertIn(b'baz', res.data)
            self.assertIn(b'&lt;/bar&gt;', res.data)
    
    def test_accept_xml_namespace(self):
        """Test application/xml with namespace"""
        class Foo(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        app = Flask(__name__)
        app.config['RESTFUL_XML'] = {
            'namespace': 'http://example.com',
            'ns_prefix': 'ex'
        }
        api = flask_restful.Api(app)
        
        api.add_resource(Foo, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<ex:response xmlns:ex="http://example.com">', res.data)
            self.assertIn(b'<ex:foo>', res.data)  # 检查带有命名空间前缀的起始标签
            self.assertIn(b'bar', res.data)  # 检查内容
            self.assertIn(b'</ex:foo>', res.data)  # 检查带有命名空间前缀的结束标签
            self.assertIn(b'</ex:response>', res.data)
    
    def test_xml_custom_root(self):
        """Test XML output with custom root element"""
        app = Flask(__name__)
        app.config['RESTFUL_XML'] = {'root': 'custom'}
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<custom>', res.data)
            self.assertIn(b'</custom>', res.data)
    
    def test_xml_namespace(self):
        """Test XML output with namespace"""
        app = Flask(__name__)
        app.config['RESTFUL_XML'] = {
            'root': 'data',
            'namespace': 'http://example.com/api',
            'ns_prefix': 'api'
        }
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<api:data xmlns:api="http://example.com/api">', res.data)
            self.assertIn(b'<api:foo>', res.data)
            self.assertIn(b'bar', res.data)
            self.assertIn(b'</api:foo>', res.data)
            self.assertIn(b'</api:data>', res.data)
    
    def test_xml_no_prefix_namespace(self):
        """Test XML output with namespace but no prefix"""
        app = Flask(__name__)
        app.config['RESTFUL_XML'] = {
            'root': 'data',
            'namespace': 'http://example.com/api'
        }
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'<data xmlns="http://example.com/api">', res.data)
            self.assertIn(b'<foo>', res.data)
            self.assertIn(b'bar', res.data)
            self.assertIn(b'</foo>', res.data)
            self.assertIn(b'</data>', res.data)
    
    def test_xml_indent(self):
        """Test XML output with custom indent"""
        app = Flask(__name__)
        app.config['RESTFUL_XML'] = {'indent': 4}
        api = flask_restful.Api(app)
        
        class TestResource(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}
        
        api.add_resource(TestResource, '/')
        
        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'    <foo>', res.data)
            self.assertIn(b'bar', res.data)
            self.assertIn(b'</foo>', res.data)


if __name__ == '__main__':
    unittest.main()