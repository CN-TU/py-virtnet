"""base_container module.

This module build the base for every device and all the interfaces.
"""

from typing import Union, Sequence, Type, List, Tuple
from enum import Enum
import ipaddress
import collections
from abc import ABC, abstractmethod
import pyroute2.ipdb.main
from . address import Network
from . iproute import IPDB
import os

class RouteDirection(Enum):
    """Route direction behaviour on connect"""
    DEFAULT = 1
    NONE = 2
    INWARD = 3
    OUTWARD = 4
    
    @property
    def allow_ingress(self) -> bool:
        return self == RouteDirection.INWARD or self == RouteDirection.DEFAULT
    
    @property
    def allow_egress(self) -> bool:
        return self == RouteDirection.OUTWARD or self == RouteDirection.DEFAULT
    
    def reverse(self):
        if self == RouteDirection.INWARD:
            return RouteDirection.OUTWARD
        elif self == RouteDirection.OUTWARD:
            return RouteDirection.INWARD
        else:
            return self


class BaseContainer(ABC):
    """BaseContainer provides base functionality like naming, starting, stopping.

    Args:
        name: Name for this thing.
        ipdb: Instances to IPDBs, this container belongs to

    Attributes:
        name: Name of this thing.
    """
    def __init__(self, name: str,
                 ipdb: Union[pyroute2.ipdb.main.IPDB,
                             Sequence[pyroute2.ipdb.main.IPDB]]=None) -> None:
        self.name = name
        self.__ipdb = ipdb
        self.start()

    @property
    def router(self) -> bool:
        """Return true if container is a router"""
        return False

    @property
    def switch(self) -> bool:
        """Return true if container is a switch"""
        return False

    @property
    @abstractmethod
    def running(self) -> bool:
        """Returns true if this device is running"""
        return False

    @property
    def ipdb(self) -> Union[pyroute2.ipdb.main.IPDB, Sequence[pyroute2.ipdb.main.IPDB], None]:
        """Returns ipdb of this device"""
        return self.__ipdb

    @ipdb.setter
    def ipdb(self, value):
        self.__ipdb = value

    @abstractmethod
    def start(self) -> None:
        """Starts up device"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the device"""
        pass

    def get_hostnames(self) -> List[Tuple[str, Union[ipaddress.IPv4Address,
                                                     ipaddress.IPv6Address]]]:
        # pylint: disable=no-self-use
        "Return a list of (hostname, address) pairs"
        return []

    def set_hosts(self, hosts: List[Tuple[str, Union[ipaddress.IPv4Address,
                                                     ipaddress.IPv6Address]]]):
        "Set listed hosts as hosts file."
        pass

class Interface(BaseContainer): # pylint: disable=abstract-method
    """Interface is the base for all Interfaces
        Args:
        name: Name for this Interface.
        ipdb: Instance to IPDB, this container belongs to
        route: routing properties for this link.

    Attributes:
        name: Name of this Interface.
        interface: pyroute2 interface.
        route: routing properties for this link."""
    def __init__(self, name: str, interface: pyroute2.ipdb.interfaces.Interface,
                 ipdb: pyroute2.ipdb.main.IPDB = None, route: RouteDirection = None) -> None:
        self.interface = interface
        self.addresses = set()
        self.route = route
        super().__init__(name, ipdb)

    def set_name(self, name:str):
        """Set new name"""
        with self.interface as intf:
            intf.name = name
        self.name = name

    def move_to(self, container):
        """Move interface to container"""
        with self.interface as intf:
                if container.ipdb is IPDB:
                    # move interface back to physical host
                    intf.net_ns_pid = os.getpid()
                else:
                    intf.net_ns_fd = container.ipdb.nl.netns
                    container.attach_interface(self)
        self.ipdb = container.ipdb
        while True:
            try:
                self.interface = self.ipdb.interfaces[self.name]
            except KeyError:
                continue
            break
        self.interface.up()

    @property
    def running(self) -> bool:
        return self.interface is not None

    def add_ip(self, address: Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface,
                                    Network]) -> None:
        "Add ip to interface"
        if isinstance(address, Network):
            address = next(address)
        self.addresses.add(address)
        self.interface.add_ip(address.with_prefixlen).commit()

    def del_ip(self, address: Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]) -> None:
        "Remove ip from interface"
        self.addresses.remove(address)
        self.interface.del_ip(address.with_prefixlen).commit()

class Link(BaseContainer):
    """Link is the base for a link
        Args:
        name: Name for this thing.
        ipdb: Instances to two IPDBs, this container belongs to
        route: routing properties for this link.

    Attributes:
        name: Name of this thing.
        route: routing properties for this link."""
    def __init__(self, name: str, peers: Sequence["InterfaceContainer"], peername: str,
                 route: RouteDirection = None) -> None:
        self.peername = peername
        self.route = route
        self.peers = peers
        super().__init__(name, list(obj.ipdb for obj in peers))

    @property
    @abstractmethod
    def peer(self) -> pyroute2.ipdb.interfaces.Interface:
        """Return the peer Interface"""
        raise NotImplementedError

    @property
    @abstractmethod
    def main(self) -> pyroute2.ipdb.interfaces.Interface:
        """Return main interface"""
        raise NotImplementedError

class InterfaceContainer(BaseContainer): # pylint: disable=abstract-method
    """InterfaceContainer provides attaching Interfaces to a container"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.interfaces = collections.OrderedDict()

    @property
    def network(self):
        """Return a network to draw addresses from upon connect"""
        return None

    def attach_interface(self, intf: Interface) -> None:
        """Attach existing interface to this container"""
        self.interfaces[intf.name] = intf

    def connect(self, intf: Type[Interface], remote: 'InterfaceContainer', name: str,
                remotename: str = None, route: RouteDirection = RouteDirection.DEFAULT) -> Link:
        """Connect InterfaceContainer with another InterfaceContainer"""
        if remotename is None:
            remotename = "{}{}".format(self.name, len(self.interfaces))
        intf = intf(name, [self, remote], remotename, route=route)
        self.attach_interface(intf.main)

        network = remote.network
        if network is not None:
            router = network.router
            if self.router:
                if route is RouteDirection.DEFAULT and router is not None:
                    intf.main.add_ip(network.router_interface)
                else:
                    intf.main.add_ip(network)
            else:
                intf.main.add_ip(network)
                if route is RouteDirection.DEFAULT:
                    if router is not None:
                        routes = self.ipdb.routes
                        if 'default' not in routes:
                            routes.add({'dst': 'default', 'gateway': str(router)}).commit()

        remote.attach_interface(intf.peer)
        return intf

    def __getitem__(self, key: str) -> Interface:
        return self.interfaces[key]
