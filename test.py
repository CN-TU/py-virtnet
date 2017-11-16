import virtnet

def run():
    host = virtnet.Host("host")
    switch = virtnet.Switch("sw")
    host.connect(virtnet.VirtualLink, switch, "eth0")

    input("Done")

    host.stop()
    switch.stop()

run()
