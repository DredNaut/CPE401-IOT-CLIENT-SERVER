# NAME:             server.py
# AUTHOR:           Jared Knutson
# DATE:             25FEB2019
# DESCRIPTION:      Connection Oriented Server


from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sqlite3
import hashlib
import logging
from threading import Thread
import sys

# Logging settings
FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

d = '\t'

def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(FORMAT)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Set up file loggers
activity_logger = setup_logger('Activity', './log/Activity.log')
error_logger = setup_logger('Error', './log/Error.log')



# CLASS:        AckPacket
# DESCRIPTION:  Class which handles the client requests.
class AckPacket:

# FUNCTION:     __init__
# DESCRIPTION:  Parameterized Constructor
    def __init__ (self, p_type="", user="", password="", mac="", ip="", port="", raw=""):
        self.p_type = p_type
        self.raw = raw
        self.user = user
        self.password = password
        self.mac = mac
        self.ip = ip
        self.port = port


# FUNCTION:     generateAck
# DESCRIPTION:  Check if the device is already in the registrar file
    def generateAck(self):

        self.setTime()
        self.setHash()

        if self.p_type == "REGISTER":
            response = self.parseRegistration()

        elif self.p_type == "DEREGISTER": 
            response = self.parseDeregistration()

        elif self.p_type == "LOGIN": 
            response = self.parseLogin()

        elif self.p_type == "LOGOFF": 
            response = self.parseLogoff()

        elif self.p_type == "DATA": 
            response = self.parseData()

        else:
            print("")

        response = "ACK"+d+self.code+d+self.user+d+self.time+d+self.hash

        return response


# FUNCTION:     setHash
# DESCRIPTION:  Check if the device is already in the registrar file
    def setHash(self):
        self.hash = hashlib.sha256(self.raw).hexdigest()


# FUNCTION:     setTime
# DESCRIPTION:  Check if the device is already in the registrar file
    def setTime(self):
        currentDT = datetime.datetime.now()
        self.time = currentDT.strftime("%Y-%m-%d:%H:%M:%S")
        

# FUNCTION:     parseRegister
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseRegistration(self):
        activity_logger.info("Register Packet Received")
        entry = [self.user,self.mac,self.ip,self.password]
        if self.auditRegistration() == False:
            activity_logger.info("Adding the user to the db")
            self.setRegistration()
        elif self.code == "02":
            activity_logger.info("Updating IP")
            self.removeRegistration()


# FUNCTION:     parseDeregister
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseDeregistration(self):
        activity_logger.info("De-Register Packet Received")
        if self.auditDeregistration() == True:
            activity_logger.info("User is in the register, removing the user")
            self.removeRegistration()
        else:
            activity_logger.info("Deregistration failed: %s" % (self.code))


# FUNCTION:     parseLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseLogin(self):
        activity_logger.info("Login Packet Received")
        if self.auditLogin() == True:
            self.setLogin()



# FUNCTION:     parseLogoff
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseLogoff(self):
        activity_logger.info("Logoff Packet Received")
        if self.auditLogin() == False:
            self.setLogoff()


# FUNCTION:     parseData
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseData(self):
        activity_logger.info("Data Packet Received")


# FUNCTION:     setRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def setRegistration(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        new_entry = (self.user, self.mac, self.ip, self.password)
        format_str = """INSERT INTO registrar (username, mac, ip, password)
        VALUES (?,?,?,?);"""

        try:
            with connection:
                cursor.execute(format_str,new_entry)
        except sqlite3.IntegrityError:
            activity_logger.info("Record already exists")
        finally:
            connection.commit()
            connection.close()


# FUNCTION:     removeRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def removeRegistration(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str = """DELETE FROM registrar WHERE username LIKE '{username}' AND password LIKE '{password}';""".format(username=self.user,password=self.password)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            activity_logger.info("Record not found")
        finally:
            connection.commit()
            connection.close()


# FUNCTION:     setLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def setLogin(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str = """update registrar set active = 1 where username LIKE '{username}'""".format(username=self.user)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            logging.warning("Record not found")
        finally:
            activity_logger.info("Setting User to active")
            connection.commit()
            connection.close()


# FUNCTION:     setLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def setLogoff(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str = """update registrar set active = 0 where username LIKE '{username}'""".format(username=self.user)

        try:
            with connection:
                cursor.execute(format_str)
        except sqlite3.IntegrityError:
            logging.warning("Record not found")
        finally:
            self.code = "80"
            activity_logger.info("Setting User to inactive")
            connection.commit()
            connection.close()


# FUNCTION:     auditLogin
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditLogin(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND password LIKE '{password}'""".format(username=self.user,password=self.password)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND active==0""".format(username=self.user)

        cursor.execute(format_str0)
        if cursor.fetchone():
            activity_logger.info("Found Credentials for user")
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
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}' AND ip LIKE '{ip}';""".format(username=self.user,mac=self.mac,ip=self.ip)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}';""".format(username=self.user,mac=self.mac)
        format_str2 = """SELECT * FROM registrar WHERE ip LIKE '{ip}';""".format(ip=self.ip)
        format_str3 = """SELECT * FROM registrar WHERE mac LIKE '{mac}';""".format(mac=self.mac)

        cursor.execute(format_str0)
        if cursor.fetchone():
            activity_logger.info("Register Found Exact")
            self.code = "01"
            connection.close()
            return True
        else:
            cursor.execute(format_str1)
            if cursor.fetchone():
                activity_logger.info("IP needs to be updated")
                self.code = "02"
                connection.close()
                return True
            else:
                cursor.execute(format_str2)
                if cursor.fetchone():
                    activity_logger.info("IP reused")
                    self.code = "12"
                    connection.close()
                    return True
                else:
                    cursor.execute(format_str3)
                    if cursor.fetchone():
                        activity_logger.info("MAC reused")
                        self.code = "13"
                        connection.close()
                        return True
                    else:
                        activity_logger.info("No match, user not registered")
                        self.code = "00"
                        connection.close()
                        return False
            

# FUNCTION:     auditDeregistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditDeregistration(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
        cursor = connection.cursor()

        format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND mac LIKE '{mac}' AND ip LIKE '{ip}' AND password LIKE '{password}';""".format(username=self.user,mac=self.mac,ip=self.ip,password=self.password)
        format_str1 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND (mac LIKE '{mac}' OR ip LIKE '{ip}');""".format(username=self.user,mac=self.mac,ip=self.ip)

        cursor.execute(format_str0)
        if cursor.fetchone():
            activity_logger.info("Entry Found, Removing")
            self.code = "20"
            connection.close()
            return True
        else:
            cursor.execute(format_str1)
            if cursor.fetchone():
                activity_logger.info("User registered to another ip or mac cannot remove")
                self.code = "30"
                connection.close()
                return False
            else:
                activity_logger.info("Mac or User not registered")
                self.code = "21"
                connection.close()
                return False


def auditQuery(user):
    connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/CPE401-IOT-CLIENT-SERVER/iot_server.db")
    cursor = connection.cursor()

    format_str0 = """SELECT * FROM registrar WHERE username LIKE '{username}' AND active==1""".format(username=user)

    cursor.execute(format_str0)
    if cursor.fetchone():
        activity_logger.info("Found Credentials for user")
        connection.close()
        return True
    else:
        connection.close()
        return False
    

def Listen(sock):
    while True:
        sock, addr = s.accept()
        #logging.info(("connection from %s" addr))
        data = sock.recv(1024)
        logging.info(data)
        fields = data.split('\t')
        if len(fields) > 1:
            if fields[0] == "REGISTER" or fields[0] == "DEREGISTER":
                p_type = fields[0]
                user = fields[1]
                password = fields[2]
                mac = fields[3]
                ip = fields[4]
                port = fields[5]

                new_ack = AckPacket(p_type,user,password,mac,ip,port,data)
                response = new_ack.generateAck()

            elif fields[0] == "LOGIN": 
                p_type = fields[0]
                user = fields[1]
                password = fields[2]
                ip = fields[3]
                port = fields[4]

                new_ack = AckPacket(p_type,user,password,ip,port,data)
                response = new_ack.generateAck()

            elif fields[0] == "LOGOFF":
                p_type = fields[0]
                user = fields[1]

                new_ack = AckPacket(p_type,user,data)
                response = new_ack.generateAck()

            elif fields[0] == "DATA":
                p_type = fields[0]
                d_code = fields[1]
                user = fields[2]
                time = fields[3]
                length = fields[4]
                message = fields[5]

            else:
                logging.error("Invalid packet received")


            if not data: break
            error_logger.info("RECV: "+data)
            error_logger.info("SEND: "+response)
            sock.send(response) # echo
        sock.close()


def sendQuery(user)
    current = datetime.datetime.now()
    currentDT = currentDT.strftime("%Y-%m-%d:%H:%M:%S")
    query = "QUERY 00 asmith "+currentDT

    (SERVER, PORT) = ('127.0.0.1', 1994)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((SERVER,PORT))
    s.send(query)
    data = s.recv(1024)
    print (data)
    s.close()


# FUNCTION:     Main
s = socket(AF_INET, SOCK_STREAM)
s.bind(('127.0.0.1', 1994))
s.listen(5) # max queued connections
t = Thread(target=Listen, args=(s,))
t.daemon=True
t.start()
while True:
    choice = raw_input("(1)\tSend Query\n(2)\tExit\nPlease Make a Selection: ")
    if choice == "1":
        user = raw_input("Enter the query you would like to query: ")
        if auditQuery(user) == True:
            print("Sending Query")
        else:
            print("User is not logged in or no user exists")
    else:
        sys.exit(0)
