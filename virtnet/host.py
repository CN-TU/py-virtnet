"""Host module.

This module contains everything to represent a virtual host in it's own
network container.

Todo:
    * Implement like everything!
"""

from typing import Union

from pyroute2.netns.nslink import NetNS
import pyroute2.ipdb.main

from . switch import Switch
from . interface import VirtualInterface

class HostException(Exception):
    """Base Class for Host-based exceptions"""

class HostUpException(HostException):
    """Host is already running"""

class HostDownException(HostException):
    """Host is not running"""

class NamespaceExistsException(HostException):
    """Namespace with this name already exists"""

class Host(object):
    """Host in a network container.

    This is a host in a networked container.

    Args:
        name: Name for the host, which is the name for the network namespace.

    Attributes:
        name: Name of the host, which is also the name of the network namespace.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.__ns = None
        self.__ipdb = None
        self.interfaces = []
        self.start()

    @property
    def running(self) -> bool:
        """True if host is running"""
        return self.__ns is not None

    @property
    def ipdb(self) -> pyroute2.ipdb.main.IPDB:
        """Return host IPDB"""
        if not self.running:
            raise HostDownException()
        return self.__ipdb

    def connect(self, remote: Union[Switch, 'Host'], name: str, remotename: str = None) -> None:
        """Connect host to switch or host"""
        if remotename is None:
            remotename = "{}{}".format(self.name, len(self.interfaces))
        intf = VirtualInterface(name, self.ipdb, remotename, remote.ipdb)
        self.interfaces.append(intf)
        remote.attach_peer(intf)

    def attach_peer(self, intf: VirtualInterface) -> None:
        """Attach peer part of VirtualInterface"""
        self.interfaces.append(intf)

    def start(self) -> None:
        """Start host

        Raises:
            HostUpException: If host is already running.
        """
        if self.__ns is not None:
            raise HostUpException()
        try:
            self.__ns = NetNS(self.name)
        except FileExistsError:
            raise HostUpException()
        self.__ipdb = pyroute2.ipdb.main.IPDB(nl=self.__ns)

    def stop(self) -> None:
        """Stop host

        Raises:
            HostDownException: If host is already stopped.
        """
        if self.__ns is None:
            raise HostDownException()
        for interface in self.interfaces:
            if interface.running:
                interface.stop()
        self.__ipdb.release()
        self.__ipdb = None
        self.__ns.close()
        self.__ns.remove()
        self.__ns = None
