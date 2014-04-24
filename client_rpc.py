#!/usr/bin/env python
import json
import os, sys
from optparse import OptionParser
from optparse import Option, OptionValueError
import urllib
import urllib2


conflist = []
jsondata ={}

VERSION = '0.1'

class MultipleOption(Option):
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":

            values.ensure_value(dest, []).append(value)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)


def main():
    PROG = os.path.basename(os.path.splitext(__file__)[0])
    long_commands = ('categories')
    short_commands = {'cat':'categories'}
    description = """Just a test"""
    parser = OptionParser(option_class=MultipleOption,
                          usage='usage: %prog [OPTIONS] COMMAND [BLOG_FILE]',
                          version='%s %s' % (PROG, VERSION),
                          description=description)
    parser.add_option('-m', '--mux', 
                      action="extend", type="string",
                      dest='name', 
                      metavar='CONFIGURATION', 
                      help='MUX Configuration eg - WISC')
    parser.add_option('-u', '--user', 
                      action="extend", type="string",
                      dest='username', 
                      metavar='string', 
                      help='Username')
    parser.add_option('-p', '--password', 
                      action="extend", type="string",
                      dest='password', 
                      metavar='string', 
                      help='password')
    parser.add_option('-t', 
                      type="string",
                      dest='tid', 
                      metavar='CONFIGURATION', 
                      help='Transaction Id')
    parser.add_option('-l', 
                      type="string",
                      dest='priority', 
                      metavar='CONFIGURATION', 
                      help='Custom Priority Level')


    parser.add_option('-a','--announce', help='Announce option', dest='announce', 
                      default=False, action='store_true')

    parser.add_option('-c','--check', help='Check option', dest='check', 
                      default=False, action='store_true')



    if len(sys.argv) == 1:
        parser.parse_args(['--help'])



    OPTIONS, args = parser.parse_args()
    


    if OPTIONS.name is not None:
      for conf in OPTIONS.name:
        print conf
        d= {}
        mux=conf.split(".")
        d["mux"]=mux[0]
        if len(mux)==2:
          d["data"]=mux[1]
        else:
          d["data"]=""
        conflist.append(d)
    jsondata["configuration"]=conflist
    

    if OPTIONS.username is not None:
      jsondata["username"]=OPTIONS.username[0]
    else:
      print "Username is needed"
      exit(-1)

    if OPTIONS.password is not None:
      jsondata["password"]=OPTIONS.password[0]
    else:
      print "Password is needed"
      exit(-1)


    if OPTIONS.check == True:
        print "Check"
        if OPTIONS.tid is not None:
          jsondata["TID"]=OPTIONS.tid   
         
          data= json.dumps(jsondata)
          #print data
          url = "http://localhost:5000/beacon_check"

          request_object = urllib2.Request(url, data)

          #make the request using the request object as an argument, store response in a variable
          response = urllib2.urlopen(request_object)

          #store request response in a string
          html_string = response.read()
          print html_string   
        else:
          print "Invalid Arguments Transaction Id needed for checking"

    if OPTIONS.announce == True:
        print "Announce"
        if OPTIONS.priority is not None:
          jsondata["priority"]=OPTIONS.priority

        #print conflist
        #print jsondata
        data= json.dumps(jsondata)
        #print data
        url = "http://localhost:5000/beacon"

        request_object = urllib2.Request(url, data)

        #make the request using the request object as an argument, store response in a variable
        response = urllib2.urlopen(request_object)

        #store request response in a string
        html_string = response.read()
        print html_string
        

     
    




if __name__ == '__main__':
    main()
