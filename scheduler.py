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


MUXES=['GATECH','WISC','CLEMSON','PRINCE','UW','AMSIX','ISI']
#Three different classes of priority. These variables keep track number of requests 
#in each priority class.
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
    
    def checkqueue(self,transid):
         print("Priority")
         print("=" * 42)
         for elem in self.queue:
             print(elem)
         print("current queue status")
	 index=0
         for _,_,req in self.queue:
	     tmp=req.split(" ")
	     tid=tmp[2]
	     if tid == transid:
		index=index+1
		return index 
             else:
                 index=index+1
	 return 0
		         

#Msg format: string MUX username
#MUX is combination of MUX names
#for example WISC,ISI,GATECH
#it may include ASN -->WISC.73,ISI.73/74
#or it may include withdraw or unpoison messages -->WISC.unpoison
def validate_message(msg):
    	tup=msg.split(",")
	for i in range(len(tup)):
        	mux=tup[i].split(".")
        	if mux[0]  not in MUXES:
                	return "false"
        	else:
                	if(len(mux) ==2):
                        	asn=mux[1].split("/")
                        	if len(asn) ==1:
                                	try:
                                        	int(asn[0])
                                	except ValueError:
                                        	if asn[0] != "unpoison" and asn[0] != "withdraw":
                                                	return "false"

                        	else:
                                	for j in range(len(asn)):
                                        	try:
                                                	int(asn[j])
                                        	except ValueError:
                                                	return "false"


	return "true"
	
    
	
def authenticate_user(username):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users where username= '"+username+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
            return 'true'
        else:
            return 'false'
             


def authenticate(username,group):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users where username= '"+username+"' and user_group= '"+group+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
	    return 'true'
	else:
	    return 'false'

def validate(username,password):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users where username= '"+username+"' and password= '"+password+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
            return 'true'
        else:
            return 'false'

def updateTransaction(username,tid):
	con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    	with con:
        	cur = con.cursor()
        	cur.execute("insert into transaction values('"+username+"','"+tid+"')")

    

#will be exposed to both normal users and researchers
#Writes the request to the priority queue
#Format: "announce [MUX,MUX..] username"
#MUX might include ASN for poison
#MUX1.AS1/AS2,MUX2.AS2,MUX3
def announce(msg):
    global p1
    global p2
    global p3
    global pos_user
    str1=msg.split(" ")
    print len(str1)
    if len(str1)<3:
	response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    if validate_message(str1[1]) == "false":
        response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    threadLock.acquire()
    #print msg
    #if str1[0] == "check":
    #print "calling check"
    uid=getUniqueId()
    if authenticate_user(str1[2])== 'true':
    	pfx_count=checkPfx()
	msg=str1[0]+" "+str1[1]+" "+str(uid)
	username=str1[2]
	updateTransaction(username,str(uid))
	print msg
    	reqQueue.put(msg,2) #priority for users
    	#cycle=(p1/pfx_count)+(((p1%pfx_count)+p2)/pfx_count)
    	if (p1+p2)%pfx_count == 0 and p2 !=0:
        	cycle=((p1+p2)/pfx_count)-1
    	else:
		cycle=((p1+p2)/pfx_count)
    	pos_user=pos_user+1    
    	user_map[uid]=pos_user
    	#print "p1 == "+str(p1)
    	#print "p2 == "+str(p2)
    	#print "pfx_count = "+ str(pfx_count)
    
    	#print "Request will be scheduled and will annouced after " + str(cycle)
    	sch_time="Request is queued and is scheduled to be annouced with in " +str((cycle+1)*1.5)+" hours"
    	response=str(uid)+","+sch_time;
    else:
        response="You are not Authorized to make this request.Contact NSL for more information."
        response="None,"+response;

    threadLock.release() 
    return response

#will be exposed only to researchers
#Writes the request to the priority queue
def priority_announce(msg):
    global p1
    global p2
    global p3
    global pos_research

    str1=msg.split(" ")
    #print len(str1)
    if len(str1)<3:
        response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    if validate_message(str1[1]) == "false":
	response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    threadLock.acquire()
    #print msg
    #print str1[0]
    #if str1[0] == "check":
    #print "calling check"
    print len(str1)
    uid=getUniqueId()
    if authenticate(str1[2],'research')== 'true':
    	pos_research=pos_research+1
    	research_map[uid]=pos_research
    	pfx_count=checkPfx()
    	msg=str1[0]+" "+str1[1]+" "+str(uid)
    	reqQueue.put(msg,1) #priority for researchers
    	if (p1)%pfx_count == 0:
        	cycle=(p1/pfx_count)-1
    	else:
        	cycle=(p1/pfx_count)
    #print "Request will be scheduled and will annouced after " + str(cycle)
    	sch_time="Request is queued and is scheduled to be annouced with in " +str((cycle+1)*1.5)+" hours"
    	response=str(uid)+","+sch_time;
    else:
	response="You are not Authorized to make this request.Contact NSL for more information." 
        response="None,"+response;
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


def check_schedule(transid):
    index=reqQueue.checkqueue(transid);
    pfx_count=checkPfx()
    print "index is "+str(index)
    if index <= pfx_count:
	if index ==0:
        	ret=check(transid)
        	if ret is not None:
            		return "Currently announced and will be withdrawn within 1.5 hours and pfx used is 184.164."+str(ret)+".0"
        	else:
            		return "Request is not scheduled to be announced"

	return "Request is queued and is scheduled to be annouced with in 1.5 hours " 
    else:
	if index%pfx_count == 0:
	   index=(index/pfx_count)-1
	else:
	   index=index/pfx_count
        return "Request is queued and is scheduled to be annouced with in " +str((index+1)*1.5)+" hours"
		
   

#    os.system("python ctrlpfx.py --prefix 236 --mux wisc --poison 72")

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        #print "Starting " + self.name
        if self.name == "Thread1":
            process()
        else:
	    readQueue()
        #print "Exiting " + self.name

#Wont explicitly withdraw an announcement
#Will update the Database to free the prefix
#It will be used in next cycle
def withdraw():
    #print "in withdraw"
    while not prevQueue.empty():
        msgl=prevQueue.get()
        str1=msgl.split(" ")
        pfx=check(str1[2])
	msg="withdraw"+" "+str(pfx)+" "+str1[1]
	print msg
	sock.send(msg)
         
#Sends Beacon Request-- Request is hardcoded
#To do-- Figure out better way to generate default request
def sendBeaconReq():
    req="announce WISC Default"
    print "Sending Default Beacon Request"
    sock.send(req)
    prevQueue.put(req) 
    


#reads the request from the queue and makes announcement
def readQueue():
    while 1:
        #print "In readQueue"
        time.sleep(60)
        threadLock.acquire()
	withdraw() #indicates the beginning of next cycle
        time.sleep(5) 
        pfxCount=checkFreePfx()
        if pfxCount >= 1:
            if not reqQueue.empty():
                while not reqQueue.empty() and pfxCount>=1:
                    data = reqQueue.get()
		    sock.send(data)
		    print data
		    #print pfxCount
                    pfxCount=pfxCount-1
		    prevQueue.put(data)
		else:
		    if pfxCount>=1:
		        sendBeaconReq()
            else:
		#send beacon request if prefixes are still avaialble
		sendBeaconReq()
                #print "No Requests is queued this time"
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
server.register_function(check_schedule, "check_schedule")
server.register_function(priority_announce,"priority_announce")
server.register_function(validate,"validate")
threadLock = threading.Lock()
reqQueue = MyPriorityQueue()
prevQueue = Queue.Queue()
#reqQueue = Queue.Queue(100)
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
