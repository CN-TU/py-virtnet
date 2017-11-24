"""This module holds the iproute2 socket"""

import pyroute2.ipdb.main
import pyroute2.netlink.rtnl.tcmsg
from . import sched_netem_test

pyroute2.netlink.rtnl.tcmsg.plugins['netem'] = sched_netem_test

IPDB = pyroute2.ipdb.main.IPDB()
