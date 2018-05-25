# (C) Copyright 2018 Hewlett Packard Enterprise Development LP

import requests
sessionid = requests.Session()

import json

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from Crypto.Cipher import XOR
import base64

from sqlalchemy import *
engine=create_engine('mysql://aruba:ArubaRocks@localhost:3306/Aruba', echo=True)

def logincx (url, username, password, ipaddress, sessionid):
    credentials={'username': username,'password': decrypt("ArubaRocks", password) }
    try:
        response = sessionid.post(url + "login", params=credentials, verify=False, timeout=2)
        return response.status_code
    except:
        return 401

def logoutcx(url,sessionid):
    response = sessionid.post(url + "logout", verify=False)
    return response.status_code

def sqlQuery(queryStr):
    global engine
    conn=engine.connect()
    result=conn.execute(queryStr)
    conn.close()
    return result

def encrypt(salt, plaintext):
  cipher = XOR.new(salt)
  return str(base64.b64encode(cipher.encrypt(plaintext)),'utf-8')
  #print(str(classes.encrypt(salt, plaintext),'utf-8'))

def decrypt(salt, ciphertext):
  cipher = XOR.new(salt)
  return str(cipher.decrypt(base64.b64decode(ciphertext)),'utf-8')
  #print(classes.decrypt(salt, ciphertext))

def checkStatus(url,username,password,cookies, deviceid,ipaddress):
    response=logincx(url, username, password,ipaddress,sessionid)
    if response==200:
        response=sessionid.get(url +"system?attributes=mgmt_intf_status&depth=0", verify=False )
        datastore=json.loads(response.content)
        response=datastore['mgmt_intf_status']['hostname'] + " is online"
        logoutcx(url,sessionid)
        return response
    elif response==401:
        return "Login failure"
    return response

