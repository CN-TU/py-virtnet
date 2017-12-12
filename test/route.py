"""Example file for testing

This creates a smallt testnet with two hosts belonging to two distinct networks, which are connected
via seperate switches with a router.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import virtnet

def run(vnet):
    "Main functionality"
    network1 = vnet.Network("192.168.0.0/24", router=1)
    network2 = vnet.Network("10.0.0.0/24", router=2)
    switch1 = vnet.Switch("sw1", network=network1)
    switch2 = vnet.Switch("sw2", network=network2)
    host1 = vnet.Host("host1")
    host2 = vnet.Host("host2")
    router = vnet.Router("router")
    host1.connect(vnet.VirtualLink, switch1, "eth0")
    router.connect(vnet.VirtualLink, switch1, "eth0")
    router.connect(vnet.VirtualLink, switch2, "eth1")
    host2.connect(vnet.VirtualLink, switch2, "eth0")

    vnet.update_hosts()

    host1.Popen(["ping", "-c", "3", "host2"]).wait()
    host1.Popen(["traceroute", "host2"]).wait()
    input("Done")

with virtnet.Manager() as context:
    run(context)
