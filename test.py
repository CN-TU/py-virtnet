import virtnet.host
import virtnet.interface
from virtnet.iproute import IPDB

host = virtnet.host.Host("host")
intf = virtnet.interface.VirtualInterface("host0", IPDB, "eth0", host.ipdb)