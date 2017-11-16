"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

import pyroute2.ipdb.main
from . iproute import IPDB
from . container import InterfaceContainer, Interface

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
        ipdb: IPDB
    """
    def __init__(self, name: str, ipdb: pyroute2.ipdb.main.IPDB = None) -> None:
        if ipdb is None:
            ipdb = IPDB
        self.__intf = None
        super().__init__(name, ipdb)

    @property
    def running(self) -> bool:
        """True if switch is running"""
        return self.__intf is not None

    def attach_interface(self, intf: Interface) -> None:
        """Attach peer part of VirtualInterface"""
        self.__intf.add_port(intf.peer).commit()
        super().attach_interface(intf)

    def start(self) -> None:
        """Start switch

        Raises:
            SwitchUpException: If switch is already running.
        """
        if self.__intf is not None:
            raise SwitchUpException()
        self.__intf = IPDB.create(kind="bridge", ifname=self.name).up().commit()

    def stop(self) -> None:
        """Stop switch

        Raises:
            SwitchDownException: If switch is already stopped.
        """
        if self.__intf is None:
            raise SwitchDownException()
        self.__intf.down().remove().commit()
        self.__intf = None
