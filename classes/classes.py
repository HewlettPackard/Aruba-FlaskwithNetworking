# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
from classes.afc import getRestafc, obtainafcToken, checkafcToken, getafcSwitches, afcauditInfo, afcswitchInfo
from classes.psm import getRestpsm, obtainpsmToken, checkpsmToken
from classes.arubacentral import centralAuthentication, centralAuthorization, checkcentralToken
from classes.clearpass import clearpassdbAction, getRESTcp, checkcpOnline, getendpointInfo, getservicesInfo, gettrustInfo
from classes.arubaoscx import getcxInfo, getcxREST, postcxREST, checkcxCookie
from classes.arubaosswitch import getswitchInfo,anycli,anycliProvision,checkswitchCookie, getswitchREST, postswitchREST
from classes.switch import checkifOnline, discoverModel, devicedbAction, interfacedbAction, showLinechart, portAccess, portAccesscx, clearClient, getswitchFamily
from classes.deviceattributes import deviceattributesdbAction, assignedAttributes, assignswitchAttribute, removeswitchAttribute, showassignedAttributes
from classes.deviceupgrades import upgradescheduledbAction, upgradeprofiledbAction, scheduledbAction, getupgradeInfo, bootSwitch, upgradeprofilesearchDevices, getsoftwareimageList, getupgradeprofileName, getupgradeprofileInfo, getupgradeprofileDevices, getupgradeprofiledeviceInfo, getupgradeprofileStatus
from classes.mobility import mobilitydbAction, loginmc, logoutmc, getRESTmc, mcinterfaceInfo, mcroleInfo,mcpolicyInfo, checkmcOnline
from classes.dsprofile import dsprofiledbAction,dsprofileInfo
from classes.trackers import dhcpdbAction, snmpdbAction, syslogdbAction
from classes.dsservice import dsservicedbAction, getVLANinfo, getVLANint, getVLANidname, getRolesinfo, getRoleinfo, getACLinfo, getProfile, getService, provisionSwitch
from classes.sysadmin import verifyAccess, checkAuth, submitLogin, submitsysConf, userdbAction,userldapAction, roledbAction, changePassword, checkProcess, processAction, checkPhpipam, checkInfoblox, checkldap, submitIntegration, checkAFC, checkPSM
from classes.configmgr import configdbAction, runningbackupSwitch, runningbackupCX, startupbackupSwitch, startupbackupCX, deleteBackup, branchBackup, changebranchBackup
from classes.ztp import ztpdevicedbAction, ztptemplatedbAction, ztpActivate, ztpDeactivate, verifyCredentials
from classes.deviceimages import imagedbAction
from classes.phpipam import PHPipamtoken, PHPipamget
from classes.topology import topodbAction, endpointInfo, checktopoDevice, topoInfo
from classes.infoblox import getInfoblox
from classes.afc import obtainafcToken, checkafcToken, afcvmwareInventory
from classes.telemetry import telemetrydbAction, subscriptionAction, checkRunningws, checkSubscriptions

import requests, os, sys, platform, psutil, subprocess, socket
sessionid = requests.Session()

import json

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import datetime
import time

import pymysql.cursors

import ssl

def convertTime(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%-m/%-d/%Y, %H:%M:%S %p') 


def timeDelta(timestamp):
    timeNow=time.time()
    timeDiff=timeNow-timestamp
    td=datetime.timedelta(seconds=timeDiff)
    days=td.days
    hms=int((timeDiff-(days*84600)))
    hours=int(hms//3600)
    minutes=int((hms-(hours*3600))//60)
    seconds=int((hms- (hours*3600) - (minutes* 60)))
    uptime="Days: {}, hours: {}, minutes: {}, seconds: {}".format(days,hours,minutes,seconds)
    return uptime


def timeDuration(starttime,endtime):
    timeDiff=endtime-starttime
    days, seconds = timeDiff.days, timeDiff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    duration="{} days, {} hours, {} minutes, {} seconds".format(days,hours,minutes,seconds)
    return duration
    

def sysTime():
    sTime=datetime.datetime.now()
    sysTime=dict({"year":sTime.strftime("%Y"),"month":sTime.strftime("%B"),"day":int(sTime.strftime("%d")),"weekday":sTime.strftime("%A"),"hour":int(sTime.strftime("%H")),"minute":int(sTime.strftime("%M")),"second":int(sTime.strftime("%S"))})
    return sysTime


def globalvars():
    queryStr="select datacontent from systemconfig where configtype='system'"
    data=sqlQuery(queryStr,'selectone')
    return(json.loads(data['datacontent']))


def obtainVars(configtype):
    queryStr="select datacontent from systemconfig where configtype='{}'".format(configtype)
    data=sqlQuery(queryStr,'selectone')
    if data==None:
        datacontent={}
    else:
        datacontent=data['datacontent']
    return(datacontent)



def sqlQuery(queryStr, command):
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    with dbconnection.cursor(pymysql.cursors.DictCursor) as cursor:
       if command=="select":
           cursor.execute(queryStr)
           result = cursor.fetchall()
           return result
       elif command=="selectone":
           cursor.execute(queryStr)
           result = cursor.fetchone()
           return result
       elif command=="insert":       
           try:
               cursor.execute(queryStr)
               return cursor.lastrowid
           except pymysql.InternalError as error:
               code, message = error.args
               return (code, message)
       elif command=="update" or command=="delete":       
           try:
               cursor.execute(queryStr)
               result="ok"
           except pymysql.InternalError as error:
               code, message = error.args
               return(code, message)
    dbconnection.close()
    return result


def encryptPassword(salt, password):
    cipher = AES.new(salt.encode(), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(password.encode(), AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    return json.dumps({'iv':iv, 'ciphertext':ct})


def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()


def loopCounter(count, compValue):
    countUp=0
    retval=""
    while countUp<=count:
        if countUp==int(compValue):
            retval +="<option value='" + str(countUp) + "' selected>" + str(countUp) + "</option>"
        else:
            retval +="<option value='" + str(countUp) + "'>" + str(countUp) + "</option>"
        countUp=countUp+1
    return retval


def listofIntegers(input):
    result=[]
    converted=json.loads(input)
    for items in converted:
        result.append(int(items))
    return result


def converttoJSON(input):
    #If the first character is a double quote, we have to remove the first and last character
    if input[0] == '"' and input[-1] == '"':
        input=input[1:-1]
    try:        
        result = json.loads(input)
    except Exception as e:      
        # Find the offending character index:
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))    
        # Remove the offending character:
        input = list(input)
        input[idx_to_replace] = ' '
        new_message = ''.join(input)     
        return converttoJSON(input=new_message)
    return result


def converttoInteger(input):
    if type(input)==str and input:
        input=int(input)
    return input


def jinjasqlQuery(input):
    result=sqlQuery(input,"selectone")
    if isinstance(result,str):
        result=json.loads(result)
    return result


def showdataType(input):
    return type(input)


def deleteEntry(dbtable,id):
    queryStr="delete from {} where id='{}'".format(dbtable,id)
    sqlQuery(queryStr,"selectone")


def getSystemInfo():
    # Obtain system information
    try:
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['processor']=platform.processor()
        info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        return json.dumps(info)
    except Exception as e:
        logging.exception(e)


def factoryDefault(result):
    # Need to do some things here. First is to empty the databases and create the admin user account
    # The default secret is  ArubaRocks!!!!!!
    queryStr=["TRUNCATE `devices`","TRUNCATE `dhcptracker`","TRUNCATE `dsprofiles`","TRUNCATE `dsservices`","TRUNCATE `snmptracker`","TRUNCATE `syslog`","TRUNCATE `sysuser`"]
    for items in queryStr:
        qresult=sqlQuery(items,"update")
    # Now create the new admin user
    queryStr="insert into sysuser (username,password,email, cookie, role) values ('{}','{}','{}','{}','{}')".format("admin",encryptPassword("ArubaRocks!!!!!!", result['password']), "","","0")
    sqlQuery(queryStr,"insert")
    # Finally, update the globalvars config file
    pathname = os.path.dirname(sys.argv[0]) 
    if platform.system()=="Windows":
        appPath = os.path.abspath(pathname) + "\\"
    else:
        appPath = os.path.abspath(pathname) + "/"
    sysInfo=getSystemInfo()
    globalsconf={"idle_timeout": "3000", "pcap_location": "", "retain_dhcp": "10", "retain_snmp": "10", "retain_syslog": "10", "secret_key": "ArubaRocks!!!!!!", "appPath": appPath, "softwareRelease": "1.1"}
    globalsconf.update({"sysInfo":json.loads(sysInfo)})
    globalsconf.update({"netInfo":psutil.net_if_addrs()})
    with open('views/globals.json', 'w') as systemconfig:
        systemconfig.write(json.dumps(globalsconf))


def navigator(queryStr,formresult):
    navresult=sqlQuery(queryStr,"selectone")
    totalentries=navresult['totalentries']
    try:
        formresult['pageoffset']
        pageoffset=formresult['pageoffset']
    except:
        pageoffset=0 
    try:
        if formresult['entryperpage']:
            entryperpage=formresult['entryperpage']
        else:
            entryperpage=25
    except:
        entryperpage=25
    return {'entryperpage':entryperpage,'totalentries':totalentries,'pageoffset':pageoffset}


def checkdbExist(queryStr):
    result=sqlQuery(queryStr,"select")
    if result:
        return 1
    else:
        return 0