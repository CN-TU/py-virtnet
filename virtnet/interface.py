"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

import pyroute2.ipdb.main
import pyroute2.ipdb.interfaces
from . iproute import IPDB
from . container import Interface, Link

class InterfaceException(Exception):
    """Base Class for Interface-based exceptions"""

class InterfaceUpException(InterfaceException):
    """Interface is already running"""

class InterfaceDownException(InterfaceException):
    """Interface is not running"""

class VirtualInterface(Interface):
    """Virtual Network device

    A veth interface.

    Args:
        name: Name of the interface.

    Attributes:
        name: Name of the interface.
    """
    def __init__(self, name: str, interface: pyroute2.ipdb.interfaces.Interface,
                 ipdb: pyroute2.ipdb.main.IPDB, parent: 'VirtualLink') -> None:
        self.parent = parent
        super().__init__(name, interface, ipdb)

    def start(self) -> None:
        with self.interface as intf:
            intf.ifname = self.name
            intf.up()

    def stop(self) -> None:
        self.interface.remove().commit()

class VirtualLink(Link):
    """Network link consisting of two virtual devices

    A veth interface.

    Args:
        name: Name of the interface.

    Attributes:
        name: Name of the interface.
        peername: Name of peer interface.
    """
    def __init__(self, *args, **kwargs) -> None:
        self.__intf = None
        self.__peer = None
        super().__init__(*args, **kwargs)

    @property
    def running(self) -> bool:
        """True if interfaces exists"""
        return self.__intf is not None

    @property
    def peer(self) -> pyroute2.ipdb.interfaces.Interface:
        """Return peer interface"""
        if not self.running:
            raise InterfaceDownException()
        return self.__peer

    @property
    def main(self) -> pyroute2.ipdb.interfaces.Interface:
        """Return main interface"""
        if not self.running:
            raise InterfaceDownException()
        return self.__intf

    def start(self) -> None:
        """Start interface

        Raises:
            InterfaceUpException: If interface already exists.
        """
        if self.__intf is not None:
            raise InterfaceUpException()
        self.__intf = IPDB.create(ifname="virt0Master", kind="veth", peer="virt0Peer").commit()
        if self.ipdb[0] is not IPDB:
            with IPDB.interfaces["virt0Master"] as veth:
                veth.net_ns_fd = self.ipdb[0].nl.netns
        if self.ipdb[1] is not IPDB:
            with IPDB.interfaces["virt0Peer"] as veth:
                veth.net_ns_fd = self.ipdb[1].nl.netns
        self.__peer = VirtualInterface(self.peername, self.ipdb[1].interfaces["virt0Peer"],
                                       self.ipdb[1], self)
        self.__intf = VirtualInterface(self.name, self.ipdb[0].interfaces["virt0Master"],
                                       self.ipdb[0], self)

    def stop(self) -> None:
        """Stop interface

        Raises:
            InterfaceDownException: If interface is already stopped.
        """
        if self.__intf is None:
            raise InterfaceDownException()
        self.__intf.stop()
        self.__peer = None
        self.__intf = None
