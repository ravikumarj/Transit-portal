import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000/",allow_none=True)
print "Try announcing from client" 
#Announces prefix
#proxy.announce('announce 237 WISC')

#Withdraws prefix
#proxy.announce('withdraw 237 WISC')

#Poison prefix
proxy.announce('poison 237 WISC 74')
