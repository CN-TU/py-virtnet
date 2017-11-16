"""Virtnet library

This library provides some high level functions to easlily setup a local
network topology with the help of pyroute2
"""

from . switch import Switch
from . host import Host
from . interface import VirtualLink
