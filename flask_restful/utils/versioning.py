# -*- coding: utf-8 -*-
"""
Version compatibility testing utilities for Flask-RESTful API versioning system.
"""

import unittest
import json
from flask import Flask

# 延迟导入以避免循环依赖
Api = None
Resource = None

def _import_flask_restful():
    global Api, Resource
    if Api is None or Resource is None:
        from flask_restful import Api, Resource
    return Api, Resource


class VersionCompatibilityTest(unittest.TestCase):
    """
    Base class for API version compatibility tests.
    
    This class provides utilities to test that different API versions
    produce compatible responses.
    """
    
    def setUp(self):
        """Set up test app and API."""
        _import_flask_restful()  # 确保Api已导入
        self.app = Flask(__name__)
        self.api = Api(self.app, default_version='v1')
        
    def test_version_compatibility(self, endpoint, versions, expected_status=200):
        """
        Test that the same endpoint behaves consistently across versions.
        
        :param endpoint: The API endpoint to test (e.g., '/users')
        :type endpoint: str
        
        :param versions: List of versions to test
        :type versions: list
        
        :param expected_status: Expected HTTP status code
        :type expected_status: int
        """
        with self.app.test_client() as client:
            for version in versions:
                # Test with URL path versioning
                versioned_endpoint = '/{}{}'.format(version, endpoint)
                response = client.get(versioned_endpoint)
                self.assertEqual(response.status_code, expected_status, 
                                 "Version {} failed with status {} for endpoint {}".format(
                                     version, response.status_code, versioned_endpoint))
                
                # Test with query parameter versioning
                response = client.get('{}?version={}'.format(endpoint, version))
                self.assertEqual(response.status_code, expected_status, 
                                 "Version {} failed with status {} for endpoint {}?version={}".format(
                                     version, response.status_code, endpoint, version))
                
                # Test with header versioning
                response = client.get(endpoint, headers={'Accept': 'application/json; version={}'.format(version)})
                self.assertEqual(response.status_code, expected_status, 
                                 "Version {} failed with status {} for endpoint {} with version header".format(
                                     version, response.status_code, endpoint))
    
    def test_response_format(self, endpoint, version, expected_fields):
        """
        Test that the response contains expected fields.
        
        :param endpoint: The API endpoint to test (e.g., '/users')
        :type endpoint: str
        
        :param version: The API version to test
        :type version: str
        
        :param expected_fields: List of expected fields in the response
        :type expected_fields: list
        """
        with self.app.test_client() as client:
            versioned_endpoint = '/{}{}'.format(version, endpoint)
            response = client.get(versioned_endpoint)
            data = json.loads(response.data.decode('utf-8'))
            
            for field in expected_fields:
                self.assertIn(field, data, "Version {} missing field '{}' in response".format(version, field))


def generate_compatibility_report(api, test_cases):
    """
    Generate a compatibility report for API versions.
    
    :param api: The Flask-RESTful API instance
    :type api: flask_restful.Api
    
    :param test_cases: List of test cases to run
    :type test_cases: list
    
    :return: Compatibility report as a dictionary
    :rtype: dict
    """
    report = {
        'api_version': getattr(api, 'version', 'unknown'),
        'test_cases': [],
        'summary': {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
    }
    
    app = Flask(__name__)
    api.init_app(app)
    
    with app.test_client() as client:
        for test_case in test_cases:
            endpoint = test_case['endpoint']
            versions = test_case['versions']
            expected_status = test_case.get('expected_status', 200)
            
            for version in versions:
                report['summary']['total_tests'] += 1
                
                # Test URL path versioning
                versioned_endpoint = '/{}{}'.format(version, endpoint)
                response = client.get(versioned_endpoint)
                
                test_result = {
                    'endpoint': endpoint,
                    'version': version,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'expected_status': expected_status,
                    'passed': response.status_code == expected_status
                }
                
                if response.status_code == expected_status:
                    report['summary']['passed_tests'] += 1
                else:
                    report['summary']['failed_tests'] += 1
                    test_result['error'] = 'Status code mismatch'
                
                report['test_cases'].append(test_result)
    
    return report


def generate_compatibility_report_json(api, test_cases):
    """
    Generate compatibility report in JSON format.
    
    :param api: The Flask-RESTful API instance
    :type api: flask_restful.Api
    
    :param test_cases: List of test cases to run
    :type test_cases: list
    
    :return: JSON formatted compatibility report
    :rtype: str
    """
    report = generate_compatibility_report(api, test_cases)
    return json.dumps(report, indent=2, ensure_ascii=False)