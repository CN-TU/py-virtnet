"""base_container module.

This module build the base for every device and all the interfaces.
"""

from typing import Union, Sequence, Type
import collections
from abc import ABC, abstractmethod
import pyroute2.ipdb.main

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
    @abstractmethod
    def running(self) -> bool:
        """Returns true if this device is running"""
        return False

    @property
    def ipdb(self) -> Union[pyroute2.ipdb.main.IPDB, Sequence[pyroute2.ipdb.main.IPDB], None]:
        """Returns ipdb of this device"""
        return self.__ipdb

    @abstractmethod
    def start(self) -> None:
        """Starts up device"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the device"""
        pass

class Interface(BaseContainer): # pylint: disable=abstract-method
    """Interface is the base for all Interfaces
        Args:
        name: Name for this Interface.
        ipdb: Instance to IPDB, this container belongs to

    Attributes:
        name: Name of this Interface.
        interface: pyroute2 interface"""
    def __init__(self, name: str, interface: pyroute2.ipdb.interfaces.Interface,
                 ipdb: pyroute2.ipdb.main.IPDB = None) -> None:
        self.interface = interface
        super().__init__(name, ipdb)

    @property
    def running(self) -> bool:
        return self.interface is not None

class Link(BaseContainer):
    """Link is the base for a link
        Args:
        name: Name for this thing.
        ipdb: Instances to two IPDBs, this container belongs to

    Attributes:
        name: Name of this thing."""
    def __init__(self, name: str, ipdb: Sequence[pyroute2.ipdb.main.IPDB], peername: str) -> None:
        self.peername = peername
        super().__init__(name, ipdb)

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

    def attach_interface(self, intf: Interface) -> None:
        """Attach existing interface to this container"""
        self.interfaces[intf.name] = intf

    def connect(self, intf: Type[Interface], remote: 'InterfaceContainer', name: str,
                remotename: str = None) -> None:
        """Connect InterfaceContainer with another InterfaceContainer"""
        if remotename is None:
            remotename = "{}{}".format(self.name, len(self.interfaces))
        intf = intf(name, [self.ipdb, remote.ipdb], remotename)
        self.attach_interface(intf)
        remote.attach_interface(intf)
