import xmlrpclib
import MySQLdb as mdb
import sys, getopt

def saveUid(trans_id):
    fo = open("transid.txt", "w+")
    fo.write(trans_id);
    fo.close()

def getUid():
    fo = open("transid.txt", "r")
    uid=fo.read();
    fo.close()
    return uid


def getPfx(uid):
    con = mdb.connect('localhost', 'testuser', 'test623', 'DR');
    with con:
        cur = con.cursor()
        cur.execute("SELECT pfx FROM pfx where TransactionId='"+str(uid)+"'")
        row = cur.fetchone()
        return row[0]


def main(argv):
   proxy = xmlrpclib.ServerProxy("http://localhost:8000/")
   print "Try announcing from client"

    
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"ha:w:p:",["announce=","withdraw=","poison="])
   except getopt.GetoptError:
      print 'client.py -a <MUX>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'client.py -a <MUX>'
         sys.exit()
      elif opt in ("-a", "--announce"):
         mux = arg
	 uid=proxy.announce('announce '+str(mux)) 
         saveUid(uid)
      elif opt in ("-w", "--withdraw"):#MUX
         uid=getUid()
         mux=arg
         pfx=getPfx(str(uid))
         print pfx
	 proxy.announce('withdraw '+str(pfx)+' WISC')

if __name__ == "__main__":
   main(sys.argv[1:])


#Allows no return value in RPC call
#proxy = xmlrpclib.ServerProxy("http://localhost:8000/",allow_none=True)

#proxy = xmlrpclib.ServerProxy("http://localhost:8000/")
#print "Try announcing from client" 
#Announces prefix
#proxy.announce('announce 237 WISC')

#uid=proxy.announce('announce WISC')





#Withdraws prefix
#proxy.announce('withdraw 237 WISC')

#Poison prefix
#proxy.announce('poison 237 WISC 74')
