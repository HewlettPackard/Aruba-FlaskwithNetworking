# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
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
from ldap3 import Server, Connection, Tls, ALL, SUBTREE
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
    globalsconf=classes.classes.globalvars()
    if globalsconf['authsource']=="ldap":
        if bool(request.cookies)==False:
            authOK=0
        else:
            hasaccess=verifyAccess(item, type)
            authOK={'username':request.cookies['username'],'token':request.cookies['token'],'hasaccess': hasaccess }
    else:
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
    #Definition that verifies whether user has access to the item. RBAC is only supported for local authentication. If the authentication source is LDAP, everything is allowed
    globalsconf=classes.classes.globalvars()
    if (globalsconf['authsource']=="ldap"):
        return True
    else:
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
    # If the authentication source is LDAP, we need to authenticate against the LDAP server. If the LDAP server is not available, we need to fallback to local authentication
    if globalsconf['authsource']=="ldap":
        if checkldap(username, password, globalsconf['ldapsource'], globalsconf['basedn'],"submitLogin")['message']=="LDAP connection successful":
            print("LDAP connection is successful")
            # Set a cookie. Cookie has to contain the username and the cookie value
            token = secrets.token_urlsafe(24)
            cookievals = {'username':username,'token':token}
            return cookievals
        else:
            # To add: if local fallback is enabled, perform local authentication
            if "localfallback" in globalsconf:
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
                except:
                    return 0
            else:
                return 0
    else:
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
    # Update the globals configuration file
    for key, items in sysconf.items():
        # Store the values in a dictionary
        if key=="action" or key=="orig_secret_key" or key=="orig_ztppassword":
            continue
        else:
            globalsconf.update( { key : items} )
    globalsconf.update({"appPath":appPath})
    globalsconf.update({"softwareRelease":"2.2"})
    globalsconf.update({"sysInfo":json.loads(sysInfo)})
    globalsconf.update({"netInfo":psutil.net_if_addrs()})
    with open('bash/globals.json', 'w') as systemconfig:
        systemconfig.write(json.dumps(globalsconf))
    # Update the timezone (if configured)
    if "timezoneregion" in sysconf and "timezonecity" in sysconf:
        # There is a timezone configuration. If these variable have a value, then set the timezone
        if sysconf['timezoneregion']!="" and sysconf['timezonecity']!="":
            # Set the timezone
            scriptName="timedatectl set-timezone " + sysconf['timezoneregion'] + "/" + sysconf['timezonecity']
            proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
    # If there is an NTP server configured, make sure that this one is added (or replaced) and that NTP is enabled and active
    if sysconf['ntpserver']!="":
        # Need to edit the /etc/systemd/timesyncd.conf file and add/remove/change the NTP server entry
        with open('/etc/systemd/timesyncd.conf', 'r') as ntpconfig:
            ntplines = ntpconfig.readlines()
        ntpconfig.close()
        # Iterate through the lines. If there is no NTP server entry in the list with the given IP address, we have to append. If there is an entry with the same IP address we don't have to do anything
        ntpExists=False
        timeheaderExists=False
        for items in ntplines:
            if sysconf['ntpserver'] in items:
                ntpExists=True
            if "[Time]" in items:
                timeheaderExists=True
        if timeheaderExists==False:
            # There is no time header. We have to append this to the configuration file
            ntpconfig = open('/etc/systemd/timesyncd.conf', 'a')
            ntpconfig.write("[Time]")
            ntpconfig.close()
        if ntpExists==False:
            # We need to add the NTP server
            ntpconfig = open('/etc/systemd/timesyncd.conf', 'a')
            ntpconfig.write("\nNTP=" + sysconf['ntpserver'])
            ntpconfig.close()
        scriptName="timedatectl set-ntp true"
        proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
        scriptName="systemctl restart systemd-timedated"
        proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
        scriptName="systemctl restart systemd-timesyncd.service"
        proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)



def userdbAction(formresult):
    # This definition is for all the database actions for the user administration
    constructQuery=""
    roleResult=classes.classes.sqlQuery("select id, name from sysrole","select")
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
            result=classes.classes.sqlQuery("select * from sysuser" + constructQuery,"select")
        elif  (formresult['action']=="Submit changes"):
            if(formresult['username']=="admin"):
                queryStr="update sysuser set email='{}' where id='{}'".format(formresult['email'],formresult['userid'])
            else:
                queryStr="update sysuser set username='{}',password='{}',email='{}', role='{}' where id='{}' "\
                .format(formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!", formresult['password']),formresult['email'], formresult['role'], formresult['userid'])
            classes.classes.sqlQuery(queryStr,"update")
            # And update the status of the assigned role to 1
            queryStr="update sysrole set status='1' where id='{}'".format(formresult['role'])
            classes.classes.sqlQuery(queryStr,"update")
            checkroleStatus(formresult['orgrole'])
            result=classes.classes.sqlQuery("select * from sysuser" + constructQuery,"select")
        elif (formresult['action']=="Delete"):
            queryStr="select role from sysuser where id='{}'".format(formresult['userid'])
            roleInfo=classes.classes.sqlQuery(queryStr,"selectone")
            queryStr="delete from sysuser where id='{}'".format(formresult['userid'])
            classes.classes.sqlQuery(queryStr,"delete")
            checkroleStatus(roleInfo['role'])
            result=classes.classes.sqlQuery("select * from sysuser" + constructQuery,"select")
        else:
            result=classes.classes.sqlQuery("select * from sysuser" + constructQuery,"select")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""
        if formresult['searchName'] or formresult['searchEmail'] or formresult['searchRole']:
            constructQuery= " where id is not NULL AND "
        else:
            constructQuery="      "
        if formresult['searchName']:
            constructQuery += " username like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchEmail']:
            constructQuery += " email like '%" + formresult['searchEmail'] + "%' AND "
        if formresult['searchRole']:
            # This one is more tough. The sysuser table holds the id of the role, not the name. We need to use the roleresult, to check which roles contain the text
            roleList=[]
            for items in roleResult:
                if formresult['searchRole'] in items['name']:
                    # We need to add the id to the list
                    roleList.append(items['id'])
            constructQuery +=  " role in (" + str(roleList)[1:-1] + ") AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from sysuser " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from sysuser " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from sysuser"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=10
        pageoffset=0
        result=classes.classes.sqlQuery("select * from sysuser","select")
    
    # Select the roles from the database
    response={"roleresult":roleResult,"userresult":result,'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}
    return response


def userldapAction(formresult):
    # This definition is for all the ldap actions for the user administration  
    globalsconf=classes.classes.globalvars()
    totalentries=0
    if formresult['entryperpage']:
        entryperpage=formresult['entryperpage']
    else:
        entryperpage=10
    if formresult['pageoffset']:
        pageoffset=formresult['pageoffset']
    else:
        pageoffset=0
    ldapstatus=""
    response=checkldap(globalsconf['ldapuser'], globalsconf['ldappassword'], globalsconf['ldapsource'], globalsconf['basedn'],"userldapAction")
    if response['message']=="LDAP connection successful":
        tls_configuration = Tls(validate=ssl.CERT_NONE)
        ldapserver = Server(globalsconf['ldapsource'], use_ssl=True, tls=tls_configuration)
        conn = Connection(ldapserver, user=globalsconf['ldapuser'], password=globalsconf['ldappassword'], auto_bind=True)
        conn.search(search_base = globalsconf['basedn'], search_filter = '(objectClass=user)', search_scope = SUBTREE, attributes = ["cn","userPrincipalName","distinguishedName"])
        totalentries = len(conn.response)
        # We need to extract the proper list based on the page offset and number of entries per page
        userresult=conn.response[int(pageoffset): int(pageoffset)+int(entryperpage)]
        result={"roleresult":{},"userresult":userresult,'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage, ldapstatus:response['message'] }
        conn.unbind()
    else:
        # There is an issue connecting to the LDAP server, we need to return an error message
        result={"roleresult":{},"userresult":{},'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage, ldapstatus:response['message'] }
    return result
    

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
        if name=="Cleanup" or name=="Topology" or name=="ZTP" or name=="Telemetry" or name=="Device-upgrade":
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
        if name=="Cleanup" or name=="Topology" or name=="ZTP" or name=="Telemetry"  or name=="Device-upgrade":
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

def checkldap(ldapuser, ldappassword, ldapsource, basedn, calldef):
    response={}
    tls_configuration = Tls(validate=ssl.CERT_NONE)
    ldapserver = Server(ldapsource, use_ssl=True, tls=tls_configuration, get_info=ALL, connect_timeout=5)
    try:
        conn = Connection(ldapserver, user=ldapuser, password=ldappassword, auto_bind=True, raise_exceptions=True)
        # If the connection is successful, we need to check whether the user exists in the context. This only applies when the user is logging in, not in the system configuration
        if calldef=="submitLogin":
            try:
                uid_filter = "(cn="+ldapuser+")"
                conn.search(search_base = basedn, search_filter=uid_filter,search_scope = SUBTREE)
                if len(conn.response)>0:
                    response['message']="LDAP connection successful"
                else:
                    response['message']="Cannot find user in LDAP"
            except Exception as e:
                response['message']=e
        else:
            response['message']="LDAP connection successful"
        conn.unbind()
    except Exception as e:
        if type(e).__name__=="LDAPInvalidCredentialsResult":
            response['message']="Invalid user credentials"
        elif type(e).__name__=="LDAPSocketOpenError":
            response['message']="LDAP server unreachable"
        else:
            response['message']=e
    return response
