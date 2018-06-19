"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

import pyroute2.ipdb.main
from . iproute import IPDB
from . container import InterfaceContainer, Interface
from . context import Manager
from . address import Network

class SwitchException(Exception):
    """Base Class for switch-based exceptions"""

class SwitchUpException(SwitchException):
    """Switch is already running"""

class SwitchDownException(SwitchException):
    """Switch is not running"""

class Switch(InterfaceContainer):
    """Switch in a network container.

    This is a switch in a networked container.

    Args:
        name: Name for the switch = interface name.

    Attributes:
        name: Name of the switch = interface name.
        network: A Network to draw ipaddresses from
        ipdb: IPDB
    """
    def __init__(self, name: str, network: Network = None,
                 ipdb: pyroute2.ipdb.main.IPDB = None,
                 manager: Manager = None) -> None:
        if ipdb is None:
            ipdb = IPDB
        self.__intf = None
        self.__manager = manager
        self.__network = network
        super().__init__(name, ipdb)

    @property
    def running(self) -> bool:
        """True if switch is running"""
        return self.__intf is not None

    @property
    def switch(self) -> bool:
        """Return true if container is a switch"""
        return True

    @property
    def network(self):
        """Return a network to draw addresses from upon connect"""
        return self.__network

    def attach_interface(self, intf: Interface) -> None:
        """Attach peer part of VirtualInterface"""
        self.__intf.add_port(intf.interface).commit()
        super().attach_interface(intf)

    def start(self) -> None:
        """Start switch

        Raises:
            SwitchUpException: If switch is already running.
        """
        if self.__intf is not None:
            raise SwitchUpException()
        self.__intf = self.ipdb.create(kind="bridge", ifname=self.name).up().commit()
        if self.__manager is not None:
            self.__manager.register(self)

    @property
    def stp(self):
        return self.__intf.br_stp_state

    @stp.setter
    def stp(self, value):
        with self.__intf as intf:
            intf.br_stp_state = 0

    def stop(self) -> None:
        """Stop switch

        Raises:
            SwitchDownException: If switch is already stopped.
        """
        if self.__intf is None:
            raise SwitchDownException()
        self.__intf.down().remove().commit()
        self.__intf = None
        if self.__manager is not None:
            self.__manager.unregister(self)
