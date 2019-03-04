# CPE401-IOT-CLIENT-SERVER
## Lab 2
#### Jared Knutson
My implementation of a client server protocol for interfacing generic IOT devices. Written in Python.

## Files:
- README.md
- server.py
- client.py
- iot_server.db
- Register
- Login

### server.py
Purpose: To provide a means of storing and retrieving data related to
the lab. This server listens for corretly formatted UDP packets from a client.
The server stores the clients data inside of a SQLite database which
is included with the files submitted. The table names are "registrar" and
"login".

### client.py
Purpose: To provide a client to interact with the server. The client provides
a menu for sending packets to the server. The user determines the port number
mac, ip, device-id, and password for the message to the server.

### iot_server.db
Purpose: This file is a SQLite database which is the container for the data
passed to the server from the client. Contains two tables, registrar and login.

### Register
Purpose: Test file for testing all register and deregister situations

### Login
Purpose: Test file for testing all login and logoff situations

### Major Issues
The idea of storing passwords in plaintext is a major issue, the client should
hash the password before it is sent to the server so that if there is anyone evedropping on the
connection the password cannot be read while in transit. Another method of securing this protocol
would be to encrypt the traffic on both ends so that the transmission is secured across an unsecure
channel. I was not able to find a case to use to test the QUERY/DATA packets as there was no specific
use case for them yet. 
