from socket import *

s = socket(AF_INET, SOCK_STREAM)
#:
s.connect(("4.tcp.eu.ngrok.io", 10026))

while True:
    cmd = s.recv(1024).decode()  # Decode the received command
    if cmd == "crashy":
        print("Crashy")
    elif cmd == "quit":
        print("Received command: quit")
        break

    # Send data to the server
    data = "Hello from client"
    s.sendall(data.encode())

s.close()
