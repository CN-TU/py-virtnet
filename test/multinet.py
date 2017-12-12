"""Example file for testing

This creates several small testnetworks and connects those via routers.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import collections
import virtnet

Star = collections.namedtuple('Star', ['router', 'switch', 'hosts'])

def star(vnet, name, numhosts, network):
    "create a star topology with a router, a switch, and some hosts"
    switch = vnet.Switch(name+"_sw", network=network)
    router = vnet.Router(name+"_router")
    router.connect(vnet.VirtualLink, switch, "eth0")
    hosts = []
    for i in range(numhosts):
        host = vnet.Host("{}_host{}".format(name, i))
        host.connect(vnet.VirtualLink, switch, "eth0")
        hosts.append(host)
    return Star(router, switch, hosts)


def run(vnet):
    "Main functionality"
    stars = []
    networks = []
    router_networks = []
    router = vnet.Router("central")
    for i in range(3):
        network = vnet.Network("192.168.{}.0/24".format(i), router=1)
        networks.append(network)
        net = star(vnet, "star{}".format(i), 3, network)
        router_network = vnet.Network("10.0.{}.0/24".format(i))
        router_networks.append(router_network)
        intf = router.connect(vnet.VirtualLink, net.router, "star{}".format(i), "up{}".format(i))
        intf.main.add_ip(router_network)
        intf.peer.add_ip(router_network)
        stars.append(net)

    vnet.simple_route()
    vnet.update_hosts()

    stars[0].hosts[0].Popen(["ping", "-c", "3", "star2_host2"]).wait()
    stars[0].hosts[0].Popen(["traceroute", "star2_host2"]).wait()
    input("Done")

with virtnet.Manager() as context:
    run(context)
