import xmlrpclib
import os
import socket,time
from SimpleXMLRPCServer import SimpleXMLRPCServer
import signal
import sys
import uuid
import MySQLdb as mdb
import Queue
import threading
import time
def getUniqueId():
    return uuid.uuid1()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sock.close()
    sys.exit(0)

def announce(msg):
    str1=msg.split(" ")
    print msg
   # print str1[0]
   #if str1[0] == "check":
   #    print "calling check"
    uid=getUniqueId()
    pfx_count=checkFreePfx()
    msg=msg+" "+str(uid)
    if pfx_count>=1:
        sock.send(msg)
    else:
        print "No Pfx avaialble.Request will be queued"
        reqQueue.put(msg)
    return str(uid)

def checkFreePfx():
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where Availability =1")
        rows = cur.fetchall()
        return len(rows)

def check(msg):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where TransactionId ='"+msg+"'")
	row = cur.fetchone()
        if row is None:
            return None
        else:
            return row[0]       
#    os.system("python ctrlpfx.py --prefix 236 --mux wisc --poison 72")

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        if self.name == "Thread1":
            process()
        else:
	    checkDB()
        print "Exiting " + self.name

def checkDB():
    while 1:
        print "In check DB"
    	time.sleep(30)
    	threadLock.acquire()
    	pfxCount=checkFreePfx() 
    	if pfxCount >= 1:
            if not reqQueue.empty():
                data = reqQueue.get()
	        announce(data)
	    else:
                print "No Requests is queued this time"   
        else:
            print "No pfx still available" 
        threadLock.release()
    


def process():
    print "Listening on port 8999..."
    server.serve_forever()

server = SimpleXMLRPCServer(("localhost", 8000),allow_none=True)
serverAddress = ('localhost',8999)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serverAddress)
server.register_function(announce, "announce")
server.register_function(check, "check")

threadLock = threading.Lock()
reqQueue = Queue.Queue(100)
threadList = ["Thread1", "Thread2" ]
threads = []
threadID = 1
signal.signal(signal.SIGINT, signal_handler)
# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName )
    thread.start()
    threads.append(thread)
    threadID += 1

# Wait for all threads to complete
for t in threads:
    t.join()
