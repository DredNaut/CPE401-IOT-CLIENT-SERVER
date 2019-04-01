# NAME:             server.py
# AUTHOR:           Jared Knutson
# DATE:             25FEB2019
# DESCRIPTION:      Connection Oriented Server


from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import datetime
import sqlite3
import hashlib
import logging
from threading import Thread
import sys



# CLASS:        AckPacket
# DESCRIPTION:  Class which handles the client requests.
class AckPacket:

# FUNCTION:     __init__
# DESCRIPTION:  Parameterized Constructor
    def __init__ (self,data):
        self.data = data
        fields = data.split('\t')
        if len(fields) > 1:
            if fields[0] == "REGISTER" or fields[0] == "DEREGISTER":
                self.p_type = fields[0]
                self.user = fields[1]
                self.password = fields[2]
                self.mac = fields[3]
                self.ip = fields[4]
                self.port = fields[5]

            elif fields[0] == "LOGIN": 
                self.p_type = fields[0]
                self.user = fields[1]
                self.password = fields[2]
                self.ip = fields[3]
                self.port = fields[4]

            elif fields[0] == "LOGOFF":
                self.p_type = fields[0]
                self.user = fields[1]

            elif fields[0] == "DATA":
                self.p_type = fields[0]
                self.d_code = fields[1]
                self.user = fields[2]
                self.time = fields[3]
                self.length = fields[4]
                self.message = fields[5]

            elif fields[0] == "QUERY":
                self.p_type = fields[0]
                self.q_code = fields[1]
                self.user = fields[2]
                self.time = fields[3]
                self.target_device = fields[4]

            elif fields[0] == "ACK":
                self.p_type = fields[0]
                logging.info(self.data)

            elif fields[0] == "STATUS":
                self.p_type = fields[0]
                self.user = fields[2]
                
            else:
                logging.error(self.data)


# FUNCTION:     generateAck
# DESCRIPTION:  Check if the device is already in the registrar file
    def generateAck(self):

        self.setTime()
        self.setHash()
        print (self.data)

        if self.p_type == "REGISTER":
            response = self.parseRegistration()
            response = "ACK"+d+self.code+d+self.user+d+self.time+d+self.hash

        elif self.p_type == "DEREGISTER": 
            response = self.parseDeregistration()
            response = "ACK"+d+self.code+d+self.user+d+self.time+d+self.hash

        elif self.p_type == "LOGIN": 
            response = self.parseLogin()
            response = "ACK"+d+self.code+d+self.user+d+self.time+d+self.hash

        elif self.p_type == "LOGOFF": 
            response = self.parseLogoff()
            response = "ACK"+d+self.code+d+self.user+d+self.time+d+self.hash

        elif self.p_type == "DATA": 
            response = self.parseData()

        elif self.p_type == "QUERY": 
            response = self.parseQuery()

        elif self.p_type == "STATUS":
            response = "ACK\t40"+d+self.user+d+self.time+d+self.hash

        else:
            print("")

        return response


# FUNCTION:     setHash
# DESCRIPTION:  Check if the device is already in the registrar file
    def setHash(self):
        self.hash = hashlib.sha256(self.data).hexdigest()


# FUNCTION:     setTime
# DESCRIPTION:  Check if the device is already in the registrar file
    def setTime(self):
        currentDT = datetime.datetime.now()
        self.time = currentDT.strftime("%Y-%m-%d:%H:%M:%S")
        

# FUNCTION:     parseRegister
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseRegistration(self):
        logging.info("Register Packet Received")
        entry = [self.user,self.mac,self.ip,self.password]
        if self.auditRegistration() == False:
            logging.info("Adding the user to the db")
            self.setRegistration()
        elif self.code == "02":
            logging.info("Updating IP")
            self.removeRegistration()


# FUNCTION:     parseDeregister
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseDeregistration(self):
        logging.info("De-Register Packet Received")
        if self.auditDeregistration() == True:
            logging.info("User is in the register, removing the user")
            self.removeRegistration()
        else:
            logging.info("Deregistration failed: %s" % (self.code))


# FUNCTION:     parseLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseLogin(self):
        logging.info("Login Packet Received")
        if self.auditLogin() == True:
            self.setLogin()



# FUNCTION:     parseLogoff
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseLogoff(self):
        logging.info("Logoff Packet Received")
        if self.auditLogin() == False:
            self.setLogoff()


# FUNCTION:     parseData
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseData(self):
        logging.info("Data Packet Received")
        response = "ACK\t50\tserver\t"+self.time+d+self.hash
        return response

    def parseQuery(self):
        logging.info("Query Packet Received")
        # Query for IP and Port
        if self.q_code == "01":
            if auditQuery(self.target_device):
                logging.info("User found and logged in")
                connection = sqlite3.connect("./iot_server.db")
                cursor = connection.cursor()

                format_str0 = """SELECT ip,port FROM registrar WHERE username LIKE '{username}'""".format(username=self.user)
                cursor.execute(format_str0)
                mydata = cursor.fetchall()
                ip,port = mydata[0]
                message = ip+d+port
                response = "DATA"+d+"01"+d+self.user+d+self.time+d+str(len(message))+d+message

            elif userExists(self.user):
                logging.error("User is not logged in")
                response = "DATA"+d+"12"+d+self.user+d+self.time+d+str(len(self.target_device))+d+self.target_device
            else:
                logging.error("User not found")
                response = "DATA"+d+"11"+d+self.user+d+self.time+d+str(len(self.target_device))+d+self.target_device
        else:
            logging.error("Query Type Not Recognized")
        return response



# FUNCTION:     setRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def setRegistration(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        new_entry = (self.user, self.mac, self.ip, self.password,self.port)
        format_str = """INSERT INTO registrar (username, mac, ip, password,port)
        VALUES (?,?,?,?,?);"""

        try:
            with connection:
                cursor.execute(format_str,new_entry)
        except sqlite3.IntegrityError:
            logging.info("Record already exists")
        finally:
            connection.commit()
            connection.close()


# FUNCTION:     removeRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def removeRegistration(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str = """DELETE FROM registrar WHERE username LIKE '{username}' AND password LIKE '{password}';""".format(username=self.user,password=self.password)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            logging.info("Record not found")
        finally:
            connection.commit()
            connection.close()


# FUNCTION:     setLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def setLogin(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str = """update registrar set active = 1 where username LIKE '{username}'""".format(username=self.user)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            logging.warning("Record not found")
        finally:
            logging.info("Setting User to active")
            connection.commit()
            connection.close()


# FUNCTION:     setLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def setLogoff(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str = """update registrar set active = 0 where username LIKE '{username}'""".format(username=self.user)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            logging.warning("Record not found")
        finally:
            self.code = "80"
            logging.info("Setting User to inactive")
            connection.commit()
            connection.close()


# FUNCTION:     auditLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditLogin(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND password LIKE '{password}'""".format(username=self.user,password=self.password)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND active==0""".format(username=self.user)

        cursor.execute(format_str0)
        if cursor.fetchone():
            logging.info("Found Credentials for user")
            cursor.execute(format_str1)
            if cursor.fetchone():
                self.code = "70"
                connection.close()
                return True
            else:
                logging.warning("User is already logged in")
                self.code = "31"
                connection.close()
                return False
        else:
            logging.warning("Could not Login user")
            self.code = "31"
            connection.close()
            return False

# FUNCTION:     auditRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditRegistration(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}' AND ip LIKE '{ip}';""".format(username=self.user,mac=self.mac,ip=self.ip)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}';""".format(username=self.user,mac=self.mac)
        format_str2 = """SELECT * FROM registrar WHERE ip LIKE '{ip}';""".format(ip=self.ip)
        format_str3 = """SELECT * FROM registrar WHERE mac LIKE '{mac}';""".format(mac=self.mac)

        cursor.execute(format_str0)
        if cursor.fetchone():
            logging.info("Register Found Exact")
            self.code = "01"
            connection.close()
            return True
        else:
            cursor.execute(format_str1)
            if cursor.fetchone():
                logging.info("IP needs to be updated")
                self.code = "02"
                connection.close()
                return True
            else:
                cursor.execute(format_str3)
                if cursor.fetchone():
                    logging.info("MAC reused")
                    self.code = "13"
                    connection.close()
                    return True
                else:
                    logging.info("No match, user not registered")
                    self.code = "00"
                    connection.close()
                    return False
            

# FUNCTION:     auditDeregistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditDeregistration(self):
        connection = sqlite3.connect("./iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}' AND ip LIKE '{ip}' AND password LIKE '{password}';""".format(username=self.user,mac=self.mac,ip=self.ip,password=self.password)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND (mac LIKE '{mac}' OR ip LIKE '{ip}');""".format(username=self.user,mac=self.mac,ip=self.ip)

        cursor.execute(format_str0)
        if cursor.fetchone():
            logging.info("Entry Found, Removing")
            self.code = "20"
            connection.close()
            return True
        else:
            cursor.execute(format_str1)
            if cursor.fetchone():
                logging.info("User registered to another ip or mac cannot remove")
                self.code = "30"
                connection.close()
                return False
            else:
                logging.info("Mac or User not registered")
                self.code = "21"
                connection.close()
                return False

def printDatabase():
    connection = sqlite3.connect("./iot_server.db")
    cursor = connection.cursor()

    format_str0 = """SELECT * FROM registrar WHERE 1=1"""

    cursor.execute(format_str0)
    print(cursor.fetchall())
    connection.close()


def auditQuery(user):
    connection = sqlite3.connect("./iot_server.db")
    cursor = connection.cursor()

    format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND active==1""".format(username=user)

    cursor.execute(format_str0)
    if cursor.fetchone():
        logging.info("Found Credentials for user")
        connection.close()
        return True
    else:
        connection.close()
        return False
    
def userExists(user):
    connection = sqlite3.connect("./iot_server.db")
    cursor = connection.cursor()

    format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}'""".format(username=user)

    cursor.execute(format_str0)
    if cursor.fetchone() is not None:
        logging.info("Found Credentials for user")
        connection.close()
        return True
    else:
        connection.close()
        return False

def listen_tcp(sock):
    while True:
        sock, addr = s.accept()
        #logging.info(("connection from %s" addr))
        data = sock.recv(1024)
        logging.info(data)
        new_ack = AckPacket(data)
        response = new_ack.generateAck()
        logging.info("RECV: "+data)
        print("\nReceived TCP packet check Activity.log for details")
        logging.info("SEND: "+response)
        sock.send(response) # echo
        sock.close()

def listen_udp(sock):
    sock.bind(("127.0.0.1", server_port))
    while True:
        data = sock.recv(1024)
        fields = data.split('\t')
        logging.info(data)
        new_ack = AckPacket(data)
        response = new_ack.generateAck()
        logging.info("RECV: "+data)
        print("\nReceived UDP packet check Activity.log for details")
        logging.info("SEND: "+response)
        if fields[0] == "ACK":
            sock.send(response) # echo
            sock.close()


def sendQuery(user):
    connection = sqlite3.connect("./iot_server.db")
    current = datetime.datetime.now()
    currentDT = current.strftime("%Y-%m-%d:%H:%M:%S")
    query = "QUERY\t01\tserver\t127.0.0.1\t1994\t"+currentDT+d+user

    cursor = connection.cursor()
    format_str0 = """SELECT port FROM registrar WHERE username LIKE '{username}'""".format(username=user)

    cursor.execute(format_str0)
    dst_port = cursor.fetchall()[0][0]
    print(dst_port)

    (SERVER, PORT) = ('127.0.0.1', int(dst_port))
    s = socket(AF_INET, SOCK_DGRAM)
    s.sendto(query, (SERVER, PORT))
    s.close()

if len(sys.argv) == 2:
# Logging settings
    server_port = int(sys.argv[1])
    d = '\t'
    logging.basicConfig(filename='./log/Activity.log',level=logging.DEBUG)
    open("./log/Activity.log","w+").close()

# FUNCTION:     Main
    s = socket(AF_INET, SOCK_STREAM)
    o = socket(AF_INET, SOCK_DGRAM)
    s.bind(('127.0.0.1', server_port))
    s.listen(5) # max queued connections
    t = Thread(target=listen_tcp, args=(s,))
    t.daemon=True
    t.start()
    r = Thread(target=listen_udp, args=(o,))
    r.daemon=True
    r.start()
    while True:
        choice = raw_input("(1)\tSend Query\n(2)\tPrint Database\n(3)\tExit\nPlease Make a Selection: ")
        if choice == "1":
            user = raw_input("Enter the user you would like to query: ")
            if auditQuery(user) == True:
                logging.info("Sending Query")
                sendQuery(user)
            else:
                logging.info("User is not logged in or no user exists")
        elif choice == "2":
            printDatabase()
        else:
            s.close()
            sys.exit(0)

else:
    print("USAGE:\npython server.py <server port>")
