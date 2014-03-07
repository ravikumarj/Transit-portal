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
   print "Try announcing from client"

    
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"ha:wp:c",["announce=","withdraw=","poison=","check="])
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
         #mux=arg
         #pfx=getPfx(str(uid))
	 pfx=proxy.check(uid)
         print pfx
	 if pfx is not None:
	     proxy.announce('withdraw '+str(pfx)+' WISC')
	 else:
             print "No announcement made to withdraw"
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
