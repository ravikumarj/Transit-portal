Beacon
======

At present to run simple experiment Transit Portal requires significant manual configuration which includes having openvpn tunnel 
connection to the MUXES(border routers) from where we intend to announce our prefixes.
We propose to have Beacon which will be pre configured with openvpn tunnels to all the available MUXES and have Beacon client which will allow researchers to make announcement through the Beacon Server.This improves openness of the Transit portal which is currently used only be select group of people

Client:

Since a REST interface is used at the scheduler, anyone who is able to POST a request with JSON message will be able to schedule a request 
and are not binded to our client scripts. Authentication information should be included in every request
Configuration Message should be specified in JSON format with key value pairs.

{
    "username": "ravi",
    "password": "test",
    "configuration": [
        {
            "data": "73,74",
            "mux": "WISC"
        },
        {
            "data": "withdraw",
            "mux": "ISI"
        }
    ],
 "priority" : "default"
}


where 
*username & password are authentication information.                                                                                        
*configuration is a json Array and can include any number of MUXES through which user wishes to make announcement.                          
*mux includes MUX names through which user wishes to make announcements.                                                                    
*data includes AS numbers which uses wishes to poison.data can also include withdraw which enables users to announce from one MUX and                  withdraw the same prefix from different MUX. data can also be empty in which it won't poison any AS during announcement.
*priority : As specified in above sections it can include values from 1-10 and if not specified scheduler will use default values.

Usage of the client script:
python client_rpc.py -a -m Conf1 -m Conf2 -u username -p password -l priority 

-a     - Annoucement
-c     - Check
-m    - Mux configuration multiple ASN separated by comma
-t      - transaction ID
-u     -username
-p     -password
-l     -priority level

For example if we wish to make priority level 9(lower)announcement through WISC MUX and poison AS 93 and 94 it can be specified as 
python client_rpc.py -a -m WISC.93,94 -u ravi -p test -l 9

Multiple AS numbers to be prepended/ poisoned can be separated with comma.

To check announcement schedule  with announcement ID 12345 
python client_rpc.py -c -t 12345 -u ravi -p test       

To Do: (Features that are planned to be included in Beacon)                                                                                                                                                                                                                                   
*Get available MUX from TP database at runtime .                                                                                            *Capability to add prefix dynamically by the user and uses the prefix for experiment.                                                       *Configure an SMTP server for the email messages to be sent via instead of localhost SMTP service.


