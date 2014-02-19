import socket
import signal
import sys
import os
import ctrlpfx_new
import MySQLdb as mdb
MUXES=('GATECH','WISC','CLEMSON','PRINCE','UW','AMSIX','ISI')

PREFIXES = range(236, 238)


def updateDB(pfx,trans_id):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("UPDATE pfx SET TransactionId='"+str(trans_id)+"' where PFX = "+str(pfx))
    

def Announce(pfx,mux):
    print "Using pfx .."+str(pfx)
    if mux == "all":
        for muxl in MUXES:
	    ctrlpfx_new.announce(int(pfx),muxl) 
	#return getUniqueId();    
    else:
        ctrlpfx_new.announce(int(pfx),mux) 
        #getUniqueId();

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    clientSocket.close()
    sys.exit(0)


#Get Avaialble prefixes from Database and returns first avaialble prefix
def getfree_pfx():
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con: 
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where Availability=1")
        rows = cur.fetchall()
        for row in rows:
            #print "returning "+row
	    cur.execute("UPDATE pfx SET Availability=0 where pfx="+str(row[0]))
	    return row[0];


#pfx=getfree_pfx();
#print "pffffx"+str(pfx);
#if pfx is not None:
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
            pfx=getfree_pfx()
	    mux=msg[1]
	    trans_id=msg[2]
	    if pfx is not None:
		if((pfx in PREFIXES)and((mux in MUXES)or(mux =='all'))):
		    Announce(pfx,mux)
		    updateDB(pfx,trans_id)
	    else:
		print "No prefixes avaialble for advertisement"
    		print "Request is queued"
		#Add to queue <Operation,MUX,PFX,Trans_ID>
	
        if msg[0] == 'withdraw':
            print 'withdrawing'
	    ctrlpfx_new.withdraw(int(msg[1]),msg[2]) 
        if msg[0] == 'poison':
	    print 'Poisoning'
	    ctrlpfx_new.poison(int(msg[1]),msg[2])   
    clientSocket.close()
