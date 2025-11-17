import sys

try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict

from werkzeug.http import HTTP_STATUS_CODES
from .cors import crossdomain
from .crypto import encrypt, decrypt
from .rate_limit import RateLimiter, rate_limit, get_ip_key_func, get_user_key_func, MemoryStorage, RedisStorage, configure_global_rate_limit

PY3 = sys.version_info > (3,)


def http_status_message(code):
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}
