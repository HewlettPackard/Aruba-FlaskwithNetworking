# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from datetime import datetime, time, timedelta
import time
import json
import pymysql.cursors
import sys
import os
import requests
import urllib3
import ipaddress
import socket
import base64
from netmiko import ConnectHandler
import paramiko


from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def scheduler():
    upgradelog = open('/var/www/html/log/device-upgrade.log', 'a')
    pathname = os.path.dirname(sys.argv[0])
    appPath = os.path.abspath(pathname) + "/globals.json"
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    # Obtain the active IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    hostip=s.getsockname()[0]
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    # First step is to check whether there are scheduled upgrades. Criteria is that the status=0 and there is either no schedule date or the schedule date has passed the current datetime
    queryStr="select * from softwareupdate where status=0 and (schedule IS NULL or schedule<'{}')".format(datetime.now())
    cursor.execute(queryStr)
    result = cursor.fetchall() 
    for items in result:
        # For the results, we need to set the status of each entry to 1 to mark that the upgrade process has started
        queryStr="update softwareupdate set status=1 where id='{}'".format(items['id'])
        cursor.execute(queryStr)
    # Now obtain all the active upgrades and check the status
    queryStr="select * from softwareupdate where status<100 and status>0"
    cursor.execute(queryStr)
    result = cursor.fetchall()  
    for items in result:
        #Obtain the switch and software information
        queryStr="select id, ipaddress, username, password, osversion,ostype, secinfo from devices where id='{}'".format(items['switchid'])
        cursor.execute(queryStr)
        switchInfo = cursor.fetchall()
        if switchInfo[0]['ostype']=="arubaos-switch":
            switchInfo[0]['secinfo']=checkswitchCookie(cursor,items['id'],switchInfo[0]['ipaddress'],switchInfo[0]['username'],switchInfo[0]['password'],switchInfo[0]['secinfo'], globalconf['secret_key'])
        elif switchInfo[0]['ostype']=="arubaos-cx":
            switchInfo[0]['secinfo']=checkcxCookie(cursor, items['id'], switchInfo[0]['ipaddress'], switchInfo[0]['username'], switchInfo[0]['password'], switchInfo[0]['secinfo'], globalconf['secret_key'])
        queryStr="select * from deviceimages where id='{}'".format(items['software'])
        cursor.execute(queryStr)
        softwareInfo = cursor.fetchall()
        # Per item we need to check the status. Based on the status, we need to perform an action (upload software, verify whether software has been uploaded correctly, set boot partition..
        # If needed, reboot the switch)
        if items['status']==1:
            stageOne(cursor, hostip,items, switchInfo[0], softwareInfo[0], upgradelog)
        elif items['status']==5:
            stageFive(cursor, hostip,items, switchInfo[0], softwareInfo[0], upgradelog)
        elif items['status']==10:
            stageTen(cursor, hostip,items, switchInfo[0], softwareInfo[0], upgradelog)
        elif items['status']==20:
            stageTwenty(cursor, hostip,items, switchInfo[0], softwareInfo[0], upgradelog)
        elif items['status']==50:
            stageFifty(cursor, hostip,items, switchInfo[0], softwareInfo[0], upgradelog)
    upgradelog.close()



def stageOne(cursor, hostip,upgradeInfo,switchInfo,softwareInfo, upgradelog):
    # Uploading the new software
    if switchInfo['ostype']=="arubaos-cx":
        # Put the software on the upgradepartition
        vrf=checkVRF(switchInfo['ipaddress'],switchInfo['secinfo'])
        url = "firmware?image=" + upgradeInfo['imagepartition'] + "&from=http://" + hostip + "/images/" + softwareInfo['filename'] + "&vrf=" + vrf
        pResponse=putRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        if pResponse==200:
            # Software upgrade command has been issued successfully, set stage to 5 (checking whether the software has been uploaded successfully
            # In addition, obtain the current software information and store this as well. Also set the start time
            response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
            queryStr="update softwareupdate set status=5, upgradefrom='{}', softwareinfo='{}', starttime='{}' where id='{}'".format(response['current_version'],json.dumps(response),datetime.now(),upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: Copy software {} onto {}. \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))
        elif pResponse==400:
            # There already seems to be a software upgrade in progress. Setting the stage to 50
            queryStr="update softwareupdate set status=50 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
    elif switchInfo['ostype']=="arubaos-switch":
        imageurl="http://" + hostip + "/images/" + softwareInfo['filename']
        url="file-transfer"
        if upgradeInfo['imagepartition']=="primary":
            imagepartition="BI_PRIMARY_IMAGE"
        else:
            imagepartition="BI_SECONDARY_IMAGE"
        parameters={ "file_type":"FTT_FIRMWARE", "url":imageurl, "action":"FTA_DOWNLOAD", "boot_image":imagepartition}
        response= postRESTswitch(switchInfo['ipaddress'],switchInfo['secinfo'],url,parameters)
        url="file-transfer/status"
        sresponse=getRESTswitch(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        if "message" in response:
            if response['message']=="File transfer initiated":
                cmd="show flash"
                versionInfo=anycli(switchInfo['ipaddress'],switchInfo['secinfo'],cmd) 
                if "error_msg" in versionInfo:
                    if versionInfo['error_msg']=="":
                        versionInfo=convertFlash( base64.b64decode(versionInfo['result_base64_encoded']).decode('utf-8') )
                        # Obtain the current active software version
                        if versionInfo['default_image']=="Primary":
                            originalVersion=versionInfo['primary_version']
                        else:
                            originalVersion=versionInfo['secondary_version']
                        # File transfer has been initialized. Set status to stage 5, check whether software has been uploaded
                        queryStr="update softwareupdate set status=5, upgradefrom='{}', softwareinfo='{}', starttime='{}' where id='{}'".format(originalVersion, json.dumps(versionInfo),datetime.now(),upgradeInfo['id'])
                        cursor.execute(queryStr)
                        upgradelog.write('{}: Copy software {} onto {}. \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))


def stageFive(cursor, hostip,upgradeInfo,switchInfo,softwareInfo, upgradelog):
    # Check whether the software was uploaded successfully
    if switchInfo['ostype']=="arubaos-cx":
        url="firmware/status"
        response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        if "status" in response:
            if response['status']=="success":
                queryStr="update softwareupdate set status=10 where id='{}'".format(upgradeInfo['id'])
                cursor.execute(queryStr)
                # Software has been upgraded successfully. Go to stage 10
                upgradelog.write('{}: Software {} uploaded successfully onto {}. \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))
            elif response['status']=="none":
                queryStr="update softwareupdate set status=1 where id='{}'".format(upgradeInfo['id'])
                cursor.execute(queryStr)
                # Software has not been upgraded. Go back to stage 1
                upgradelog.write('{}: Error copying software {} onto {}. Retrying... \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))

        else:
            pass
    elif switchInfo['ostype']=="arubaos-switch":
        url="file-transfer/status"
        response=getRESTswitch(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        if response['status']=="FTS_COMPLETED":
            # File copy has been completed. Set the status to 10
            queryStr="update softwareupdate set status=10 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: Software {} uploaded successfully onto {}. \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))
        else:
            queryStr="update softwareupdate set status=1 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
            # Software has not been upgraded. Go back to stage 1
            upgradelog.write('{}: Error copying software {} onto {}. Retrying... \n'.format(datetime.now(),softwareInfo['filename'],switchInfo['ipaddress']))

def stageTen(cursor, hostip,upgradeInfo,switchInfo,softwareInfo, upgradelog):
    # Software has been uploaded successfully. Setting boot parameters
    if switchInfo['ostype']=="arubaos-cx":
        # Need to check whether the switch has to be rebooted as instructed by the upgrade job
        if upgradeInfo['reboot']==1:
            # We need to reboot the switch with the proper boot partition
            url="boot?image=" + upgradeInfo['activepartition']
            response=postRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url,'')
            queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: Reboot {} on partition {}. \n'.format(datetime.now(),switchInfo['ipaddress'],upgradeInfo['activepartition'] ))
        else:
            # No reboot, however we do have to tell the system that the switch has to be rebooted. The upgrade job is completed, setting the status to 110
            url="firmware"
            response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
            # Now update the database with the new information and set the status to 100 (completed)
            queryStr="update softwareupdate set status=110, upgradeto='{}', softwareinfoafter='{}', endtime='{}' where id='{}'".format(response['current_version'],json.dumps(response),datetime.now(),upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: No reboot for {} on partition {} as configured in upgrade job. \n'.format(datetime.now(),switchInfo['ipaddress'],upgradeInfo['activepartition'] ))
    elif switchInfo['ostype']=="arubaos-switch":
        # Need to check whether the switch has to be rebooted as instructed by the upgrade job
        if upgradeInfo['reboot']==1:
            # We need to reboot the switch with the proper boot partition
            url="system/reboot"
            if upgradeInfo['imagepartition']=="primary":
                imagepartition="BI_PRIMARY_IMAGE"
            else:
                imagepartition="BI_SECONDARY_IMAGE"
            parameters={ "boot_image":imagepartition}
            response=postRESTswitch(switchInfo['ipaddress'],switchInfo['secinfo'],url,parameters)
            queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: Reboot {} on partition {}. \n'.format(datetime.now(),switchInfo['ipaddress'],upgradeInfo['imagepartition'] ))
        else:
            # No reboot, however we do have to tell the system that the switch has to be rebooted. The upgrade job is completed, setting the status to 110
            # We need to format the version in formation and convert to a dict 
            cmd="show flash"
            versionInfo=anycli(switchInfo['ipaddress'],switchInfo['secinfo'],cmd) 
            if "error_msg" in versionInfo:
                if versionInfo['error_msg']=="":
                    versionInfo=convertFlash( base64.b64decode(versionInfo['result_base64_encoded']).decode('utf-8') )   
                    if versionInfo['default_image']=="Primary":
                        newVersion=versionInfo['primary_version']
                    else:
                        newVersion=versionInfo['secondary_version'] 
                    queryStr="update softwareupdate set status=110, upgradeto='{}', softwareinfoafter='{}', endtime='{}' where id='{}'".format(newVersion, json.dumps(versionInfo),datetime.now(),upgradeInfo['id'])
                    cursor.execute(queryStr)
                    upgradelog.write('{}: No reboot for {} on partition {}. \n'.format(datetime.now(),switchInfo['ipaddress'],upgradeInfo['imagepartition'] ))



def stageTwenty(cursor, hostip,upgradeInfo,switchInfo,softwareInfo, upgradelog):
    # Switch has been rebooted. Check if switch is back online
    if switchInfo['ostype']=="arubaos-cx":
        url="firmware/status"
        response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        if "status" in response:
            if response['status']=="none":
                # Switch is back online and upgraded
                url="firmware"
                response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
                # Now update the database with the new information and set the status to 100 (completed)
                queryStr="update softwareupdate set status=100, upgradeto='{}', softwareinfoafter='{}', endtime='{}' where id='{}'".format(response['current_version'],json.dumps(response),datetime.now(),upgradeInfo['id'])
                cursor.execute(queryStr)
                upgradelog.write('{}: Switch {} is back online. Upgrade finished. \n'.format(datetime.now(),switchInfo['ipaddress'] ))
    elif switchInfo['ostype']=="arubaos-switch":
        # Need to check whether the switch has to be rebooted as instructed by the upgrade job
        cmd="show flash"
        #because the switch has rebooted, a new cookie has to be obtained
        versionInfo=anycli(switchInfo['ipaddress'],switchInfo['secinfo'],cmd) 
        if "error_msg" in versionInfo:
            if versionInfo['error_msg']=="":
                # We have a response and we can store this information in the database and set the status to completed (100). Also set the finish time
                # We need to format the version in formation and convert to a dict
                versionInfo=convertFlash( base64.b64decode(versionInfo['result_base64_encoded']).decode('utf-8') )   
                if versionInfo['default_image']=="Primary":
                    newVersion=versionInfo['primary_version']
                else:
                    newVersion=versionInfo['secondary_version']
                queryStr="update softwareupdate set status=100, upgradeto='{}', softwareinfoafter='{}', endtime='{}' where id='{}'".format(newVersion, json.dumps(versionInfo),datetime.now(),upgradeInfo['id'])
                cursor.execute(queryStr)
                upgradelog.write('{}: Switch {} is back online. Upgrade to {} finished. \n'.format(datetime.now(),switchInfo['ipaddress'], newVersion ))
            else:
                # If there is an error in the response, we try again in the next iteration
                pass


def stageFifty(cursor, hostip,upgradeInfo,switchInfo,softwareInfo, upgradelog):
    # There is already an upgrade in progress. We need to wait until that upgrade has completed and then the upgrade can be performed 
    if switchInfo['ostype']=="arubaos-cx":
        url="firmware/status"
        response=getRESTcx(switchInfo['ipaddress'],switchInfo['secinfo'],url)
        # If status is in_progress or success, then an upgrade is in progress. Don't change status in that case
        if response['status']=="none":
            # We're ok for the upgrade to start now, reset the status to 1
            queryStr="update softwareupdate set status=1 where id='{}'".format(upgradeInfo['id'])
            cursor.execute(queryStr)
            upgradelog.write('{}: Another software upgrade is in progress for {}. Retrying...\n'.format(datetime.now(),switchInfo['ipaddress'] ))


def getRESTcx(ipaddress,cookie_header,url):
    url="https://{}/rest/v1/{}".format(ipaddress,url)
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response = requests.get(url,headers=header, verify=False, timeout=10)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            response={}
    except:
        response={}
    return response


def putRESTcx(ipaddress,cookie_header,url):
    url="https://{}/rest/v1/{}".format(ipaddress,url)
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response = requests.put(url,headers=header, verify=False, timeout=10)
        response = response.status_code
    except:
        response=0
    return response


def postRESTcx(ipaddress,cookie_header,url,parameters):
    url="https://{}/rest/v1/{}".format(ipaddress, url)
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response = requests.post(url,headers=header, data=parameters,verify=False, timeout=20)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            response=response.status_code
    except:
        return {}
    return response


def getRESTswitch(switchip,cookie_header,url):
    # Obtain device information from the database
    url="http://{}/rest/v7/".format(switchip) + url
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response=requests.get(url, verify=False, headers=header)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
    except:
        response={} 
    return response


def postRESTswitch(switchip,cookie_header,url,parameters):
    # Obtain device information from the database
    url="http://{}/rest/v7/{}".format(switchip,url)
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response = requests.post(url, verify=False, data=json.dumps(parameters), headers=header, timeout=20)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
    except:
        response={} 
    return response


def checkIpaddress(ip):
    try:
        ipInfo=bool(ipaddress.ip_address(str(ip)))
        return True
    except:
        return False


def checkVRF(ip,secinfo):
    # Check which VRF has the active IP address
    # Check the management VRF IP address against the configured IP address. If there is a match we need to return the mgmt VRF, else the default VRF
    url="system?attributes=mgmt_intf%2Cmgmt_intf_status&depth=2"
    response=getRESTcx(ip,secinfo,url)
    if response:
        if "ip" in response['mgmt_intf_status']:
            if response['mgmt_intf_status']['ip']==ip:
                return "mgmt"
            else:
                return "default"
        else:
            return "default"
    else:
        return "default"


def anycli(ip,cookie_header,cmd):
    url="http://{}/rest/v7/cli".format(ip)
    sendcmd={'cmd':cmd}
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    try:
        response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd))
        # If the response contains information, the content is converted to json format
        return json.loads(response.content)
    except:
        return {}        


def checkcxCookie(cursor, id, ipaddress, username, password, secinfo, secret_key):
    baseurl="https://{}/rest/v1/".format(ipaddress)
    # First, let's check if we can perform a REST call and get a response 200
    if secinfo is None or secinfo=="":
        # There is no cookie in the secinfo field, we HAVE to login
        credentials={'username': username,'password': decryptPassword(secret_key, password) }
        try:
            # Login to the switch. The cookie value is stored in the session cookie jar
            response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
            if "set-cookie" in response.headers:
                # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                cookie_header = {'Cookie': response.headers['set-cookie']}
                queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,id)
                cursor.execute(queryStr)
            else:
                queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,id)
                cursor.execute(queryStr)
                return            

            return cookie_header
        except:
            # Something went wrong with the login
            queryStr="update devices set switchstatus=100 where id='{}'".format(deviceid)
            cursor.execute(queryStr)
            return
    else:
        try:
            if type(secinfo) is dict:
                header=secinfo
            else:
                header=json.loads(secinfo)
            try:
                response=requests.get(baseurl+"system?attributes=software_info&depth=2",headers=header,verify=False,timeout=5)
                if response.status_code==200:
                    # The cookie is still valid, return the cookie that is stored in the database
                    queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,id)
                    cursor.execute(queryStr)
                    return secinfo
                else:
                    # There is something wrong with the cookie, might be expired or the switch may be out of sessions
                    # If the latter is the case, we need to SSH into the switch and reset the sessions, then try to login again and get the cookie
                    # There could also be an authentication failure, if that is the case, we should return that result code
                    if "Authorization Required" in response.text:
                        # Need to login and store the cookie
                        credentials={'username': username,'password': decryptPassword(secret_key, password) }
                        response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                        if "session limit reached" in response.text:
                            cs=clearSessions(ipaddress, username,decryptPassword(secret_key, password))
                            if cs=="ok":
                                response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                                if "set-cookie" in response.headers:
                                    cookie_header = {'Cookie': response.headers['set-cookie']}
                                else:
                                    cookie_header=""                       
                                queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),id)
                                cursor.execute(queryStr)
                                return cookie_header
                            else:
                                return {}
                        elif "set-cookie" in response.headers:
                            cookie_header = {'Cookie': response.headers['set-cookie']}
                        else:
                            cookie_header=""                       
                        queryStr="update devices set secinfo='{}' where id='{}'".format(json.dumps(cookie_header),id)
                        cursor.execute(queryStr)
                        return cookie_header
                    elif "session limit reached" in response.text:
                        cs=clearSessions(ipaddress, username,decryptPassword(secret_key, password))
                        if cs=="ok":
                            response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                            if "set-cookie" in response.headers:
                                cookie_header = {'Cookie': response.headers['set-cookie']}
                            else:
                                cookie_header=""                       
                            queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),id)
                            cursor.execute(queryStr)
                            return cookie_header
                        else:
                            queryStr="update devices set switchstatus=120 where id='{}'".format(id)
                            cursor.execute(queryStr)
                            return 120
                    else:
                        return
            except:
                pass
        except:
            pass
    return {}


def checkswitchCookie(cursor, id, ipaddress, username, password, secinfo, secret_key):
    # Definition to check whether the cookie for the switch is still valid
    # If not ok, we need to login, and store the new cookie value
    # If login fails, this needs to be reflected in the database as well with the statuscode
    baseurl="http://{}/rest/v7/".format(ipaddress)
    credentials = {"userName": username, "password": decryptPassword(secret_key, password) }
    url="login-sessions"
    # First, let's check if we can perform a REST call and get a response 200
    if secinfo is None or secinfo=="":
        # There is no cookie in the secinfo field, we HAVE to login
        try:
            # Login to the switch. The cookie value is stored in the session cookie jar
            response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
            sessioninfo = response.json()
            if "Set-Cookie" in response.headers:
                # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                cookie_header={'Cookie': sessioninfo['cookie']}
                queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,id)
                cursor.execute(queryStr)
                return cookie_header
            else:
                return                 
        except:
            # Something went wrong with the login
            return
    else :
        try:
            response=requests.get(baseurl+"system",headers=json.loads(secinfo),verify=False,timeout=5)
            if response.status_code==200:
                # The cookie is still valid, return the cookie that is stored in the database
                return secinfo
            else:
                # There is something wrong with the cookie, might be expired or the switch may be out of sessions
                # If the latter is the case, we need to SSH into the switch and reset the sessions, then try to login again and get the cookie
                # There could also be an authentication failure, if that is the case, we should return that result code
                if response.status_code==400:
                    # Need to login and store the cookie
                    response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
                    sessioninfo = response.json()
                    if "Set-Cookie" in response.headers:
                        # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                        cookie_header={'Cookie': sessioninfo['cookie']}
                        queryStr="update devices set secinfo='{}' where id='{}'".format(json.dumps(cookie_header),id)
                        cursor.execute(queryStr)
                        return cookie_header   
                    else:
                        queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,id)
                        cursor.execute(queryStr)
                        return
                elif "session limit reached" in response.text:
                    sr=resetRest(ipaddress,username,password,secret_key)
                    if sr=="ok":
                        response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
                        sessioninfo = response.json()
                        if "Set-Cookie" in response.headers:
                            # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                            cookie_header={'Cookie': sessioninfo['cookie']}
                            queryStr="update devices set secinfo='{}' where id='{}'".format(json.dumps(cookie_header),id)
                            cursor.execute(queryStr)
                            return cookie_header
                        else:
                            queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,id)
                            cursor.execute(queryStr)
                            return
                    else:
                        queryStr="update devices set switchstatus=120 where id='{}'".format(id)
                        cursor.execute(queryStr)
                        return 120
                else:
                    return {}
        except:
            return {} 
    return {}


def resetRest(ipaddress,username,password,secret_key):
    params={'device_type':'hp_procurve','ip':ipaddress,'username':username,'password':decryptPassword(secret_key, password)}
    try:
        net_connect=ConnectHandler(**params)
        net_connect.config_mode()
        commands = ["no rest-interface","rest-interface","end"]
        net_connect.send_config_set(commands)
        net_connect.disconnect()
        return "ok"
    except:
        return "nok"


def clearSessions(ipaddr, username,password):
    try:
        remoteclient=paramiko.SSHClient()
        remoteclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remoteclient.connect(ipaddr,username=username,password=password, timeout=5)
        # Logging in could take some time. Pause a bit
        sleep(5)
        connection=remoteclient.invoke_shell()
        connection.send("\n")
        sleep(3)
        connection.send("https session close all\n")
        sleep(3)
        connection.close()
        remoteclient.close()
        return "ok"
    except:
        return "nok"


def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()



def convertFlash(flashInfo):
    bootInfo={}
    flashInfo=flashInfo.splitlines()
    res = [i for i in flashInfo if "Primary Image" in i]
    bootInfo['primary_version'] = res[0].split()[-1]
    res = [i for i in flashInfo if "Secondary Image" in i]
    bootInfo['secondary_version'] = res[0].split()[-1]
    res = [i for i in flashInfo if "Default Boot Image" in i]
    bootInfo['default_image'] = res[0].split()[-1]
    return bootInfo



