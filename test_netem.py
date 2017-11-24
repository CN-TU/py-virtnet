"""Example file for testing

This creates a smallt testnet with ipaddresses from 192.168.0.0/24,
one switch, and three hosts.
"""

import subprocess
import matplotlib.pyplot as plt
import virtnet

import numpy as np
from scipy.stats import norm


DELAY = 10000
SIGMA = 2000
SAMPLES = 1000
X = 10
NUMPING = 1000

def run(vnet):
    "Main functionality"

    print("Calculating pdf...")

    x = np.linspace(-X, X, SAMPLES)
    y = norm.pdf(x, loc=-5)+norm.pdf(x, loc=5, scale=3)
    area = np.trapz(y)*(2*X)/SAMPLES

    print("Building network...")
    network = vnet.Network("192.168.0.0/24")
    switch = vnet.Switch("sw")
    hosts = []
    for i in range(2):
        host = vnet.Host("host{}".format(i))
        host.connect(vnet.VirtualLink, switch, "eth0")
        host["eth0"].add_ip(network)
        hosts.append(host)
    hosts[0]["eth0"].tc('add', 'netem', delay=DELAY, jitter=SIGMA, dist=y)

    vnet.update_hosts()

    print("Doing ping...")

    with hosts[0].Popen(["ping", "-q", "-c", "1", "host1"], stdout=subprocess.DEVNULL):
        pass

    res = []
    pings = 0
    print(' '*40+'|'+'\b'*41, end='', flush=True)
    with hosts[0].Popen(["ping", "-c", str(NUMPING), "-i", "0", "host1"], stdout=subprocess.PIPE) as ping:
        for line in ping.stdout:
            line = line.rsplit(b'time=', 1)
            if len(line) != 2:
                continue
            pings += 1
            if not pings%(NUMPING/40):
                print('.', end='', flush=True)
            res.append(float(line[1][:-4]))
    plt.plot(x/X*4*SIGMA/1000+DELAY/1000, y/area, label='pdf of setting')

    print("Done")
    print()

    print("min={} max={}".format(min(res),max(res)))
    print("mean={} std={}".format(np.mean(res), np.std(res, ddof=1)))
    plt.hist(res, density=True, label='result histogram')
    plt.ylabel('fraction of packets')
    plt.xlabel('time [ms]')
    plt.legend()
    plt.show()

with virtnet.Manager() as context:
    run(context)
