# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request,json
devices = Blueprint('devices', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@devices.route("/", methods=['GET', 'POST'])
def index ():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.devicedbAction(formresult)
        return render_template("switch.html",result=result['result'],switchos=result['switchos'], platforms=result['platforms'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/switches", methods=['GET', 'POST'])
def switches ():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.devicedbAction(formresult)
        return render_template("switch.html",result=result['result'], switchos=result['switchos'], platforms=result['platforms'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars, entryExists=result['entryExists'])
    else:
        return render_template("login.html")

@devices.route("/portAccess", methods=['GET','POST'])
def portAccess ():
    sysvars=classes.globalvars()
    # Obtain the device information
    queryStr="select id, ipaddress, description from devices where id='{}'".format(request.args.get('deviceid'))
    deviceInfo=classes.sqlQuery(queryStr,"selectone")
    # Obtain the port access information from the device
    result=classes.portAccess(request.args.get('deviceid'))
    return render_template("portaccess.html", accessInfo=result, deviceInfo=deviceInfo)

@devices.route("/backupInfo", methods=['GET','POST'])
def backupInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from configmgr where id='{}'".format(formresult['id'])
    # Obtain the relevant device information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@devices.route("/branchBackup", methods=['GET','POST'])
def branchBackup ():
    sysvars=classes.globalvars()
    formresult=request.form
    # Based on the action, perform a branch backup submit, or edit submit
    if formresult['action']=="submitBranch":
        try:
            id= classes.branchBackup(formresult['deviceid'], formresult['masterbackup'], formresult['sysuser'], formresult['backupContent'], formresult['backuptype'], formresult['backupDescription'])  
            # Result is the newly created ID
        except:
            print("Branch backup not created")
    elif formresult['action']=="submitbackupChanges":
        classes.changebranchBackup(formresult['id'], formresult['deviceid'], formresult['masterbackup'], formresult['sysuser'], formresult['backupContent'], formresult['backuptype'], formresult['backupDescription'])  
        id=formresult['id']
    queryStr="select * from configmgr where id='{}'".format(id)
    # Obtain the relevant device information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@devices.route("/configmgr", methods=['GET','POST'])
def configmgr ():
    sysvars=classes.globalvars()
    if request.args.get('searchconfigDescription') is None:
        searchconfigDescription=""
    else:
        searchconfigDescription=request.args.get('searchconfigDescription')
    queryStr="select id,ipaddress,description from devices where id='{}'".format(request.args.get('deviceid'))
    deviceinfo=classes.sqlQuery(queryStr,'selectone')
    # Action: running Backup, startup Backup, view backup
    if request.args.get('action')=="deleteBackup":
        classes.deleteBackup(request.args.get('id'))
    elif request.args.get('action')=="runningConfig":
        # Depends on the ostype
        if request.args.get('ostype')=="arubaos-switch":
            classes.runningbackupSwitch(request.args.get('deviceid'),request.args.get('sysuser'))
        else:
            classes.runningbackupCX(request.args.get('deviceid'),request.args.get('sysuser'))
    elif request.args.get('action')=="startupConfig":
        # Depends on the ostype
        if request.args.get('ostype')=="arubaos-switch":
            classes.startupbackupSwitch(request.args.get('deviceid'),request.args.get('sysuser'))
        else:
            classes.startupbackupCX(request.args.get('deviceid'),request.args.get('sysuser'))
    configresult=classes.configdbAction(request.args.get('deviceid'),request.args.get('masterbackup'),request.args.get('backuptype'),request.args.get('owner'),searchconfigDescription,request.args.get('action'),request.args.get('configentryperpage'),request.args.get('configpageoffset'))
    return render_template("switchconfig.html", result=configresult['result'], searchOwner=request.args.get('owner'), masterbackup=request.args.get('masterbackup'), backuptype=request.args.get('backuptype'), searchconfigDescription=searchconfigDescription, deviceinfo=deviceinfo, ownerinfo=configresult['ownerinfo'], configtotalentries=configresult['configtotalentries'],configpageoffset=configresult['configpageoffset'],configentryperpage=configresult['configentryperpage'])

@devices.route("/resetClient", methods=['GET','POST'])
def resetClient ():
    sysvars=classes.globalvars()
    formresult=request.form
    result=classes.clearClient(formresult['deviceid'],formresult['macaddress'],formresult['port'],formresult['authmethod'])
    return json.dumps(result)

@devices.route("/deviceInfo", methods=['GET','POST'])
def deviceInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from devices where id='{}'".format(formresult['id'])
    # Obtain the relevant device information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    result['password']=classes.decryptPassword(sysvars['secret_key'],result['password'])
    return json.dumps(result)


@devices.route("/clearpass", methods=['GET', 'POST'])
def clearpass ():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant ClearPass information from the database
        result=classes.clearpassdbAction(formresult)
        return render_template("clearpass.html",result=result['result'], platformResult=result['platformResult'],osversionResult=result['osversionResult'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/mobility", methods=['GET', 'POST'])
def mobility ():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant Mobility Controller information from the database
        result=classes.mobilitydbAction(formresult)
        return render_template("mobility.html",result=result['result'], platformResult=result['platformResult'],osversionResult=result['osversionResult'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/deviceinfo", methods=['GET','POST'])
def deviceinfo ():
    sysvars=classes.globalvars()
    authOK=classes.checkAuth()
    if authOK!=0:
        # Definition for the main device monitoring page. If no switch has been selected, only the select form is rendered (deviceinfo.html). 
        # Based on the information that is returned from the deviceInformation definition, a cx or switch page is rendered
        devInfo={}
        interface=""
        interfaces={}
        isOnline=""
        try:
            formresult=request.form
        except:
            formresult=[]
        if formresult:
            queryStr="select ipaddress, username, password, ostype, sysinfo, interfaces from devices where id='{}'".format(formresult['deviceid'])
            devInfo=classes.sqlQuery(queryStr,"selectone")
            if devInfo is not None:
                interfaces=json.loads(devInfo['interfaces'])
                sysinfo=json.loads(devInfo['sysinfo'])
                ostype=devInfo['ostype']
            else:
                ostype="none"
                sysinfo="none"
                interfaces="none"
            if 'interface' in formresult:
                interface=formresult['interface']
            isOnline=classes.checkifOnline(formresult['deviceid'],ostype)
        else:
            ostype="none"
        queryStr="select id, description, ipaddress, ostype, platform, osversion from devices where ostype='arubaos-cx' or ostype='arubaos-switch' or ostype is NULL"
        devicelist=classes.sqlQuery(queryStr,"select")
        if ostype=="arubaos-cx":
            return render_template("deviceinfocx.html", formresult=formresult, interfaces=interfaces, interface=interface, ostype=ostype, devicelist=devicelist, isOnline=isOnline, authOK=authOK, sysvars=sysvars)
        elif ostype=="arubaos-switch":
            return render_template("deviceinfoswitch.html",devicelist=devicelist, sysinfo=sysinfo, formresult=formresult, interfaces=interfaces, interface=interface, ostype=ostype, isOnline=isOnline, authOK=authOK, sysvars=sysvars)
        else:
            return render_template("deviceinfo.html", formresult=formresult, devInfo=devInfo, devicelist=devicelist, authOK=authOK,sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/mcroleInfo", methods=['GET', 'POST'])
def mcroleInfo ():
    # Obtain the relevant Mobility Controller information from the database
    result=classes.mcroleInfo(request.form['deviceid'])
    return result

@devices.route("/mcpolicyInfo", methods=['GET', 'POST'])
def mcpolicyInfo ():
    # Obtain the relevant Mobility Controller information from the database
    result=classes.mcpolicyInfo(request.form['deviceid'])
    return result

@devices.route("/mcinterfaceInfo", methods=['GET', 'POST'])
def mcinterfaceInfo ():
    # Obtain the relevant Mobility Controller information from the database
    result=classes.mcinterfaceInfo(request.form['deviceid'])
    return result

@devices.route("/deviceStatus", methods=['GET','POST'])
def deviceStatus ():
    # Obtain the online/offline status of the device
    result={"status":classes.checkifOnline(request.form['deviceid'],request.form['ostype'])}
    return json.dumps(result)

@devices.route("/cpStatus", methods=['GET','POST'])
def cpStatus ():
    # Obtain the online/offline status of ClearPass
    print(request.form['deviceid'])
    result={"status": classes.checkcpOnline(request.form['deviceid'])}
    return json.dumps(result)

@devices.route("/mcStatus", methods=['GET','POST'])
def mcStatus ():
    # Obtain the online/offline status of the Mobility Controller
    result={"status": classes.checkmcOnline(request.form['deviceid'])}
    return json.dumps(result)