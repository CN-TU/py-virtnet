"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

import pyroute2.ipdb.main
import pyroute2.ipdb.interfaces
from . iproute import IPDB

class InterfaceException(Exception):
    """Base Class for Interface-based exceptions"""

class InterfaceUpException(InterfaceException):
    """Interface is already running"""

class InterfaceDownException(InterfaceException):
    """Interface is not running"""

class VirtualInterface(object):
    """Network Interface

    A veth interface.

    Args:
        name: Name of the interface.

    Attributes:
        name: Name of the interface.
        peername: Name of peer interface.
    """
    def __init__(self, name: str, main: pyroute2.ipdb.main.IPDB, peername: str,
                 peer: pyroute2.ipdb.main.IPDB) -> None:
        self.name = name
        self.__main_ipdb = main
        self.peername = peername
        self.__peer_ipdb = peer
        self.__intf = None
        self.__peer = None
        self.start()

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
        return self.__main

    def start(self) -> None:
        """Start interface

        Raises:
            InterfaceUpException: If interface already exists.
        """
        if self.__intf is not None:
            raise InterfaceUpException()
        self.__intf = IPDB.create(ifname="virt0Master", kind="veth", peer="virt0Peer").commit()
        if self.__main_ipdb is not IPDB:
            with IPDB.interfaces["virt0Master"] as veth:
                veth.net_ns_fd = self.__main_ipdb.nl.netns
        if self.__peer_ipdb is not IPDB:
            with IPDB.interfaces["virt0Peer"] as veth:
                veth.net_ns_fd = self.__peer_ipdb.nl.netns
        with self.__peer_ipdb.interfaces["virt0Peer"] as self.__peer:
            self.__peer.ifname = self.peername
            self.__peer.up()
        with self.__main_ipdb.interfaces["virt0Master"] as self.__intf:
            self.__intf.ifname = self.name
            self.__intf.up()

    def stop(self) -> None:
        """Stop interface

        Raises:
            InterfaceDownException: If interface is already stopped.
        """
        if self.__intf is None:
            raise InterfaceDownException()
        self.__intf.remove().commit()
        self.__peer = None
        self.__intf = None
