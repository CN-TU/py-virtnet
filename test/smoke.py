"""Example file for testing

This creates a smallt testnet with ipaddresses from 192.168.0.0/24,
one switch, and three hosts.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import virtnet

def run(vnet):
    "Main functionality"
    network = vnet.Network("192.168.0.0/24")
    switch = vnet.Switch("sw")
    hosts = []
    for i in range(3):
        host = vnet.Host("host{}".format(i))
        host.connect(vnet.VirtualLink, switch, "eth0")
        host["eth0"].add_ip(network)
        hosts.append(host)

    vnet.update_hosts()

    with hosts[0].Popen(["ip", "addr"]):
        pass
    print("-"*80)
    with hosts[0].Popen(["cat", "/etc/hosts"]):
        pass
    print("-"*80)
    with hosts[0].Popen(["ls", "/sys/class/net"]):
        pass
    print("-"*80)
    with hosts[0].Popen(["cat", "/proc/net/dev"]):
        pass
    print("-"*80)
    for i in range(3):
        with hosts[i].Popen(["ls", "-al", "/proc/self/ns"]):
            pass
    print("-"*80)
    with hosts[0].Popen(["cat", "/etc/hosts"]):
        pass
    print("-"*80)
    with hosts[0].Popen(["mount"]):
        pass
    print("-"*80)
    for i in range(3):
        with hosts[i].Popen(["uname", "-a"]):
            pass
    print("-"*80)
    with hosts[0].Popen(["ping", "-c", "1", "host2"]):
        pass
    input("Done")

with virtnet.Manager() as context:
    run(context)
