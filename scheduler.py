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
from flask import Flask
from flask import request
import json
import sys, getopt
import time
import flask


config = {}
priority_level = None;

app = Flask(__name__)


app.secret_key = "bacon"


@app.route("/")
def login():
    return flask.render_template('beacon.html')

@app.route("/authenticate", methods=['POST'])
def authentication():
    data=request.stream.read()
    #jdata=json.dumps(data)
    pdata=json.loads(data)  
    print pdata
    try:
        username=pdata["username"]
        password=pdata["password"]
        print username
        print password
        ret=validate(username,password)
    except:
        print "Invalid JSON"
        return "false"
    return ret


#configuration username
@app.route("/beacon", methods=['POST'])
def parse_announce_request():
    global priority_level
    test="announce "
    data=request.stream.read()
    print data
    jdata=json.dumps(data)
    pdata=json.loads(data)

    try:
        ##Decoding the JSON recevied in the request 
        if len(pdata["configuration"]) != 0:   
            for row in range(len(pdata["configuration"])-1):
                if pdata["configuration"][row]["data"] != "":
                    test= test+pdata["configuration"][row]["mux"]+"."
                else:
                    test= test+pdata["configuration"][row]["mux"]
                
                asn=pdata["configuration"][row]["data"].split(",")
                for num in range(len(asn)-1):
                    test=test+ asn[num]+"/"
                test=test+ asn[-1]
                test=test+","
            if pdata["configuration"][-1]["data"] != "":
                test= test+pdata["configuration"][-1]["mux"]+"."
            else:
                test= test+pdata["configuration"][-1]["mux"]
            asn=pdata["configuration"][-1]["data"].split(",")
            for num in range(len(asn)-1):
                test=test+ asn[num]+"/"
            test=test+ asn[-1]
            test=test+" "+pdata["username"]
        else:
            print "No Configuration !!"
    except KeyError:
        print "Key Error"
    print test
    
    if "priority" in pdata:
        priority_level=pdata["priority"]
    else:
        priority_level=None
        print "Use defaulr priority_level"
    
    if priority_level is not None:
        print "priority --> "+priority_level

    print test
    response=announce(test)
  
    return response

@app.route("/beacon_check", methods=['POST'])
def parse_check_request():
    print "In check "
    data=request.stream.read()
    print data
    jdata=json.dumps(data)
    pdata=json.loads(data)
    username=""
    password=""
    tid=""
    try:
        username=pdata["username"]
        password=pdata["password"]
        tid=pdata["TID"]
    except KeyError:
        print "Key error"

    ret=validate(username,password)
    if ret == 'false':
        response="You are not Authorized to check the schedule"
    else:
        response=check_schedule(tid)
    return response


def getUniqueId():
    return uuid.uuid1()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sock.close()
    sys.exit(0)


class MyPriorityQueue(PriorityQueue):
    def __init__(self):
        PriorityQueue.__init__(self)
        self.counter = 0
    

    def put(self, req, priority):
        
        PriorityQueue.put(self, (priority, time.time(), req))
        self.counter += 1
        
        
    def get(self, *args, **kwargs):

        p, _, item = PriorityQueue.get(self, *args, **kwargs)
        return item
    def get1(self, *args, **kwargs):

        item = PriorityQueue.get(self, *args, **kwargs)
        return item

    def getElement(self, *args, **kwargs):
        item = PriorityQueue.get(self, *args, **kwargs)
        return item
    
		         
#gets the position of request the queue
#As it is a priority queue merely going theough the queue will be give us wrong index
#Hence we are removing the elements to see when our interested message is getting popped.This gives us index
#Priority queue is recreated after finding the index of the element.
#Make sure when queue is locked when using this function
def getIndexInPriorityQ(ques):
    print "In getIndexInPriorityQ"
    print ques
    ls= []
    while not reqQueue.empty():
        msg=reqQueue.get1()
        #print msg
        ls.append(msg)

    pos_tmp=0
    index=0
    for _,_,elem in ls:
        pos_tmp=pos_tmp+1    
        tid=elem.split(" ")
        if tid[2] == str(ques): 
            index=pos_tmp

    for p,_,elem in ls:
        reqQueue.put(elem,p)

    return index
    


    #for elem in orderlist:
        #print "elem -----> "+elem
#Msg format: string MUX username
#MUX is combination of MUX names
#for example WISC,ISI,GATECH
#it may include ASN -->WISC.73,ISI.73/74
#or it may include withdraw or unpoison messages -->WISC.unpoison
def validate_message(msg):
	print "In validate"
    	tup=msg.split(",")
	for i in range(len(tup)):
        	mux=tup[i].split(".")
            	if(len(mux)>2):
                	return "false"
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
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users where username= '"+username+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
            return 'true'
        else:
            return 'false'
             

def getUserGroup(username):
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT user_group FROM users where username= '"+username+"'")
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return row[0] 



def authenticate(username,group):
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users where username= '"+username+"' and user_group= '"+group+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
	    return 'true'
	else:
	    return 'false'

def validate(username,password):
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT user_group FROM users where username= '"+username+"' and password= '"+password+"'")
        rows = cur.fetchall()
        if len(rows)>=1:
            return rows[0]     
        else:
            return 'false'

def updateTransaction(username,tid):
	con = mdb.connect('localhost', db_user_name, db_password, db_name)
    	with con:
        	cur = con.cursor()
        	cur.execute("insert into transaction values('"+username+"','"+tid+"')")

    

#will be exposed to both normal users and researchers
#Writes the request to the priority queue
#Format: "announce [MUX,MUX..] username,password priority_level"
#MUX might include ASN for poison
#MUX1.AS1/AS2,MUX2.AS2,MUX3
def announce(msg):
    print "In announce msg:"
    global pos_user
    global priority_level
    str1=msg.split(" ")
    print len(str1)
    if len(str1)<3:
	response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    if validate_message(str1[1]) == "false":
        response="None,Invalid Arguments!Please refer user guide for usage information"
        return response
    threadLock.acquire()
    print msg
    #if str1[0] == "check":
    #print "calling check"
    uid=getUniqueId()
    print "after uid"
    if authenticate_user(str1[2])== 'true':
    	pfx_count=checkPfx()
	msg=str1[0]+" "+str1[1]+" "+str(uid)
	username=str1[2]
	updateTransaction(username,str(uid))
        print "update Transaction"
	print msg
        userGroup=getUserGroup(username)
        if userGroup == 'user':
            if priority_level is not None:
                if int(priority_level) > 5 and int(priority_level) <= 10:    
    	           reqQueue.put(msg,int(priority_level)) #2, priority for users
                else:
                    response="None,Unsupported priority level for the user group"
                    priority_level=None
                    threadLock.release() 
                    return response
            else: #use default priority if priority is not sent in the JSON
                reqQueue.put(msg,10) # Default priority level for user group

        if userGroup == 'research':
            if priority_level is not None:
                if int(priority_level) >=1 and int(priority_level) <10:    
                   reqQueue.put(msg,int(priority_level)) #1, priority for researchers
                else:
                    response="None,Unsupported priority level for the research group"
                    threadLock.release() 
                    priority_level=None
                    return response
            else: #use default priority if priority is not sent in the JSON
                reqQueue.put(msg,5) # Default priority level for research group
        if priority_level is not None:    
	   print "put queue level-->"+ priority_level 
    	#cycle=(p1/pfx_count)+(((p1%pfx_count)+p2)/pfx_count)
    	pos=getIndexInPriorityQ(uid)
        print "position got from check " 
        cycle=(pos-1)/pfx_count
        #cycle=1
    	print "Request will be scheduled and will annouced after " + str(cycle)
    	sch_time="Request is queued and is scheduled to be annouced with in " +str((cycle+1)*cycle_time)+" seconds"
    	response=str(uid)+","+sch_time+","+str1[1];
    else:
        response="You are not Authorized to make this request.Contact NSL for more information."
        response="None,"+response;

    threadLock.release() 
    priority_level=None
    return response



def checkPfx():
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx")
        rows = cur.fetchall()
        return (len(rows))

def checkFreePfx():
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where Availability=1")
        rows = cur.fetchall()
        return len(rows)

def check(msg):
    con = mdb.connect('localhost', db_user_name, db_password, db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where TransactionId ='"+msg+"'")
	row = cur.fetchone()
        if row is None:
            return None
        else:
            return row[0] 


def check_schedule(transid):
    
    index=0
    threadLock.acquire()
    index=getIndexInPriorityQ(transid)
    threadLock.release()
    #index=reqQueue.checkqueue(transid)
    pfx_count=checkPfx()
    print "index is "+str(index)
    if index <= pfx_count:
	if index ==0:
        	ret=check(transid)
        	if ret is not None:
            		return "Currently announced and will be withdrawn within"+str(cycle_time)+" seconds and pfx used is 184.164."+str(ret)+".0"
        	else:
            		return "Request is not scheduled to be announced"

	return "Request is queued and is scheduled to be annouced with in "+str(cycle_time) +"seconds"
    else:
	if index%pfx_count == 0:
	   index=(index/pfx_count)-1
	else:
	   index=index/pfx_count
        return "Request is queued and is scheduled to be annouced with in " +str((index+1)*cycle_time)+" seconds"
		
   

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
        time.sleep(cycle_time)
        threadLock.acquire()
	withdraw() #indicates the beginning of next cycle
        time.sleep(5) #Addition harcoded time to make sure Database operations are completed
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


    

#Starts Python Flask server which will listen to POST requests
def process():
    app.run()# Add host='0.0.0.0' to make it listen on all public IP



#This is where announcer is listening for scheduler. 
#Assumption : Announcer and Scheduler will be running the same machine.
#Announcer IP address is hardcoded for this reason
serverAddress = ('localhost',8999)

#reads the config file

execfile("config.ini", config) 
try:
    MUXES=config["MUX"]
    db_name=config["db_name"]
    db_password=config["db_password"]
    db_user_name=config["db_user_name"]
    cycle_time=config["cycle_time"]
except:
    print "Config values not given."
    sys.exit(0)
    
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serverAddress)
threadLock = threading.Lock()
reqQueue = MyPriorityQueue()
prevQueue = Queue.Queue()
#reqQueue = Queue.Queue(100)
threadList = [ "Thread1","Thread2" ]
threads = []
threadID = 1

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName )
    thread.start()
    threads.append(thread)
    threadID += 1

# Wait for all threads to complete
for t in threads:
    t.join()

