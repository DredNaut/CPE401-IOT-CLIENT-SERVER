# Connection Oriented Server

from socket import socket, AF_INET, SOCK_STREAM, gethostname
import sys

d = "\t"

def register():
    print("REGISTER PACKET:")
    mac = raw_input("MAC:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    user = raw_input("USER:\t")
    password = raw_input("PASSWORD:\t")
    packet = "REGISTER"+d+user+d+password+d+mac+d+ip+d+port
    return packet


def deregister():
    print("REGISTER PACKET:")
    mac = raw_input("MAC:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    user = raw_input("USER:\t")
    password = raw_input("PASSWORD:\t")
    packet = "DEREGISTER"+d+user+d+password+d+mac+d+ip+d+port
    return packet


def login():
    print("LOGIN PACKET")
    user = raw_input("USER:\t")
    password = raw_input("PASSWORD:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    packet = "LOGIN"+d+user+d+password+d+ip+d+port
    return packet


def logoff():
    print("LOGOFF PACKET")
    user = raw_input("USER:\t")
    packet = "LOGOFF"+d+user
    return packet

while True:

    choice = int(raw_input("(1)\tRegister\n(2)\tDe-Register\n(3)\tLogin\n(4)\tLogoff\n(5)\tExit\nPlease Make a Selection: "))

    if choice == 1:
        raw_packet = register()
    elif choice == 2:
        raw_packet = deregister()
    elif choice == 3:
        raw_packet = login()
    elif choice == 4:
        raw_packet = logoff()
    elif choice == 5:
        sys.exit(0) 
    else:
        sys.exit(1)

    (SERVER, PORT) = ('127.0.0.1', 1994)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((SERVER,PORT))

    s.send(raw_packet)
    data = s.recv(1024)
    print (data)
    s.close()
