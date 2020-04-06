# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Infoblox classes
import requests
from requests.auth import HTTPBasicAuth
import classes.classes
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ibSession=requests.session()

def getInfoblox(url):
    globalsconf=classes.classes.globalvars()
    url = 'https://' + globalsconf['ipamipaddress'] + "/wapi/v2.10/" + url
    response=requests.get(url, auth=HTTPBasicAuth(globalsconf['ipamuser'], globalsconf['ipampassword']), verify=False)
    return response.json()