import json

from wrapt import ObjectProxy


class TypeWrapper(ObjectProxy):
    """
    Type annotation wrapper

    This is a base class for adding type annotations and OpenMCT config
    information to pipeline data. For an example, see imagify.ImageUri.
    """

    def _omct_hints(self):
        """Get the OpenMCT configuration hints"""
        return dict()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TypeWrapper):
            return self.default(obj.__wrapped__)
        return obj