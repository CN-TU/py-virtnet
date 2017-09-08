import virtnet
from virtnet.iproute import IPDB

host = virtnet.Host("host")
switch = virtnet.Switch("sw")
host.connect(switch, "eth0")

input("Done")

host.stop()
switch.stop()
