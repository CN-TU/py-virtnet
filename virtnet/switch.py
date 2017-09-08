"""Switch module.

This module contains everything to represent a virtual switch.

Todo:
    * Implement like everything!
"""

from . iproute import IPR

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
        self.__index = None

    @property
    def running(self) -> bool:
        """True if switch is running"""
        return self.__index is not None

    def start(self) -> None:
        """Start switch

        Raises:
            SwitchUpException: If switch is already running.
        """
        if self.__index is not None:
            raise SwitchUpException()
        IPR.link("add", ifname=self.name, kind="bridge", stp_state="0")
        self.__index = IPR.link_lookup(ifname=self.name)[0]
        IPR.link("set", index=self.__index, state="up")

    def stop(self) -> None:
        """Stop switch

        Raises:
            SwitchDownException: If switch is already stopped.
        """
        if self.__index is None:
            raise SwitchDownException()
        IPR.link("remove", index=self.__index)
