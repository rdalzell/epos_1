import socket 

BUFFER_SIZE = 1024


def send_packet_recv(ip, port, packet):
             
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(packet)
    data = s.recv(BUFFER_SIZE)
    s.close()
    return (data)

