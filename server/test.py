from socket import *
from time import sleep

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
# s.bind(('', 9000))

# while True:
#     m = s.recvfrom(1024)
#     print(m[0])
while True:
    sleep(2)
    print('sendto')
    s.sendto(b'this is testing', ('255.255.255.255', 8020))
