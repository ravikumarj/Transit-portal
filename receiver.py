import xmlrpclib
import os
import socket,time
from SimpleXMLRPCServer import SimpleXMLRPCServer
import signal
import sys

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sock.close()
    sys.exit(0)

def announce(msg):
    sock.send(msg)

#    os.system("python ctrlpfx.py --prefix 236 --mux wisc --poison 72")

server = SimpleXMLRPCServer(("localhost", 8000),allow_none=True)
print "Listening on port 8999..."
serverAddress = ('localhost',8999)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serverAddress)
signal.signal(signal.SIGINT, signal_handler)
server.register_function(announce, "announce")
server.serve_forever()
