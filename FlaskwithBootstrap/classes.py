# (C) Copyright 2018 Hewlett Packard Enterprise Development LP

import requests, json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def logincx(url,creds):
    # Login to the switch
    sessionid=requests.Session()
    try:
        response=sessionid.post(url + "login", params=creds, verify=False, timeout=2)
        print("Logged into switch")
    except:
        print ("Error logging in")
        return False
    return sessionid

def logoutcx(url,sessionid):
    # Logout from the switch
    try:
        response=sessionid.post(url + "logout", verify=False, timeout=2)
    except:
        print("Logout error")
        return False

def getvlancx(url,sessionid):
    # Obtaining VLAN information from the ArubaOS-CX switch
    print("Getting VLAN Information")
    try:
        vlans=sessionid.get(url + "system/bridge/vlans?depth=1", verify=False, timeout=2)
    except:
        print("Cannot access the device")
        return False
    return vlans

