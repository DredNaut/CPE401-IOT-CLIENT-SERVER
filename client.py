# Connection Oriented Server

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname, error
import sys
import errno
import datetime
import time
import hashlib
from threading import Thread

d = "\t"
Scode = "01"
user = sys.argv[1]
server_ip = sys.argv[2]
server_port = sys.argv[3]
FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
message = "heartbeat"
length = len(message)
message_size = str(length)

def register():
    print("REGISTER PACKET:")
    mac = raw_input("MAC:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    password = raw_input("PASSWORD:\t")
    packet = "REGISTER"+d+user+d+password+d+mac+d+ip+d+port
    return packet


def deregister():
    print("REGISTER PACKET:")
    mac = raw_input("MAC:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    password = raw_input("PASSWORD:\t")
    packet = "DEREGISTER"+d+user+d+password+d+mac+d+ip+d+port
    return packet


def login():
    print("LOGIN PACKET")
    password = raw_input("PASSWORD:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    packet = "LOGIN"+d+user+d+password+d+ip+d+port
    return packet


def logoff():
    print("LOGOFF PACKET")
    packet = "LOGOFF"+d+user
    return packet

def getHash(message):
    return hashlib.sha256(message).hexdigest()

def getTime():
    currentDT = datetime.datetime.now()
    return currentDT.strftime("%Y-%m-%d:%H:%M:%S")

# UDP PEER-TO-PEER

def query_server():
    packet = ""
    print("QUERY PACKET")
    target_device = raw_input("DEST. USER:\t")
    choice = raw_input("QUERY TYPE:\n(1) Lookup Device IP/PORT\n")
    if choice == 1:
        qcode = "01"
        packet = "QUERY"+d+qcode+d+user+d+getTime()+d+target_device
        print("Pinging {0}".format(user))
    else:
        print("Invalid choice")
    return packet

# Send the heartbeat to the server
def status():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 1994
    sock = socket(AF_INET, SOCK_DGRAM)
    while True:
        time.sleep(300)        
        print("Status Packet Sent")

        packet = "STATUS"+d+Scode+d+user+d+str(getTime())+d+message_size.encode('utf-8')+d+message
        sock.sendto(packet, (UDP_IP, UDP_PORT))

# Listen for messages
def listen():
    UDP_IP = "localhost"
    UDP_PORT = 1994

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        # buffer size is 1024 bytes
        #data, addr = sock.recvfrom(1024)
        data = str(sock.recv(1024)).encode("utf-8")
        print ("Received message:{0}".format(data))
        fields = data.split('\t')
        if fields[0] == "STATUS":
            print("Status Packet Received from device-id: {0}".format(fields[2]))
            response = "ACK"+d+"40"+d+user+d+str(getTime())+d+getHash(data)
            sock.sendto(response, (UDP_IP, UDP_PORT))
        elif fields[0] == "QUERY":
            print("QUERY packet received")
        else:
            print("Some other packet received")


# Start the listening and status threads
l_t = Thread(target=listen, args=())
l_t.daemon=True
l_t.start()
s_t = Thread(target=status, args=())
s_t.daemon=True
s_t.start()
while True:

    choice = int(raw_input("(1)\tRegister\n(2)\tDe-Register\n(3)\tLogin\n(4)\tLogoff\n(5)\tQuery Server\n(6)\tExit\nPlease Make a Selection: "))

    if choice == 1:
        raw_packet = register()
    elif choice == 2:
        raw_packet = deregister()
    elif choice == 3:
        raw_packet = login()
    elif choice == 4:
        raw_packet = logoff()
    elif choice == 5:
        raw_packet = query_server()
    elif choice == 6:
        sys.exit(0) 
    else:
        print("Incorrect input received.. Exiting")
        sys.exit(1)

    # Need each client to have a unique port number if using localhost
    (SERVER, PORT) = (server_ip, server_port)
    # Create the socket objects for tcp and udp sockets
    tcp_s = socket(AF_INET, SOCK_STREAM)
    udp_s = socket(AF_INET, SOCK_DGRAM)

    # Attempt to connect to the server
    try:
        tcp_s.connect((SERVER,PORT))

        tcp_s.send(raw_packet)
        #data = tcp_s.recv(1024)
        #print (data)
        tcp_s.close()

    # Catch if connection refused
    except error as e:
        if e.errno == errno.ECONNREFUSED:
            print ("Error connecting to the server.")

