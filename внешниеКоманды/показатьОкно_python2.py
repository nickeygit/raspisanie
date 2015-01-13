import socket
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.sendto('vidimostb', ('127.0.0.1', 50000))