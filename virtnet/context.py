"""manager module.

This module provides a context class which provides automatic cleanup.
"""

class Manager(object):
    def __init__(self) -> None:
        self.registered = {}

    def register(self, obj) -> None:
        self.registered[obj] = None

    def unregister(self, obj) -> None:
        if obj in self.registered:
            del self.registered[obj]

    def __enter__(self) -> 'Manager':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        while self.registered:
            obj, _ = self.registered.popitem()
            obj.stop()
        return False
