import sys
import socket
import time

socketCar = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketCar.connect(("192.168.0.101", 9000))
print("connected")

cmd="U"
i=0
while True:
    try:
        i+=1
        print(i, cmd)
        socketCar.send((cmd+"\n").encode())
        time.sleep(.05)
        # if i > 100: break
    except KeyboardInterrupt:
        break
socketCar.close()
