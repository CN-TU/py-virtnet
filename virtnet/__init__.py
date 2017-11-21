"""Virtnet library

This library provides some high level functions to easlily setup a local
network topology with the help of pyroute2
"""

from . switch import Switch
from . host import Host
from . interface import VirtualLink
from . address import Network
from . container import BaseContainer
from . context import Manager

def _make_creator(obj):
    creator = globals()[obj]
    def create(self, *args, **kwargs):
        return creator(*args, **kwargs, manager=self)
    return create

_OBJECTS = ['Switch', 'Host', 'VirtualLink', 'Network']

for _obj in _OBJECTS:
    setattr(Manager, _obj, _make_creator(_obj))

__all__ = _OBJECTS + ['Manager']
