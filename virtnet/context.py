"""manager module.

This module provides a context class which provides automatic cleanup.
"""

import collections
import ipaddress
			
class Manager(object):
    """Context manager for automatically cleaning up created network resources. Just use this object
    instead of the virtnet module."""
    def __init__(self) -> None:
        self.registered = collections.OrderedDict()

    def register(self, obj) -> None:
        "Register an object for future removal."
        self.registered[obj] = None

    def unregister(self, obj) -> None:
        "Unregister an object from future removal."
        if obj in self.registered:
            del self.registered[obj]

    def update_hosts(self) -> None:
        "Update all hosts files to include every Host"
        hosts = []
        for obj in self.registered:
            hosts.extend(obj.get_hostnames())
        for obj in self.registered:
            obj.set_hosts(hosts)

    def simple_route(self) -> None:
        "Add routes between routers"
        for host in filter(lambda x: hasattr(x, 'find_routes'), self.registered):
            host.remove_prohibited_routes()
        for host in filter(lambda x: hasattr(x, 'find_routes'), self.registered):
            host.find_routes()

    def __enter__(self) -> 'Manager':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        while self.registered:
            obj, _ = self.registered.popitem()
            obj.stop()
        return False
