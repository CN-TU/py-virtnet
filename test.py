import virtnet

def run(vnet):
    network = vnet.Network("192.168.0.0/24")
    switch = vnet.Switch("sw")
    for i in range(3):
        host = vnet.Host("host{}".format(i))
        host.connect(vnet.VirtualLink, switch, "eth0")
        host["eth0"].add_ip(network)

    input("Done")

with virtnet.Manager() as context:
    run(context)
