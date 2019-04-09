"""Host module.

This module contains everything to represent a virtual host in it's own
network container.

Todo:
    * Implement like everything!
"""

import subprocess
import socket
import pathlib
import os
import errno
import shutil
from pyroute2.netns.nslink import NetNS
from pyroute2.netns import setns
import pyroute2.ipdb.main
import ipaddress
import collections
from . iproute import IPDB
from . container import InterfaceContainer
from . interface import VirtualInterface
from . context import Manager
from . import syscalls

class HostException(Exception):
    """Base Class for Host-based exceptions"""

class HostUpException(HostException):
    """Host is already running"""

class HostDownException(HostException):
    """Host is not running"""

class NamespaceExistsException(HostException):
    """Namespace with this name already exists"""

ETC_DIR = pathlib.Path('/etc')
NETNS_ETC_DIR = ETC_DIR / 'netns'

DEFAULT_HOSTS = b"""127.0.0.1	localhost.localdomain	localhost
::1		localhost.localdomain	localhost

"""


def _compatible_address (src_addr, dst_addr):
    ips = [ address.ip for address in dst_addr ]
    nets = [ address.network for address in src_addr ]
    try:
        return next( ip for ip in ips for net in nets if ip in net )
    except StopIteration:
        return None
    
    
def _setup_etc(name: str):
    hostdir = NETNS_ETC_DIR / name
    try:
        os.makedirs(str(hostdir))
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

    ret = {}

    hosts = hostdir / "hosts"
    hosts_etc = ETC_DIR / "hosts"
    hosts.write_bytes(DEFAULT_HOSTS)
    ret["hosts"] = (hosts, hosts_etc)

    return ret

def _remove_etc(name: str) -> None:
    shutil.rmtree(NETNS_ETC_DIR / name, ignore_errors=True)

class PhysicalHost(InterfaceContainer):
    """Physical Host.

    This is the default namespace.

    Args:
        name: Name for the host.

    Attributes:
        name: Name of the host.
    """
    def __init__(self, name: str = None, manager: Manager = None) -> None:
        self.__ns = None
        self.__ipdb = IPDB
        if name is None:
            name = socket.gethostname()
        super().__init__(name)

    @property
    def running(self) -> bool:
        """True if host is running"""
        return self.__ns is not None

    @property
    def ipdb(self) -> pyroute2.ipdb.main.IPDB:
        """Return host IPDB"""
        return self.__ipdb

    def start(self) -> None:
        """Start host

        Raises:
            HostUpException: If host is already running.
        """
        pass

    def Popen(self, *args, **kwargs): #pylint: disable=invalid-name
        """Popen inside the host"""

        return subprocess.Popen(*args, **kwargs)

    def stop(self) -> None:
        """Stop host

        Raises:
            HostDownException: If host is already stopped.
        """
        pass

    def set_hosts(self, hosts):
        pass

    def get_hostnames(self):
        return []


class Host(InterfaceContainer):
    """Host in a network container.

    This is a host in a networked container.

    Args:
        name: Name for the host, which is the name for the network namespace.

    Attributes:
        name: Name of the host, which is also the name of the network namespace.
    """
    def __init__(self, name: str, manager: Manager = None) -> None:
        self.__ns = None
        self.__ipdb = None
        self.__manager = manager
        self.__files = {}
        self.__hostnames = []
        super().__init__(name)

    def add_hostname(self, name: str) -> None:
        self.__hostnames.append(name)

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
        self.__files = _setup_etc(self.name)
        self.__ipdb = pyroute2.ipdb.main.IPDB(nl=self.__ns)
        self.__ipdb.interfaces["lo"].up().commit()
        if self.__manager is not None:
            self.__manager.register(self)

    def Popen(self, *args, **kwargs): #pylint: disable=invalid-name
        """Popen inside the host"""

        mounts = tuple((bytes(src), bytes(dst)) for src, dst in self.__files.values())
        def change_ns():
            """Setup the namespace"""
            # This is borrowed from iproute2 and looks more sane than pyroute2
            # Let's move ourselves to the target network namespace
            try:
                # Change to network namespace
                setns(self.name, flags=0)

                # Unshare the mount namespace (preparation for following steps)
                # Unshare UTS namespace for hostname
                syscalls.unshare(syscalls.CLONE_NEWNS|syscalls.CLONE_NEWUTS)

                # Make our mounts slave (otherwise unshare doesn't help with shared mounts)
                syscalls.mount(b"none", b"/", None, syscalls.MS_REC|syscalls.MS_SLAVE, None)

                # Mount sysfs that belongs to this network namespace
                syscalls.umount2(b"/sys", syscalls.MNT_DETACH)
                syscalls.mount(b"none", b"/sys", b"sysfs", 0, None)

                # Set the hostname
                socket.sethostname(self.name)

                # fake hosts files etc
                for src, dst in mounts:
                    syscalls.mount(src, dst, b"none", syscalls.MS_BIND, None)
            except Exception as err:
                print(err)
                raise
        return subprocess.Popen(*args, preexec_fn=change_ns, **kwargs)

    def stop(self) -> None:
        """Stop host

        Raises:
            HostDownException: If host is already stopped.
        """
        if self.__ns is None:
            raise HostDownException()
        self.__ipdb.release()
        self.__ipdb = None
        self.__ns.close()
        self.__ns.remove()
        _remove_etc(self.name)
        self.__ns = None
        if self.__manager is not None:
            self.__manager.unregister(self)

    def set_hosts(self, hosts):
        with self.__files["hosts"][0].open('wb') as hostfile:
            hostfile.write(DEFAULT_HOSTS)
            for host, address, hostnames in hosts:
                hostfile.write("{}\t{}\t{}\n".format(address, host, " ".join(hostnames)).encode())

    def get_hostnames(self):
        return [(self.name, address.ip, self.__hostnames)
                for interface in self.interfaces.values()
                for address in interface.addresses]

    def _find_gateway(self, addrtype):
        # search the network for any router and use it as default gateway
        for intf in self.interfaces.values():
            if not isinstance(intf, VirtualInterface):
                continue
            addresses = list(filter(lambda x: isinstance(x, addrtype), intf.addresses))
            intf_list = set([intf])
            visited = set([intf])
            while intf_list:
                peer, peerintf = intf_list.pop().peer()
                if peer.router:
                    gateway = _compatible_address (addresses, peerintf.addresses)
                    if gateway:
                        self.ipdb.routes.add({'dst': 'default', 'gateway': str(gateway)}).commit()
                        return 
                if peer.switch:
                    new_intfs = set(filter(
                        lambda x: x not in visited and isinstance(x, VirtualInterface),
                        peer.interfaces.values()
                    ))
                    intf_list.extend (new_intfs)
                    visited.extend (new_intfs)    
                    
        
    def remove_prohibited_routes(self):
        for intf in self.interfaces.values():
            if intf.route and not intf.route.allow_egress:
                for address in intf.addresses:
                    net = str(ipaddress.ip_network(str(address),strict=False))
                    self.ipdb.routes[net].remove().commit()
                    
    def find_routes(self):
        if {'dst': 'default', 'family': socket.AF_INET} not in self.ipdb.routes:
            self._find_gateway(ipaddress.IPv4Interface)
        if {'dst': 'default', 'family': socket.AF_INET6} not in self.ipdb.routes:
            self._find_gateway(ipaddress.IPv6Interface)
            
class Router(Host):
    """Router extends Host with some additional settings a router needs

    Args:
        name: Name for the host, which is the name for the network namespace.

    Attributes:
        name: Name of the host, which is also the name of the network namespace."""
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        # no simple way to open files in the network namespace :(
        self.Popen(["sysctl", "-w", "net.ipv4.ip_forward=1", "net.ipv6.conf.all.forwarding=1",
                    "net.ipv4.conf.default.rp_filter=0"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL).wait()

    @property
    def router(self) -> bool:
        """Return true if container is a router"""
        return True
        
    def _bfs(self, addrtype):
        node_list = collections.deque([(self,None,None)])
        visited = set([self])
        
        while node_list:
            node, routerAddresses, firsthop = node_list.pop()
            
            for intf in node.interfaces.values():
                if intf.route and not intf.route.allow_egress:
                    continue

                if node.router:
                    routerAddresses = list(filter(lambda x: isinstance(x, addrtype), intf.addresses))
                    for address in routerAddresses:
                        net = str(ipaddress.ip_network(str(address),strict=False))
                        if net not in self.ipdb.routes and node != self:
                            self.ipdb.routes.add({'dst': net, 'gateway': firsthop}).commit()
                if not isinstance(intf, VirtualInterface):
                    continue
                peer, peerintf = intf.peer()
                if peer in visited or not (peer.router or peer.switch):
                    continue
                if peer.switch:
                    # append to right side of deque to find routers on local subnet first
                    node_list.append((peer, routerAddresses, firsthop))
                else:
                    # require address to be in the same subnet as previous router
                    address = _compatible_address(routerAddresses, peerintf.addresses)
                    if not address:
                        continue
                    routeFirsthop = firsthop if firsthop else str(address)
                    node_list.appendleft((peer, None, routeFirsthop))
                visited.add(peer)
        
    def find_routes(self):
        self._bfs (ipaddress.IPv4Interface)
        self._bfs (ipaddress.IPv6Interface)

