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


def main(argv):
   pfx_g=None
   proxy = xmlrpclib.ServerProxy("http://localhost:8000/")

    
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"ha:wp:cr:",["announce=","withdraw=","poison=","check=","research="])
   except getopt.GetoptError:
      print 'client.py -a <MUX>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'client.py -a <MUX>'
         sys.exit()
      elif opt in ("-a", "--announce"):
         info=arg.split(":")
         if len(info)<2:
 	     print "Invalid Arguments! Please refer user guide for usage information"
	 else:
             mux = info[0]
             username=info[1]
 
	     response=proxy.announce('announce '+str(mux)+' ' +username) 
	     res=response.split(",")
	 
             saveUid(res[0])
	     print res[1]
      elif opt in("-r","--research"):
	 info=arg.split(":")
         if len(info)<2:
             print "Invalid Arguments! Please refer user guide for usage information"
         else:
	     mux = info[0]
	     username=info[1]
             response=proxy.priority_announce('research '+str(mux)+' '+username)
             res=response.split(",")

             saveUid(res[0])
             print res[1]
      elif opt in ("-w", "--withdraw"):#MUX
         uid=getUid()
         #mux=arg
         #pfx=getPfx(str(uid))
	 pfx=proxy.check(uid)
         print pfx
	 if pfx is not None:
	     proxy.announce('withdraw '+str(pfx)+' WISC')
	 else:
             print "No announcements made from this client that can be withdrawn"
      elif opt in ("-c","--check"):
          uid1=getUid()
	  pfx_g=proxy.check(uid1)
          if pfx_g is None:
	      print "No prefix available for this Transaction ID"
          else:
              print "PFx used %d"%pfx_g

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
