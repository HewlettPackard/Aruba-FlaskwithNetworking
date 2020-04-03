# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic Aruba Configuration classes

import classes.classes
import requests
import base64
from datetime import datetime, time, timedelta
import time
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def configdbAction(deviceid,masterbackup,backuptype,owner,description,action,entryperpage,pageoffset):
    # This definition is for all the database actions for configurations, based on the user click on the pages
    globalsconf=classes.classes.globalvars()
    constructQuery=""
    if entryperpage=="" or entryperpage==None:
        entryperpage=10
    if pageoffset=="" or pageoffset==None:
        pageoffset=0
    if description or owner or backuptype or masterbackup or action=="searchConfig":
        if description:
            constructQuery += " and description like '%" + description + "%'"
        if owner:
            constructQuery += " and owner like '%" + owner + "%'"
        if backuptype:
            constructQuery += " and backuptype = '" + backuptype + "'"
        if masterbackup:
            if masterbackup=="0":
                constructQuery += " and masterbackup = 0"
            elif masterbackup=="1":
                constructQuery += " and masterbackup = 1"
        # We have to construct the query based on the information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from configmgr where deviceid='{}'".format(deviceid) + constructQuery
        navresult=classes.classes.sqlQuery(queryStr,"selectone")
        # We have to construct the query based on the information
        queryStr="select id, deviceid, utctime, description,backuptype, owner, masterbackup from configmgr where deviceid='{}'".format(deviceid) + constructQuery + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        print(queryStr)
        result=classes.classes.sqlQuery(queryStr,"select")
        
        print(result)
    else:
        queryStr="select COUNT(*) as totalentries from configmgr where deviceid='{}'".format(deviceid)
        navresult=classes.classes.sqlQuery(queryStr,"selectone")
        queryStr="select id,deviceid,utctime, description,backuptype, owner, masterbackup from configmgr where deviceid='{}' LIMIT {} offset {}".format(deviceid,entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select distinct owner from configmgr where deviceid='{}'".format(deviceid)
    ownerinfo=classes.classes.sqlQuery(queryStr,'select')
    return {'result':result, 'configtotalentries': navresult['totalentries'], 'configpageoffset': pageoffset, 'configentryperpage': entryperpage, 'ownerinfo':ownerinfo}

def runningbackupSwitch(deviceid,sysuser):
    cmd="show running"
    response=classes.arubaosswitch.anycli(cmd,deviceid)
    result = base64.b64decode(response['result_base64_encoded']).decode('utf-8')
    utctime=datetime.now().timestamp()
    queryStr="insert into configmgr (utctime,deviceid,backuptype,owner,description,configuration, masterbackup) values ('{}','{}','Running configuration','{}','Master running configuration backup created','{}',0)".format(utctime,deviceid,sysuser,result)
    classes.classes.sqlQuery(queryStr,"insert")

def runningbackupCX(deviceid, sysuser):
    url="fullconfigs/running-config?type=cli"
    response=classes.arubaoscx.getRESTcx(deviceid,url)
    result=json.dumps(response, separators=(',',':'))
    utctime=datetime.now().timestamp()
    queryStr="insert into configmgr (utctime,deviceid,backuptype,owner,description,configuration,masterbackup) values ('{}','{}','Running configuration','{}','Master running configuration backup created','{}',0)".format(utctime,deviceid,sysuser,result)
    classes.classes.sqlQuery(queryStr,"insert")

def startupbackupSwitch(deviceid,sysuser):
    cmd="show config structured"
    response=classes.arubaosswitch.anycli(cmd,deviceid)
    result = base64.b64decode(response['result_base64_encoded']).decode('utf-8')
    utctime=datetime.now().timestamp()
    queryStr="insert into configmgr (utctime,deviceid,backupType,owner,description,configuration,masterbackup) values ('{}','{}','Startup configuration','{}','Master startup configuration backup created','{}',0)".format(utctime,deviceid,sysuser,result)
    classes.classes.sqlQuery(queryStr,"insert")

def startupbackupCX(deviceid, sysuser):
    url="fullconfigs/startup-config?type=cli"
    response=classes.arubaoscx.getRESTcx(deviceid,url)
    result=json.dumps(response, separators=(',',':'))
    utctime=datetime.now().timestamp()
    queryStr="insert into configmgr (utctime,deviceid,backuptype,owner,description,configuration,masterbackup) values ('{}','{}','Startup configuration','{}','Master startup configuration backup created','{}',0)".format(utctime,deviceid,sysuser,result)
    classes.classes.sqlQuery(queryStr,"insert")

def branchBackup(deviceid, masterbackup, sysuser, configuration, backuptype, description):
    utctime=datetime.now().timestamp()
    queryStr="insert into configmgr (utctime,deviceid,backuptype,owner,description,configuration,masterbackup) values ('{}','{}','{}','{}','{}','{}','{}')".format(utctime,deviceid,backuptype,sysuser,description,configuration,masterbackup)
    id = classes.classes.sqlQuery(queryStr,"insert")
    return id

def changebranchBackup(id, deviceid, masterbackup, sysuser, configuration, backuptype, description):
    utctime=datetime.now().timestamp()
    queryStr="update configmgr set utctime='{}', owner='{}', description='{}', configuration='{}' where id='{}'".format(utctime, sysuser, description, configuration, id)
    classes.classes.sqlQuery(queryStr,"update")
    return

def deleteBackup(id):
    queryStr="delete from configmgr where id='{}'".format(id)
    classes.classes.sqlQuery(queryStr,"delete")
