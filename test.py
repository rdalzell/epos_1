import pack
import socket
import select



TCP_IP = '79.79.1.47'
TCP_PORT = 2022
BUFFER_SIZE = 1024
RECEIVE_TIMEOUT = 20

def send_order(order):

    packet = pack.create_epos_packet(order)
    response = send_packet(packet)
    return (pack.decode_response(response))

    

def send_packet(packet):
               
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(packet)
    s.setblocking(0)
    ready = select.select([s], [], [], RECEIVE_TIMEOUT)
    if ready[0]:
        data = s.recv(BUFFER_SIZE)
    s.close()

    return (data)

