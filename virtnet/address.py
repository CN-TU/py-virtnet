"""Address module.

Some helpers for allocating addresses.

Todo:
    * Implement like everything!
"""

from typing import Union
import ipaddress
from . context import Manager

class InterfaceIter(object): #pylint: disable=too-few-public-methods
    """Iterator over Network returning Interfaces. This works for IPv6 and IPv4."""
    def __init__(self,
                 network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
                 router: Union[ipaddress.IPv4Address, ipaddress.IPv6Address] = None) -> None:
        self.network = network
        self.hosts = network.hosts()
        self.router = router
        if isinstance(network, ipaddress.IPv4Network):
            self.__cls = ipaddress.IPv4Interface
        else:
            self.__cls = ipaddress.IPv6Interface

    def __iter__(self) -> 'InterfaceIter':
        return self

    def __next__(self) -> Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]:
        addr = next(self.hosts)
        if self.router is not None and addr == self.router:
            addr = next(self.hosts) # skip router
        return self.__cls((int(addr), self.network.prefixlen))

class Network(object): #pylint: disable=too-few-public-methods
    """Network represents a network for allocating addresses from.

    Args:
        network: An ipv4 or ipv6 network

    Attributes:
        network: The ipv4 or ipv6 network
    """
    def __init__(self, network: str, router: int = None, manager: Manager = None) -> None:
        #pylint: disable=unused-argument
        self.__network = ipaddress.ip_network(network)
        self.__router = None
        if router is not None:
            self.__router = self.__network.network_address + router
        self.__hosts = InterfaceIter(self.__network, self.__router)

    @property
    def router(self):
        """Return ip address of network router, or None in case there is none"""
        return self.__router

    @property
    def router_interface(self):
        """Return router interface, or None in case there is none"""
        if self.__router is None:
            return None
        if isinstance(self.__network, ipaddress.IPv4Network):
            return ipaddress.IPv4Interface((int(self.router), self.__network.prefixlen))
        return ipaddress.IPv6Interface((int(self.router), self.__network.prefixlen))

    def __iter__(self) -> InterfaceIter:
        return self.__hosts

    def __next__(self)  -> Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]:
        return next(self.__hosts)
