import socket 
import select

BUFFER_SIZE = 1024


def send_packet_recv(ip, port, packet):
             
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(packet)
    data = s.recv(BUFFER_SIZE)
    s.close()
    return (data)

def send_packet_recv_timeout(ip, port, packet, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((ip, port))
    s.send(packet)
    s.setblocking(0)
    ready = select.select([s], [], [], timeout)
    if ready[0]:
        data = s.recv(BUFFER_SIZE)
    s.close()

    return (data)