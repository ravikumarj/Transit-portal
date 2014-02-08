import socket
import signal
import sys
import os
import ctrlpfx_new
def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    clientSocket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind(('localhost', 8999))

serversocket.listen(5)
print "Ready to Accept"
while True:
    # process connections from clients
    (clientSocket, address) = serversocket.accept()
  
    while True:
        req = clientSocket.recv(100)
        if not req: break # client closed connection
	msg = req.split()
	if msg[0] == 'announce':
	    print 'Announcing'
	    ctrlpfx_new.announce(int(msg[1]),msg[2])
        if msg[0] == 'withdraw':
	    print 'withdrawing'
	    ctrlpfx_new.withdraw(int(msg[1]),msg[2]) 
        if msg[0] == 'poison':
	    print 'Poisoning'
	    ctrlpfx_new.poison(int(msg[1]),msg[2],msg[3])   
	#os.system("python ctrlpfx.py --prefix 236 --mux wisc --poison 73")
    clientSocket.close()

