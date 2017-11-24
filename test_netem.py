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

def run(vnet):
    "Main functionality"

    x = np.linspace(-X, X, SAMPLES)
    y = norm.pdf(x, loc=-5)+norm.pdf(x, loc=5, scale=3)
    area = np.trapz(y)*(2*X)/SAMPLES

    network = vnet.Network("192.168.0.0/24")
    switch = vnet.Switch("sw")
    hosts = []
    for i in range(2):
        host = vnet.Host("host{}".format(i))
        host.connect(vnet.VirtualLink, switch, "eth0")
        host["eth0"].add_ip(network)
        hosts.append(host)
    switch["host00"].tc('add', 'netem', delay=DELAY, jitter=SIGMA, dist=y)

    vnet.update_hosts()

    with hosts[0].Popen(["ping", "-q", "-c", "1", "host1"]):
        pass

    res = []
    with hosts[0].Popen(["ping", "-c", "1000", "-i", "0", "host1"], stdout=subprocess.PIPE) as ping:
        for line in ping.stdout:
            line = line.rsplit(b'time=',1)
            if len(line) != 2:
                continue 
            res.append(float(line[1][:-4]))
    plt.plot(x/(2*X)*8*SIGMA/1000+DELAY/1000, y/area)
    print(min(res), max(res))
    print(np.mean(res), np.std(res, ddof=1))
    plt.hist(res, density=True)
    plt.show()

with virtnet.Manager() as context:
    run(context)
