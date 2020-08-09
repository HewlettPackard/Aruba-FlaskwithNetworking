# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# System Administration classes

import classes.classes
from datetime import date, datetime, time, timedelta
import requests
import time
from requests.auth import HTTPBasicAuth
import urllib3
import ssl
import json
import secrets
from http import cookies
from flask import request

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import psutil, sys, os, platform, subprocess, socket
from subprocess import Popen, PIPE

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def checkAuth(item, type):
    #Definition that verifies whether the cookie is still valid for the user. If it is valid, return 1, if not valid return 0
    # In addition, we have to check the RBAC, check whether the user is allowed access. If no access, we will add it to the dictionary that is returned
    # If 0 is returned, a logout occurs, which we don't want to happen if the cookie is still valid
    try:
        queryStr="select * from sysuser where username='{}' and cookie='{}'".format(request.cookies['username'],request.cookies['token'])
        result=classes.classes.sqlQuery(queryStr,"selectone")
        if result:
            # The cookie is valid, now we need to check whether the user is allowed access
            hasaccess=verifyAccess(item, type)
            authOK={'username':result['username'],'token':result['cookie'],'hasaccess': hasaccess }
        else:
            authOK=0
    except:
        authOK=0
    return authOK

def verifyAccess(item, type):
    #Definition that verifies whether user has access to the item
    try:
        queryStr="select * from sysuser where username='{}' and cookie='{}'".format(request.cookies['username'],request.cookies['token'])
        result=classes.classes.sqlQuery(queryStr,"selectone")
        queryStr="select accessrights from sysrole where id='{}'".format(result['role'])
        roleresult=classes.classes.sqlQuery(queryStr,"selectone")
        accessrights=json.loads(roleresult['accessrights'])
        # There are three different items, two for the menus in the navbar and one for the functions. The type variable identified this (menu, submenu or feature)
        if type=="menu":
            if item in accessrights:
                # If the item exists, this means that the menu item can be displayed
                return True
            else:
                return False
        elif type=="submenu":
            if accessrights[item]=="1" or accessrights[item]=="2":
                # Read only or write 
                return True
            else:
                return False
        elif type=="feature":
            #We need to check what type of access is allowed (read-write). This is typically for edit and delete actions
            if accessrights[item]=="2":
                # Write access 
                return True
            else:
                return False
    except:
        return {}
    return {}

def submitLogin(username,password):
    globalsconf=classes.classes.globalvars()
    queryStr="select * from sysuser where username ='{}'".format(username)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    try:
        if result['password']!="":
        # Check whether the user exists and if it exists, whether the password matches. If there is a match we have to create and set a session cookie and update 
        # the database
            if classes.classes.decryptPassword(globalsconf['secret_key'], result['password'])==password:
                # Set and Store the cookie. Cookie has to contain the username and the cookie value
                token = secrets.token_urlsafe(24)
                cookievals = {'username':username,'token':token}
                queryStr="update sysuser set cookie='{}' where id='{}'".format(token,result['id'])
                classes.classes.sqlQuery(queryStr,"selectone")
                return cookievals
            else:
                return 0
        else:
            # There is no password stored in the database, force password change for user admin
            return 2
    except:
        return 0
    return 0

def changePassword(username,password):
    globalsconf=classes.classes.globalvars()
    try:
        encpass=classes.classes.encryptPassword(globalsconf['secret_key'],password)
        queryStr="update sysuser set password='{}' where username='{}'".format(encpass,username)
        classes.classes.sqlQuery(queryStr,"selectone")
    except:
        pass
		
def checksysConf():
    # This definition is used to check whether the hardware in the system has changed, so this is not for changing the parameters
	# 
    globalsconf=classes.classes.globalvars()
    sysInfo=classes.classes.getSystemInfo()
    pathname = os.path.dirname(sys.argv[0]) 
    if platform.system()=="Windows":
        appPath = os.path.abspath(pathname) + "\\"
    else:
        appPath = os.path.abspath(pathname) + "/"
    globalsconf.update({"sysInfo":json.loads(sysInfo)})
    globalsconf.update({"netInfo":psutil.net_if_addrs()})
    with open('bash/globals.json', 'w') as systemconfig:
        systemconfig.write(json.dumps(globalsconf))


def submitsysConf(sysconf):
    globalsconf={}
    sysInfo=classes.classes.getSystemInfo()
    pathname = os.path.dirname(sys.argv[0]) 
    appPath = os.path.abspath(pathname) + "/"
    sysconf=sysconf.to_dict(flat=True)
    if sysconf['ztppassword']=="":
        sysconf['ztppassword']="ztpinit"
    # First we have to check whether the secret has changed. If it has, then refresh all the user passwords in the sysuser table
    if sysconf['orig_secret_key']!=sysconf['secret_key']:
        # Secret keys are different. We have to change the passwords of all the users in the database
        queryStr="select * from sysuser"
        result=classes.classes.sqlQuery(queryStr,"select")
        for pwitems in result:
            try:
                # Decrypt the password with the old secret
                decpass=classes.classes.decryptPassword(sysconf['orig_secret_key'], pwitems['password']) 
                # Encrypt the password with the new secret
                encpass=classes.classes.encryptPassword(sysconf['secret_key'], decpass) 
                queryStr="update sysuser set password='{}' where username='{}'".format(encpass,pwitems['username'])
                classes.classes.sqlQuery(queryStr,"selectone")
            except:
                # Something went wrong with the password change.
                pass
        # If the shared secret has changed, then all the user passwords have to be hashed with the new secret key. This applies to all the passwords in the devices database
        queryStr="select id, password from devices"
        result=classes.classes.sqlQuery(queryStr,"select")
        for pwitems in result:
            try:
                # Decrypt the password with the old secret
                decpass=classes.classes.decryptPassword(sysconf['orig_secret_key'], pwitems['password']) 
                # Encrypt the password with the new secret
                encpass=classes.classes.encryptPassword(sysconf['secret_key'], decpass) 
                queryStr="update devices set password='{}' where id='{}'".format(encpass,pwitems['id'])
                classes.classes.sqlQuery(queryStr,"selectone")
            except:
                # Something went wrong with the password change.
                pass
        # If the shared secret has failed, also change the admin user accounts in ZTP devices
        queryStr="select id, adminpassword from ztpdevices"
        result=classes.classes.sqlQuery(queryStr,"select")
        for pwitems in result:
            if pwitems['adminpassword']!="":
                try:
                    # Decrypt the password with the old secret
                    decpass=classes.classes.decryptPassword(sysconf['orig_secret_key'], pwitems['adminpassword']) 
                    # Encrypt the password with the new secret
                    encpass=classes.classes.encryptPassword(sysconf['secret_key'], decpass) 
                    queryStr="update ztpdevices set adminpassword='{}' where id='{}'".format(encpass,pwitems['id'])
                    classes.classes.sqlQuery(queryStr,"selectone")
                except:
                    # Something went wrong with the password change.
                    pass    
    # Finally, update the globals configuration file
    for key, items in sysconf.items():
        # Store the values in a dictionary
        if key=="action" or key=="orig_secret_key" or key=="orig_ztppassword":
            continue
        else:
            globalsconf.update( { key : items} )
    globalsconf.update({"appPath":appPath})
    globalsconf.update({"softwareRelease":"1.3"})
    globalsconf.update({"sysInfo":json.loads(sysInfo)})
    globalsconf.update({"netInfo":psutil.net_if_addrs()})
    with open('bash/globals.json', 'w') as systemconfig:
        systemconfig.write(json.dumps(globalsconf))

def userdbAction(formresult):
    # This definition is for all the database actions for the user administration
    if(bool(formresult)==True):
        if(formresult['action']=="Submit user"):
            # First check if the user or e-mail address already exists
            queryStr="select * from sysuser where username='{}' or email='{}'".format(formresult['username'],formresult['email'])
            if checkdbExist(queryStr)==0:
                queryStr="insert into sysuser (username,password,email, cookie, role) values ('{}','{}','{}','{}','{}')".format(formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!", formresult['password']), formresult['email'],"", formresult['role'])
                classes.classes.sqlQuery(queryStr,"insert")
                checkroleStatus(formresult['role'])
            else:
                print("User already exists")
            result=classes.classes.sqlQuery("select * from sysuser","select")
        elif  (formresult['action']=="Submit changes"):
            if(formresult['username']=="admin"):
                queryStr="update sysuser set email='{}' where id='{}'".format(formresult['email'],formresult['id'])
            else:
                queryStr="update sysuser set username='{}',password='{}',email='{}', role='{}' where id='{}' "\
                .format(formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!", formresult['password']),formresult['email'], formresult['role'], formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
            # And update the status of the assigned role to 1
            queryStr="update sysrole set status='1' where id='{}'".format(formresult['role'])
            classes.classes.sqlQuery(queryStr,"update")
            checkroleStatus(formresult['orgrole'])
            result=classes.classes.sqlQuery("select * from sysuser","select")
        elif (formresult['action']=="Delete"):
            queryStr="select role from sysuser where id='{}'".format(formresult['id'])
            roleInfo=classes.classes.sqlQuery(queryStr,"selectone")
            queryStr="delete from sysuser where id='{}'".format(formresult['id'])
            classes.classes.sqlQuery(queryStr,"delete")
            checkroleStatus(roleInfo['role'])
            result=classes.classes.sqlQuery("select * from sysuser","select")
        elif (formresult['action']=="order by username"):
            result=classes.classes.sqlQuery("select * from sysuser order by username ASC","select")
        elif (formresult['action']=="order by email"):
            result=classes.classes.sqlQuery("select * from sysuser order by email ASC","select")
        else:
            result=classes.classes.sqlQuery("select * from sysuser","select")
    else:
        result=classes.classes.sqlQuery("select * from sysuser","select")
    # Select the roles from the database
    roleResult=classes.classes.sqlQuery("select id, name from sysrole","select")
    response={"roleresult":roleResult,"userresult":result}
    return response

def roledbAction(formresult):
    # This definition is for all the database actions for the user administration
    searchAction="None"
    constructQuery=""
    if(bool(formresult)==True):
        accessrights={i:formresult[i] for i in formresult if i not in ['id','currentpageoffset', 'totalpages', 'entryperpage','currententryperpage','searchName','name','action']}
        if(formresult['action']=="Submit role"):
            # First check if the role name already exists
            queryStr="select * from sysrole where name='{}'".format(formresult['name'])
            if checkdbExist(queryStr)==0:
                queryStr="insert into sysrole (name,accessrights,status) values ('{}','{}','{}')".format(formresult['name'],json.dumps(accessrights),'0')
                classes.classes.sqlQuery(queryStr,"insert")
            else:
                print("Role name already exists")
            result=classes.classes.sqlQuery("select * from sysrole","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update sysrole set name='{}', accessrights='{}' where id='{}'".format(formresult['name'],json.dumps(accessrights),formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
            result=classes.classes.sqlQuery("select * from sysrole","select")
        elif (formresult['action']=="Delete"):
            queryStr="delete from sysrole where id='{}'".format(formresult['id'])
            classes.classes.sqlQuery(queryStr,"delete")
            result=classes.classes.sqlQuery("select * from sysrole","select")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName']:
            constructQuery += " where name like'%" + formresult['searchName'] + "%' " 
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from sysrole " + constructQuery
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from sysrole " + constructQuery + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from sysrole"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from sysrole LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def checkroleStatus(role):
    #This definition checks whether a role still has users assigned. If not, then the role needs to be set to 0 (unassigned). System is only allowed to delete a role when it
    # is not assigned to any user
    queryStr="select COUNT(*) as totalentries from sysuser where role='{}'".format(role)
    roleresult=classes.classes.sqlQuery(queryStr,"selectone")
    if roleresult['totalentries']==0:
        # There are no more users assigned to this role. We can set the status for this role to 0
        queryStr="update sysrole set status='0' where id='{}'".format(role)
        classes.classes.sqlQuery(queryStr,"update")
    else:
        # There are no more users assigned to this role. We can set the status for this role to 0
        queryStr="update sysrole set status='1' where id='{}'".format(role)
        classes.classes.sqlQuery(queryStr,"update")


def checkdbExist(queryStr):
    result=classes.classes.sqlQuery(queryStr,"select")
    if result:
        return 1
    else:
        return 0

def checkProcess(name):
    globalsconf=classes.classes.globalvars()
    for proc in psutil.process_iter():
        # Need to check whether the listener process or the scheduler process is queried
        if name=="Cleanup" or name=="Topology" or name=="ZTP" or name=="Telemetry":
            try:
                if "python" in proc.name().lower():
                    procinfo=psutil.Process(proc.pid)
                    try:
                        procname=procinfo.cmdline()[1]
                        if name.lower() in procname.lower():
                            procMem="%.3f" % procinfo.memory_percent()
                            processInfo={"status":True,"cpu":procinfo.cpu_percent(),"memory":procMem}
                            return processInfo
                    except:
                        return {"status":False,"cpu":0,"memory":0}
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        elif name=="Listener":
            try:
                if "listener" in proc.name().lower():
                    procinfo=psutil.Process(proc.pid)
                    procname=json.dumps(procinfo.open_files())
                    if name.lower() in procname.lower():
                        procMem="%.3f" % procinfo.memory_percent()
                        processInfo={"status":True,"cpu":procinfo.cpu_percent(),"memory":procMem}
                        return processInfo
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return {"status":False,"cpu":0,"memory":0}

def processAction(name, action):
    globalsconf=classes.classes.globalvars()
    pathname = os.path.dirname(sys.argv[0])
    if action =="Stop":
        # Need to check whether the listener process or the scheduler process is queried
        if name=="Cleanup" or name=="Topology" or name=="ZTP" or name=="Telemetry":
            for proc in psutil.process_iter():
                processname=globalsconf['appPath'] + "bash/" + name.lower()
                cmdline=proc.cmdline()
                if len(cmdline)>1:
                    if processname in cmdline[1]:
                        proc.kill()
        elif name=="Listener":
            for proc in psutil.process_iter():
                if any(procstr in proc.name() for procstr in ['dumpcap','listener.sh','tshark']):
                    proc.kill()
        logfileName="/var/www/html/log/"+name.lower()+".log"
        logInfo = open(logfileName, 'a')
        logInfo.write("{}: {} process stopped manually.\n".format(datetime.now(),name))
        logInfo.close()
    elif action == "Start":
        if name=="Listener":
            scriptName=globalsconf['appPath'] + "bash/" + name.lower() + ".sh"
            proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
        else:
            scriptName="python3 " + globalsconf['appPath'] + "bash/" + name.lower() + ".py"
            proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
        logfileName="/var/www/html/log/"+name.lower()+".log"
        logInfo = open(logfileName, 'a')
        logInfo.write("{}: {} process started manually.\n".format(datetime.now(),name))
        logInfo.close()

def checkPhpipam(info):
    try:
        url=info['phpipamauth'] + "://" + info['ipamipaddress'] + "/api/" + info['phpipamappid'] + "/user/"
        result = requests.post(url, auth=(info['ipamuser'], info['ipampassword']), verify=False, timeout=10)
        if result.status_code==200:
            return "Online"
        else:
            return "Offline"
    except:
        return "Offline"

def checkInfoblox(info):
    try:
        url = 'https://' + info['ipamipaddress'] + "/wapi/v2.10/network"
        result=requests.get(url, auth=HTTPBasicAuth(info['ipamuser'], info['ipampassword']), verify=False, timeout=10) 
        if result.status_code==200:
            return "Online"
        else:
            return "Offline"
    except:
        return "Offline"
