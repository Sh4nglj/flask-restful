from __future__ import absolute_import
from flask import make_response, current_app
from xml.sax.saxutils import escape


def output_xml(data, code, headers=None):
    """Makes a Flask response with an XML encoded body"""
    settings = current_app.config.get('RESTFUL_XML', {})
    
    # Default settings
    default_root = settings.get('root', 'response')
    default_indent = settings.get('indent', 2)
    default_encoding = settings.get('encoding', 'utf-8')
    default_namespace = settings.get('namespace', None)
    default_ns_prefix = settings.get('ns_prefix', None)
    
    # Build XML string
    xml = []
    xml.append('<?xml version="1.0" encoding="{}"?>'.format(default_encoding))
    
    # Handle root element with namespace
    if default_namespace:
        if default_ns_prefix:
            root_start = '<{0}:{1} xmlns:{0}="{2}">'.format(default_ns_prefix, default_root, default_namespace)
            root_end = '</{0}:{1}>'.format(default_ns_prefix, default_root)
        else:
            root_start = '<{0} xmlns="{1}">'.format(default_root, default_namespace)
            root_end = '</{0}>'.format(default_root)
    else:
        root_start = '<{}>'.format(default_root)
        root_end = '</{}>'.format(default_root)
    
    xml.append(root_start)
    
    # Convert data to XML
    _to_xml(data, default_indent, 1, xml, default_ns_prefix)
    
    xml.append(root_end)
    
    # Join XML parts and make response
    xml_string = '\n'.join(xml).encode(default_encoding)
    resp = make_response(xml_string, code)
    resp.headers.extend(headers or {})
    return resp


def _to_xml(data, indent, level, xml, ns_prefix=None):
    """Helper function to convert Python data structures to XML"""
    indent_str = ' ' * (indent * level)
    
    if isinstance(data, (list, tuple)):
        for item in data:
            xml.append('{}<item>'.format(indent_str))
            _to_xml(item, indent, level + 1, xml, ns_prefix)
            xml.append('{}</item>'.format(indent_str))
    
    elif isinstance(data, dict):
        for key, value in data.items():
            tag = '{0}:{1}'.format(ns_prefix, escape(key)) if ns_prefix else escape(key)
            xml.append('{}{}'.format(indent_str, '<{}>'.format(tag)))
            _to_xml(value, indent, level + 1, xml, ns_prefix)
            xml.append('{}{}'.format(indent_str, '</{}>'.format(tag)))
    
    elif data is None:
        xml.append('{}<null />'.format(indent_str))
    
    elif isinstance(data, bool):
        xml.append('{}{}'.format(indent_str, str(data).lower()))
    
    else:
        xml.append('{}{}'.format(indent_str, escape(str(data))))