# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Websockets classes

import classes.classes
import classes.arubaoscx
import requests
import urllib3
import ssl
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getSubscriptions(deviceid, subscriber_name):
    url = "system/notification_subscribers/" + subscriber_name +"/notification_subscriptions?depth=3"
    try:
        result=classes.classes.getRESTcx(deviceid,url)
    except:
        print("Error obtaining subscription information from device")
    print(result)
    return result