import socket 

TCP_IP = '79.79.1.47'
TCP_PORT = 2022
BUFFER_SIZE = 1024
MESSAGE = b'\x00\xff\x00\xff.\xe1@@\x00\t\x00l\x01\x00\x12\x01\x00\x02\x00\x01\x01\x00\x14\x00\x00\x00\x08\x00\x00\x00\x00x\x01\x02\x00\x12\x01\x00\x00iy\x01\x01\x00\x00\x00\x010\x00\x00\x00\x00\x00;\x02\x00\x12\x01\x00\x00iz\x01\x01\x00\x00\x00\x010\x00\x00\x00\x00\x00<\x02\x00\x12\x01\x00\x00i{\x01\x01\x00\x00\x00\x010\x00\x00\x00\x00\x00=\x08\x00\x12\x01\x0512.00\x010\x0512.00\x00\x00\x00\x0f\x00\x00'
              
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
print (data)
s.close()

