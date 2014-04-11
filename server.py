import socket
import signal
import sys
import os
import ctrlpfx_new
import MySQLdb as mdb
from multiprocessing import Process
import smtplib

from email.mime.text import MIMEText

MUXES=('GATECH','WISC','CLEMSON','PRINCE','UW','AMSIX','ISI')

PREFIXES = range(236, 239)


def updateDB_announce(pfx,trans_id):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("UPDATE pfx SET TransactionId='"+str(trans_id)+"' where PFX = "+str(pfx))
	#print "UPDATE pfx SET TransactionId='"+str(trans_id)+"' where PFX = "+str(pfx)
    

def updateDB_withdraw(pfx):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("UPDATE pfx SET TransactionId=NULL,Availability=1 where PFX = "+str(pfx))

#MUX might include AS numbers to poison
#it will be identified by "."
#multiple AS numbers will be separated by "/"
#if it includes AS number call the poison function in ctrlpfx
#format mux= WISC.73/74
#if 0 is given in ASN then withdraw is sent from that MUX
def Announce(pfx,mux):
    	print "Prefix Used for annoucement "+str(pfx)
	#p = Process(target=ctrlpfx_new.announce, args=(int(pfx), mux))
    	#p.start()
	str1=mux.split(".")
	if len(str1)==2:
        	asn=str1[1].split("/")
		mux=str1[0];
		poison="";
        	for i in range(len(asn)):
                	poison=poison+asn[i]+" "
		if len(asn) == 1:
			if poison.strip() == "withdraw":
				ctrlpfx_new.withdraw(int(pfx),mux) #pfx,MUX
			elif poison.strip() == "unpoison":
                                ctrlpfx_new.unpoison(int(pfx),mux)
			else:
			        poison=poison+"47065"
	                        print "poisoning " +poison
       	                        ctrlpfx_new.poison(int(pfx),mux,poison)

		else:
			poison=poison+"47065"
			print "poisoning " +poison
			ctrlpfx_new.poison(int(pfx),mux,poison)
	else:
		ctrlpfx_new.announce(int(pfx),mux)
        	print "Announing "+mux

        #getUniqueId();

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    clientSocket.close()
    sys.exit(0)

def getEmail(tid):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("select username from transaction where TrasactionId='"+tid+"'")
	username=cur.fetchone()
	cur.execute("select email from users where username='"+username[0]+"'")
	email=cur.fetchone()
	print email[0]
	return email[0]
	

def sendEmail(email,pfx,info):
    msg = MIMEText("Beacon: Prefix used 184.164."+str(pfx)+".0 for announcing "+info+"\nThis annoucement will expire in 1.5 hours after which it might get overwritten")

# me == the sender's email address
# you == the recipient's email address
    msg['Subject'] = 'Hi From Beacon Client'
    msg['From'] = 'jeyarama@usc.edu'
    msg['To'] = 'jeyarama@usc.edu'

# Send the message via our own SMTP server, but don't include the
# envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail('jeyarama@usc.edu', email, msg.as_string())
    s.quit()


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
        if msg[0] == 'announce' or msg[0] == 'research':
            pfx=getfree_pfx()
	    mux=msg[1]
	    trans_id=msg[2]
	    if pfx is not None:
		if((pfx in PREFIXES)):
		    if trans_id=='Default':
		        print "Announcing Default Beacon Request"
		    else:
		        if msg[0] =='announce':	
			    print "Announcing User Request"
			else:
			    print "Announing Research Request"
		    muxes=mux.split(",")
		    for i in range(len(muxes)):
		    	Announce(pfx,muxes[i])
			print muxes[i]
			
		    updateDB_announce(pfx,trans_id)
		    if trans_id != "Default":
		    	email=getEmail(trans_id)
		    	sendEmail(email,pfx,msg[1])
		    
	    else:
		print "No prefixes avaialble for advertisement"
    		print "Request is queued"
		#Add to queue <Operation,MUX,PFX,Trans_ID>
	
        if msg[0] == 'withdraw':
            print 'withdrawing'
	    muxes=msg[2].split(",")
            #for i in range(len(muxes)):
		#if muxes[i] is not None and msg[1] is not None:
			#p = Process(target=ctrlpfx_new.withdraw, args=(int(msg[1]),muxes[i]))
        		#p.start()

			#ctrlpfx_new.withdraw(int(msg[1]),muxes[i]) #pfx,MUX
	    updateDB_withdraw(int(msg[1]))
        if msg[0] == 'poison':
	    print 'Poisoning'
	    ctrlpfx_new.poison(int(msg[1]),msg[2]) 
            #updateDB(int(msg[1]))
    clientSocket.close()
