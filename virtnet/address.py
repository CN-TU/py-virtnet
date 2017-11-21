"""Address module.

Some helpers for allocating addresses.

Todo:
    * Implement like everything!
"""

from typing import Union
import ipaddress
from . context import Manager

class InterfaceIter(object):
    def __init__(self, network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> None:
        self.network = network
        self.hosts = network.hosts()
        if isinstance(network, ipaddress.IPv4Network):
            self.__cls = ipaddress.IPv4Interface
        else:
            self.__cls = ipaddress.IPv6Interface

    def __iter__(self) -> 'InterfaceIter':
        return self

    def __next__(self) -> Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]:
        return self.__cls((int(next(self.hosts)), self.network.prefixlen))

class Network(object):
    """Network represents a network for allocating addresses from.

    Args:
        network: An ipv4 or ipv6 network

    Attributes:
        network: The ipv4 or ipv6 network
    """
    def __init__(self, network: str, manager: Manager = None) -> None:
        self.network = ipaddress.ip_network(network)
        self.hosts = InterfaceIter(self.network)

    def __iter__(self) -> InterfaceIter:
        return self.hosts

    def __next__(self)  -> Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]:
        return next(self.hosts)
