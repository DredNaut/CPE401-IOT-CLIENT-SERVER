# NAME:             server.py
# AUTHOR:           Jared Knutson
# DATE:             25FEB2019
# DESCRIPTION:      Connection Oriented Server


from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sqlite3
import hashlib
import logging

# Logging settings
FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
logging.basicConfig(filename="./log/test.log",level=logging.NOTSET,format=FORMAT)
logger = logging.getLogger(__name__)

d = '\t'


# CLASS:        AckPacket
# DESCRIPTION:  Class which handles the client requests.
class AckPacket:

# FUNCTION:     __init__
# DESCRIPTION:  Parameterized Constructor
    def __init__ (self, user, password, mac, ip, port, raw):
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

        if p_type == "REGISTER":
            response = self.parseRegistration()

        elif p_type == "DEREGISTER": 
            response = self.parseDeregistration()

        elif p_type == "LOGIN": 
            response = self.parseLogin()

        elif p_type == "LOGOFF": 
            response = self.parseLogoff()

        elif p_type == "DATA": 
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


# FUNCTION:     parseLogoff
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseLogoff(self):
        loggin.info("Logoff Packet Received")


# FUNCTION:     parseData
# DESCRIPTION:  Check if the device is already in the registrar file
    def parseData(self):
        logging.info("Data Packet Received")


# FUNCTION:     setRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def setRegistration(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/test_programs/iot_server.db")
        cursor = connection.cursor()

        new_entry = (self.user, self.mac, self.ip, self.password)
        format_str = """INSERT INTO registrar (username, mac, ip, password)
        VALUES (?,?,?,?);"""

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
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/test_programs/iot_server.db")
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


# FUNCTION:     auditRegistration
# DESCRIPTION:  Check if the device is already in the registrar file
    def auditRegistration(self):
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/test_programs/iot_server.db")
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
                cursor.execute(format_str2)
                if cursor.fetchone():
                    logging.info("IP reused")
                    self.code = "12"
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
        connection = sqlite3.connect("/Users/drednaut/Courses/Latex_Course_Files/CPE401/test_programs/iot_server.db")
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


# FUNCTION:     Main
s = socket(AF_INET, SOCK_STREAM)
s.bind(('127.0.0.1', 1994))
s.listen(5) # max queued connections

while True:
    sock, addr = s.accept()
    #logging.info(("connection from %s" addr))
    data = sock.recv(1024)
    fields = data.split('\t')
    if len(fields) > 1:
        p_type = fields[0]
        user = fields[1]
        password = fields[2]
        mac = fields[3]
        ip = fields[4]
        port = fields[5]

        new_ack = AckPacket(user,password,mac,ip,port,data)
        response = new_ack.generateAck()


        if not data: break
        logging.debug("RECV: "+data)
        logging.debug("SEND: "+response)
        sock.send(response) # echo
    sock.close()
