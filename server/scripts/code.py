import random
from contextlib import closing
from socket import *
from threading import Thread
from typing import List

import ifaddr
from zeroconf import (ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf,
                      ZeroconfServiceTypes)

class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service {} of type {} removed".format(name, type))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

        # https://stackoverflow.com/a/51596612/8608146
        print("Address", inet_ntoa(info.address), info.port)

        Thread(target=client_handler, args=(info,)).start()


def client_handler(info: ServiceInfo):
    with closing(socket(AF_INET, SOCK_DGRAM)) as s:
        print(info.address, info.port)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(('', info.port))
        while True:
            print("Waiting..", s.getsockname())
            m = s.recvfrom(1024)
            print(m)

# https://stackoverflow.com/a/45690594/8608146


def find_free_port():
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        return s.getsockname()[1]

# https://github.com/p-sanches/somabits/blob/d581abaab6f045d65a774a78fbb43e232cf6f8da/somoserver/SomoServer/ZeroConf.py#L42


def get_all_addresses() -> List[str]:
    return list(set(
        addr.ip
        for iface in ifaddr.get_adapters()
        for addr in iface.ips
        # Host only netmask 255.255.255.255
        if addr.is_IPv4 and addr.network_prefix != 32
    ))


def get_local_ip(starts_with="192"):
    list_ip = get_all_addresses()
    local_ip = [i for i in list_ip if i.startswith(starts_with)]
    return local_ip[0]


print(get_all_addresses())
print(get_local_ip())

print(gethostname())
print(gethostbyname(gethostname()))

zeroconf = Zeroconf()

send_port = find_free_port()
local_ip = get_local_ip()

# assign a random name to this service
name = "pc-" + str(random.randint(0, 100))

# register a service
zeroconf.register_service(ServiceInfo(
    "_coolapp._udp.local.",
    "{}._coolapp._udp.local.".format(name),
    inet_aton(local_ip), send_port, 0, 0,
    # this is the txt record
    properties={"data": "device"}
))

listener = MyListener()
browser = ServiceBrowser(zeroconf, "_coolapp._udp.local.", listener)


try:
    std_response = ''
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    while std_response != 'q':
        std_response = input("Press q to exit...\n\n")
        # print(x)
        s.sendto(std_response.encode('utf8'), ('255.255.255.255', send_port))

finally:
    zeroconf.close()
