from time import sleep
import random
from socket import *
from contextlib import closing
from inspect import signature
from typing import List

from threading import Thread

import ifaddr
from zeroconf import (ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf,
                      ZeroconfServiceTypes)

from netifaces import interfaces, ifaddresses

import signal
import sys


def signal_handler(sig, frame):
    print('KEYboard InterruptedError')
    cleanup()
    sys.exit(0)


def cleanup():
    zeroconf.close()


signal.signal(signal.SIGINT, signal_handler)


for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(
        ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
    print('%s: %s' % (ifaceName, ', '.join(addresses)))


class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service {} of type {} removed".format(name, type))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

        # https://stackoverflow.com/a/51596612/8608146
        print("Address", inet_ntoa(info.address), info.port)

        # Thread(target=client_handler, args=(info,)).start()


# datax = []


# def client_handler(info: ServiceInfo):
#     with closing(socket(AF_INET, SOCK_DGRAM)) as s:
#         s = socket(AF_INET, SOCK_DGRAM)
#         print(info.address, info.port)
#         s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#         # s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#         # d, x = s.accept()
#         # print(d, x)
#         s.bind((inet_ntoa(info.address), info.port))
#         # datax.append(s)
#         # get_level_one_info(info)
#         # pass
#         while True:
#             # print("Waiting..")
#             m = s.recvfrom(1024)
#             print(m)

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


def get_level_one_info(obj):
    """Prints all the properties of an object"""
    print("\n"+"---"*9)
    for x in dir(obj):
        if not x.startswith("_"):
            data = getattr(obj, x)
            if callable(data):
                # https://stackoverflow.com/a/41188411/8608146
                sig = signature(data)
                params = sig.parameters

                if len(params) == 0:
                    print(x, ":", data())

            else:
                print(x, ":", data)


# print(get_all_addresses())
# print(get_local_ip())

print(gethostname())
print(gethostbyname(gethostname()))


# print(ZeroconfServiceTypes.find())


zeroconf = Zeroconf()

send_port = find_free_port()
local_ip = get_local_ip()

# register a service
zeroconf.register_service(ServiceInfo(
    "_coolapp._udp.local.",
    "{}._coolapp._udp.local.".format(f"pc-{random.randint(0, 255)}"),
    inet_aton(local_ip), send_port, 0, 0,
    # this is the txt record
    properties={"data": "device"}
))

listener = MyListener()
browser = ServiceBrowser(zeroconf, "_coolapp._udp.local.", listener)


def do_shot():
    print("do_shot")
    s = socket(AF_INET, SOCK_DGRAM)
    # s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s.bind(('', send_port))
    print(s.getsockname())
    # s.listen(1)
    # d, x = s.accept()
    # print(d, x)
    while True:
        try:
            m = s.recv(1024)
            print(m)
        except KeyboardInterrupt:
            cleanup()
            exit(1)


z = Thread(target=do_shot, args=())
z.start()

# do_shot()
# print("S")

try:
    x = 'c'
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    while x != 'q':
        x = input("Press q to exit...\n\n")
        # print(x)
        s.sendto(x.encode('utf8'), ('255.255.255.255', send_port))

finally:
    zeroconf.close()
    # z._delete()
    # for x in datax:
    #     print(x)
    #     x.close()

# command arp -a gives some stuff
# https://stackoverflow.com/a/47620499/8608146
