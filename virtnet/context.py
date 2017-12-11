"""manager module.

This module provides a context class which provides automatic cleanup.
"""

import collections
import ipaddress

def _bfs(interface, toroute):
    peer, peerintf = interface.peer()
    if not peer.router and not peer.switch:
        return
    if peer.router:
        for address in toroute:
            peer.ipdb.routes.add({'dst': str(ipaddress.ip_network(str(address),
                                                                  strict=False)),
                                  'gateway': str(next(iter(interface.addresses)).ip)
                                 }).commit()
    for intf in peer.interfaces.values():
        if intf is peerintf:
            continue
        _bfs(intf, toroute)


def _do_router(router):
    nets = set(address
               for interface in router.interfaces.values()
               for address in interface.addresses)
    for interface in router.interfaces.values():
        toroute = nets - set(interface.addresses)
        _bfs(interface, toroute)

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
        for router in filter(lambda x: x.router, self.registered):
            _do_router(router)

    def __enter__(self) -> 'Manager':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        while self.registered:
            obj, _ = self.registered.popitem()
            obj.stop()
        return False
