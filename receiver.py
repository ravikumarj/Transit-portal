import xmlrpclib
import os
import socket,time
from SimpleXMLRPCServer import SimpleXMLRPCServer
import signal
import sys
import uuid
def getUniqueId():
    return uuid.uuid1()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sock.close()
    sys.exit(0)

def announce(msg):
    uid=getUniqueId()
    msg=msg+" "+str(uid)
    #print msg
    sock.send(msg)
    return str(uid)

#    os.system("python ctrlpfx.py --prefix 236 --mux wisc --poison 72")

server = SimpleXMLRPCServer(("localhost", 8000),allow_none=True)
print "Listening on port 8999..."
serverAddress = ('localhost',8999)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serverAddress)
signal.signal(signal.SIGINT, signal_handler)
server.register_function(announce, "announce")
server.serve_forever()
