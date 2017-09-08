"""Host module.

This module contains everything to represent a virtual host in it's own
network container.

Todo:
    * Implement like everything!
"""

import os
from pyroute2.netns.nslink import NetNS

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

    @property
    def running(self) -> bool:
        """True if host is running"""
        return self.__ns is not None

    def start(self) -> None:
        """Start host

        Raises:
            HostUpException: If host is already running.
        """
        if self.__ns is None:
            raise HostUpException()
        # handle eexists error!
        try:
            self.__ns = NetNS(self.name, flags=os.O_CREAT | os.O_EXCL)
        except FileExistsError:
            raise HostUpException()

    def stop(self) -> None:
        """Stop host

        Raises:
            HostDownException: If host is already stopped.
        """
        if self.__ns is None:
            raise HostDownException()
        self.__ns.close()
        self.__ns.remove()
