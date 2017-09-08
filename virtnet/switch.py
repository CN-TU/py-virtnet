"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

from . iproute import IPDB

class SwitchException(Exception):
    """Base Class for switch-based exceptions"""

class SwitchUpException(SwitchException):
    """Switch is already running"""

class SwitchDownException(SwitchException):
    """Switch is not running"""

class Switch(object):
    """Switch in a network container.

    This is a switch in a networked container.

    Args:
        name: Name for the switch = interface name.

    Attributes:
        name: Name of the switch = interface name.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.__intf = None
        self.start()

    @property
    def running(self) -> bool:
        """True if switch is running"""
        return self.__intf is not None

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
