# (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

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
        # Login to the switch. The cookie value is stored in the session cookie jar
        response = sessionid.post(url + "login", params=credentials, verify=False, timeout=1)
        return response.status_code
    except:
        return 401

def logoutcx(url,sessionid):
    try:
        response = sessionid.post(url + "logout", verify=False)
    except:
        return "Logout failure"

def loginswitch (url, username, password, ipaddress, sessionid):
    credentials = {'userName': username, 'password': decrypt("ArubaRocks", password)}
    try:
        # Login to the switch. The cookie value is returned to the calling definition. It is not stored in the cookie jar.
        response = requests.post(url + "login-sessions", verify=False, data=json.dumps(credentials), timeout=1)
        session = response.json()
        cookie = session['cookie']
        return cookie
    except:
        return

def logoutswitch(url,headers):
    try:
        response = requests.delete(url, timeout=1, headers=headers)
    except:
        return "Logout failure"

def sqlQuery(queryStr):
    global engine
    conn=engine.connect()
    result=conn.execute(queryStr)
    conn.close()
    return result

def encrypt(salt, plaintext):
  cipher = XOR.new(salt)
  return str(base64.b64encode(cipher.encrypt(plaintext)),'utf-8')

def decrypt(salt, ciphertext):
  cipher = XOR.new(salt)
  return str(cipher.decrypt(base64.b64decode(ciphertext)),'utf-8')

def getRESTcx(url,id):
    # Obtain device information from the database
    queryStr="select * from devices where (id = '{}')".format(str(id))
    result=sqlQuery(queryStr)
    for rows in result:
        baseurl="https://{}/rest/v1/".format(rows['ipaddress'])
        username=rows['username']
        password=rows['password']
        ipaddress=rows['ipaddress']
    # Login to the switch
    response=logincx(baseurl, username, password,ipaddress,sessionid)
    if response==200:
        # If login is successful, obtain information from the switch based on the url in the request
        try:
            response=sessionid.get(baseurl +url, verify=False, timeout=1)
            try:
                # If the response contains information, the content is converted to json format
                response=json.loads(response.content)
            except:
                response="No data"
        except:
            return "Error fetching data"
        finally:
            # After information is obtained, logout of the switch again
            logoutcx(baseurl,sessionid)
        return response
    elif response==401:
        # If the response code is 401, there is either an authentication error, or the maximum number of sessions has been exceeded
        return "Not online"
    return "No information"

def getRESTswitch(url,id):
    # Obtain device information from the database
    queryStr="select * from devices where (id = '{}')".format(str(id))
    result=sqlQuery(queryStr)
    for rows in result:
        baseurl="http://{}/rest/v4/".format(rows['ipaddress'])
        username=rows['username']
        password=rows['password']
        ipaddress=rows['ipaddress']
    # Login to the switch
    response=loginswitch(baseurl, username, password,ipaddress,sessionid)
    #If there is a value returned
    if response is not None:
        try:
            headers = {'cookie': response}
            response=sessionid.get(baseurl + url, verify=False, timeout=1, headers=headers )
            try:
                # If the response contains information, the content is converted to json format
                response=json.loads(response.content)
            except:
                response="No data"
        finally:
            # After information has been obtained, logout of the switch
            logoutswitch(baseurl + "login-sessions",headers)
        return response
    elif response==401:
        # If the response code is 401, there is either an authentication error, or the maximum number of sessions has been exceeded
        return "Not online"
    return "No information"

def discoverModel(id):
    # Performing REST calls to discover what switch model we are dealing with
    # Check whether device is ArubaOS-CX
    url="system?attributes=platform_name&depth=3"
    try:
        response =getRESTcx(url,id)
        if 'platform_name' in response:
            # This is an ArubaOS-CX switch. Getting the software version
            url="firmware"
            swInfo=getRESTcx(url,id)
            if 'current_version' in swInfo:
                return {'ostype':'arubaos-cx','platform_name':response['platform_name'],'swversion':swInfo['current_version']}
            else:
                return {'ostype':'arubaos-cx','platform_name':response['platform_name'],'swversion':'Unknown'}
    except:
        return {'ostype':'Unknown','platform_name':'Unknown','swversion':'Unknown'}
    # Check whether the device is ArubaOS-Switch by obtaining the local lldp information
    url="lldp/local_device/info"
    try:
        response =getRESTswitch(url,id)
        if 'system_description' in response:
            # This is an ArubaOS-Switch switch. System description is a comma separated string that contains product and version information
            # Splitting the string into a list and then assign the values
            sysInfo=response['system_description'].split(",")
            return {'ostype':'arubaos-switch','platform_name':sysInfo[0],'swversion':sysInfo[1]}
    except:
        return {'ostype':'Unknown','platform_name':'Unknown','swversion':'Unknown'}
    return {'ostype':'Unknown','platform_name':'Unknown','swversion':'Unknown'}    
