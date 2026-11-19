"""Check only the Python packages used by an individual test route."""
from functools import wraps
import importlib.util
import unittest


def require_packages(*names):
    missing = [name for name in names if importlib.util.find_spec(name) is None]
    if missing:
        raise unittest.SkipTest('Missing Python packages for this test: ' + ', '.join(missing))


def requires_packages(*names):
    def decorate(test):
        @wraps(test)
        def checked(*args, **kwargs):
            require_packages(*names)
            return test(*args, **kwargs)
        return checked
    return decorate
