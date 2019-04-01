# Connection Oriented Server

from socket import socket, SHUT_RDWR, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname, error
import sys
import errno
import datetime
import time
import hashlib
import logging
from threading import Thread


def register():
    print("REGISTER PACKET:")
    mac = raw_input("MAC:\t")
    ip = raw_input("IP:\t")
    port = raw_input("PORT:\t")
    password = raw_input("PASSWORD:\t")
    packet = "REGISTER"+d+user+d+password+d+mac+d+ip+d+port
    return packet


def deregister():
    print("DEREGISTER PACKET:")
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


def query_server():
    packet = ""
    print("QUERY PACKET")
    target_device = raw_input("DEST. USER:\t")
    choice = raw_input("QUERY TYPE:\n(1) Lookup Device IP/PORT\n")
    if choice == "1":
        qcode = "01"
        packet = "QUERY"+d+qcode+d+user+d+getTime()+d+target_device
    else:
        print("Invalid choice")
    return packet

# UDP PEER-TO-PEER

def query_client():
    print("Querying Client")
    global udp_ip
    global udp_port
    target_device = raw_input("DEST. USER:\t")
    udp_ip = raw_input("DST IP:\t")
    udp_port = raw_input("DST PORT:\t")
    qcode = "01"
    packet = "QUERY"+d+qcode+d+user+d+udp_ip+d+str(listening_port)+d+getTime()+d+target_device
    return packet

# Send the heartbeat to the server
def status():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 1994
    tcp_s = socket(AF_INET, SOCK_DGRAM)
    tcp_s.connect((server_ip,int(server_port)))
    while True:
        time.sleep(180)        
        print("Status: Packet Sent")

        packet = "STATUS"+d+Scode+d+user+d+str(getTime())+d+message_size.encode('utf-8')+d+message
        tcp_s.send(packet)

# Listen for messages
def listen():
    UDP_IP = "localhost"

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, listening_port))

    while True:
        # buffer size is 1024 bytes
        #data, addr = sock.recvfrom(1024)
        data = str(sock.recv(1024)).encode("utf-8")
        logging.info("Received message:{0}".format(data))
        fields = data.split('\t')
        if fields[0] == "STATUS":
            logging.info("Status Packet Received from device-id: {0}".format(fields[2]))
            response = "ACK"+d+"40"+d+user+d+str(getTime())+d+getHash(data)
            sock.sendto(response, (UDP_IP, UDP_PORT))
        elif fields[0] == "QUERY":
            print("\nQUERY packet received check Activity.log for details")
            response = "DATA"+d+"01"+d+user+d+udp_ip+d+str(listening_port)+d+getTime()+d+str(len(user))+d+user
            sock.sendto(response, (fields[3], int(fields[4])))
        elif fields[0] == "DATA":
            print("\nDATA packet received check Activity.log for details")
            response = "ACK"+d+"50"+d+user+d+str(getTime())+d+getHash(data)
            sock.sendto(response, (fields[3], int(fields[4])))

if len(sys.argv) == 5:

    d = "\t"
    Scode = "01"
    user = sys.argv[1]
    server_ip = sys.argv[2]
    server_port = sys.argv[3]
    udp_ip = "127.0.0.1"
    udp_port = ""
    listening_port = int(sys.argv[4])
    message = "heartbeat"
    length = len(message)
    message_size = str(length)
    logging.basicConfig(filename='./log/Activity.log',level=logging.DEBUG)

# Start the listening and status threads
    # Listening Thread
    l_t = Thread(target=listen, args=())
    l_t.daemon=True
    l_t.start()
    # Status Thread
    s_t = Thread(target=status, args=())
    s_t.daemon=True
    s_t.start()
    while True:

        choice = int(raw_input("(1)\tRegister\n(2)\tDe-Register\n(3)\tLogin\n(4)\tLogoff\n(5)\tQuery Server\n(6)\tQuery Client\n(7)\tExit\nPlease Make a Selection: "))
        tcp_flag = True

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
            raw_packet = query_client()
            tcp_flag = False
        elif choice == 7:
            sys.exit(0) 
        else:
            print("Incorrect input received.. Exiting")
            tcp_s.close()
            sys.exit(1)

        # Need each client to have a unique port number if using localhost
        (SERVER, PORT) = (server_ip, int(server_port))
        # Create the socket objects for tcp and udp sockets
        tcp_s = socket(AF_INET, SOCK_STREAM)
        udp_s = socket(AF_INET, SOCK_DGRAM)

        if tcp_flag:
            # Attempt to connect to the server
            try:
                tcp_s.connect((SERVER,PORT))

                tcp_s.send(raw_packet)
                data = tcp_s.recv(1024)
                logging.info(data)

            # Catch if connection refused
            except error as e:
                if e.errno == errno.ECONNREFUSED:
                    print ("Error connecting to the server.")

        # Sending UDP query
        else:
            udp_s.sendto(raw_packet, (udp_ip, int(udp_port)))

else:
    print("USAGE:\npython client.py <device-id> <server-ip> <server-port> <listening port>")
