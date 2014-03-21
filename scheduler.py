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
from Queue import PriorityQueue
p1=0
p2=0
p3=0
pos_user=0
pos_research=0
research_map= {}
user_map= {}
def getUniqueId():
    return uuid.uuid1()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sock.close()
    sys.exit(0)


class MyPriorityQueue(PriorityQueue):
    def __init__(self):
        global p1
    	global p2
    	global p3
        PriorityQueue.__init__(self)
        self.counter = 0
        p1=0
	p2=0
	p3=0

    def put(self, req, priority):
        global p1
    	global p2
    	global p3
        PriorityQueue.put(self, (priority, self.counter, req))
        self.counter += 1
        if priority == 1:
	    p1=p1+1
	elif priority == 2:
	    p2=p2+1
	elif priority == 3:
	    p3=p3+1
        
    def get(self, *args, **kwargs):
	global p1
        global p2
        global p3

        p, _, item = PriorityQueue.get(self, *args, **kwargs)
	if p == 1:
	    p1=p1-1
	elif p == 2:
	    p2=p2-1
	elif p == 3:
	    p3=p3-1
        return item

#will be exposed to both normal users and researchers
#Writes the request to the priority queue
def announce(msg):
    global p1
    global p2
    global p3
    global pos_user

    threadLock.acquire()
    str1=msg
    print msg
    #if str1[0] == "check":
    #print "calling check"
    uid=getUniqueId()
    pfx_count=checkPfx()
    msg=msg+" "+str(uid)
    reqQueue.put(msg,2) #priority for users
    #cycle=(p1/pfx_count)+(((p1%pfx_count)+p2)/pfx_count)
    if (p1+p2)%pfx_count == 0 and p2 !=0:
        cycle=(p1+p2/pfx_count)-1
    else:
	cycle=(p1+p2/pfx_count)
    pos_user=pos_user+1    
    user_map[uid]=pos_user
    print "p1 == "+str(p1)
    print "p2 == "+str(p2)
    print "pfx_count = "+ str(pfx_count)
    
    print "Request will be scheduled and will annouced after " + str(cycle)
    sch_time="Request will be scheduled and will annouced after " +str(cycle)
    response=str(uid)+","+sch_time;
    threadLock.release() 
    return response

#will be exposed only to researchers
#Writes the request to the priority queue
def priority_announce(msg):
    global p1
    global p2
    global p3
    global pos_research

    threadLock.acquire()
    str1=msg.split(" ")
    print msg
    print str1[0]
    #if str1[0] == "check":
    #print "calling check"
    uid=getUniqueId()
    pos_research=pos_research+1
    research_map[uid]=pos_research
    pfx_count=checkPfx()
    msg=msg+" "+str(uid)
    reqQueue.put(msg,1) #priority for researchers
    cycle=p1/pfx_count
    print "Request will be scheduled and will annouced after " + str(cycle)
    sch_time="Request will be scheduled and will annouced after "+str(cycle)
    response=str(uid)+","+sch_time;
    threadLock.release() 
    return response


def checkPfx():
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx")
        rows = cur.fetchall()
        return (len(rows))

def checkFreePfx():
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where Availability=1")
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
	    readQueue()
        print "Exiting " + self.name

#Withdraws Annoucements made in previous cycle
def withdraw():
    while not prevQueue.empty():
        msgl=prevQueue.get()
        str1=msgl.split(" ")
        pfx=check(str1[2])
	msg="withdraw"+" "+str(pfx)+" "+str1[1]
	print msg
	sock.send(msg)
         
#reads the request from the queue and makes announcement
def readQueue():
    while 1:
        print "In readQueue"
        time.sleep(30)
        threadLock.acquire()
	withdraw() #indicates the beginning of next cycle
        time.sleep(5) 
        pfxCount=checkFreePfx()
        if pfxCount >= 1:
            if not reqQueue.empty():
                while (pfxCount>=1):
                    data = reqQueue.get()
		    sock.send(data)
		    print data
		    print pfxCount
                    pfxCount=pfxCount-1
		    prevQueue.put(data)
            else:
                print "No Requests is queued this time"
        else:
            print "No pfx still available"
	threadLock.release()


def checkDB():
    while 1:
        print "In check DB"
    	time.sleep(30)
    	threadLock.acquire()
    	pfxCount=checkPfx() 
    	if pfxCount >= 1:
            if not reqQueue.empty():
		while pfxCount>=1 and not reqQueue.empty(): 
                    data = reqQueue.get()
	            announce(data)
		    pfxCount=checkFreePfx()
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
reqQueue = MyPriorityQueue()
prevQueue = Queue.Queue()
#reqQueue = Queue.Queue(100)
threadList = ["Thread1", "Thread2" ]
threads = []
threadID = 1
#signal.signal(signal.SIGINT, signal_handler)
# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName )
    thread.start()
    threads.append(thread)
    threadID += 1

# Wait for all threads to complete
for t in threads:
    t.join()
