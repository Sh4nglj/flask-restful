#!/usr/bin/env python

import functools
import unittest

try:
    from nose import SkipTest
except ImportError:
    # 对于 Python 3.12+，nose 不兼容，使用 unittest.SkipTest
    SkipTest = unittest.SkipTest


def expected_failure(test):
    @functools.wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception:
            raise SkipTest
        else:
            raise AssertionError('Failure expected')
    return inner
