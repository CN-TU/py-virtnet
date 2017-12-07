"""Example file for testing

This creates a smallt testnet with ipaddresses from 192.168.0.0/24,
one switch, and three hosts.
"""

import virtnet

def run(vnet):
    "Main functionality"
    network1 = vnet.Network("192.168.0.0/24")
    network2 = vnet.Network("10.0.0.0/24")
    switch1 = vnet.Switch("sw1")
    switch2 = vnet.Switch("sw2")
    host1 = vnet.Host("host1")
    host2 = vnet.Host("host2")
    router = vnet.Router("router")
    host1.connect(vnet.VirtualLink, switch1, "eth0")
    router.connect(vnet.VirtualLink, switch1, "eth0")
    router.connect(vnet.VirtualLink, switch2, "eth1")
    host2.connect(vnet.VirtualLink, switch2, "eth0")
    router["eth0"].add_ip(network1)
    host1["eth0"].add_ip(network1)
    router["eth1"].add_ip(network2)
    host2["eth0"].add_ip(network2)

    host1.ipdb.routes.add({'dst': 'default', 'gateway': '192.168.0.1'}).commit()

    host2.ipdb.routes.add({'dst': 'default', 'gateway': '10.0.0.1'}).commit()

    vnet.update_hosts()

    host1.Popen(["ping", "-c", "3", "host2"]).wait()
    input("Done")

with virtnet.Manager() as context:
    run(context)
