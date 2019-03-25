# CPE401-IOT-CLIENT-SERVER
## Current Assignment: Lab 2
##### Jared Knutson
Github: https://github.com/DredNaut/CPE401-IOT-CLIENT-SERVER
My implementation of a client server protocol for interfacing generic IOT devices. Written in Python.

### Dependancies
- a folder named "log" in your working directory, this will be where server logs are
directed to.
- Version: Python 2.7

## Logs:
- use tail -F command to monitor log file
```
tail -F ./log/Activity.log
```

## Files:
- README.md
- server.py
- client.py
- iot_server.db
- Register
- Login

#### server.py
Purpose: To provide a means of storing and retrieving data related to
the lab. This server listens for corretly formatted UDP packets from a client.
The server stores the clients data inside of a SQLite database which
is included with the files submitted. The table names are "registrar" and
"login".

#### client.py
Purpose: To provide a client to interact with the server. The client provides
a menu for sending packets to the server. The user determines the port number
mac, ip, device-id, and password for the message to the server.

#### iot_server.db
Purpose: This file is a SQLite database which is the container for the data
passed to the server from the client. Contains two tables, registrar and login.

#### Register
Purpose: Test file for testing all register and deregister situations

#### Login
Purpose: Test file for testing all login and logoff situations

#### Major Issues
The idea of storing passwords in plaintext is a major issue, the client should
hash the password before it is sent to the server so that if there is anyone evedropping on the
connection the password cannot be read while in transit. Another method of securing this protocol
would be to encrypt the traffic on both ends so that the transmission is secured across an unsecure
channel. I was not able to find a case to use to test the QUERY/DATA packets as there was no specific
use case for them yet. 

## Useage:
#### Running the Client
Run the following command and then follow the prompt to create the desired packet.

```bash 
>$ python client.py <device-id> <server-ip> <server-port> <device-port>
(1) Register
(2) De-Register
(3) Login
(4) Logoff
(5) Query Server
(6) Query Client
(7) Exit
Please Make a Selection: 1
```

After this you will be asked for the following information:
- MAC
- IP
- PORT
- USER/DeviceID
- Password

The client will then send the packet off to the server which should be listening,
 if the server is configured correctly the client should receive a ACK packet.


#### Running the Server
The server does not have an interface, it will run without showing any options.
Any actions will be logged to a log file located at ./log/Activity.log and
any error will be reported to ./log/error.log

The server can be started by issuing the following command in the terminal
```bash
>$ python server.py <listening-port>
```
