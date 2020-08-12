# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request,json
devices = Blueprint('devices', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@devices.route("/", methods=['GET', 'POST'])
def index ():
    authOK=classes.checkAuth("switchaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.devicedbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("switch.html",result=result['result'],switchos=result['switchos'], platforms=result['platforms'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/switches", methods=['GET', 'POST'])
def switches ():
    authOK=classes.checkAuth("switchaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.devicedbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("switch.html",result=result['result'], switchos=result['switchos'], platforms=result['platforms'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars, entryExists=result['entryExists'])
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
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

@devices.route("/createbranchBackup", methods=['GET','POST'])
def createbranchBackup ():
    sysvars=classes.globalvars()
    formresult=request.form
    #Obtain the master backup information
    if formresult:
        queryStr="select * from configmgr where id='{}'".format(formresult['masterbackup'])
        result=classes.sqlQuery(queryStr,"selectone")
        return json.dumps(result)
    else:
        return


@devices.route("/submitbranchBackup", methods=['GET','POST'])
def submitbranchBackup ():
    sysvars=classes.globalvars()
    formresult=request.form
    try:
        id= classes.branchBackup(formresult['deviceid'], formresult['masterbackup'],formresult['backupdescription'], formresult['backuptype'],formresult['backupcontent'],formresult['sysuser'])
        queryStr="select * from configmgr where id='{}'".format(id)
        # Obtain the relevant device information from the database
        result=classes.sqlQuery(queryStr,"selectone")
        return json.dumps(result)
    except:
        pass
    return {}

@devices.route("/changebranchBackup", methods=['GET','POST'])
def changebranchBackup ():
    sysvars=classes.globalvars()
    formresult=request.form
    # Based on the action, perform a branch backup submit, or edit submit
    classes.changebranchBackup(formresult['id'],formresult['sysuser'], formresult['backupContent'], formresult['backupDescription'])  
    id=formresult['id']
    queryStr="select * from configmgr where id='{}'".format(formresult['id'])
    # Obtain the relevant device information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@devices.route("/configmgr", methods=['GET','POST'])
def configmgr ():
    sysvars=classes.globalvars()
    if request.args.get('searchdescription') is None:
        searchdescription=""
    else:
        searchdescription=request.args.get('searchdescription')
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
    configresult=classes.configdbAction(request.args.get('deviceid'),request.args.get('searchmasterbackup'),request.args.get('searchbackuptype'),request.args.get('searchowner'),searchdescription,request.args.get('action'),request.args.get('configentryperpage'),request.args.get('configpageoffset'))
    return render_template("switchconfig.html", result=configresult['result'], searchOwner=request.args.get('searchowner'), searchmasterbackup=request.args.get('searchmasterbackup'), searchbackuptype=request.args.get('searchbackuptype'), searchdescription=searchdescription, deviceinfo=deviceinfo, ownerinfo=configresult['ownerinfo'], configtotalentries=configresult['configtotalentries'],configpageoffset=configresult['configpageoffset'],configentryperpage=configresult['configentryperpage'])

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
    authOK=classes.checkAuth("clearpassaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant ClearPass information from the database
        result=classes.clearpassdbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("clearpass.html",result=result['result'], platformResult=result['platformResult'],osversionResult=result['osversionResult'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/mobility", methods=['GET', 'POST'])
def mobility ():
    authOK=classes.checkAuth("mobilityaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant Mobility Controller information from the database
        result=classes.mobilitydbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("mobility.html",result=result['result'], platformResult=result['platformResult'],osversionResult=result['osversionResult'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@devices.route("/deviceinfo", methods=['GET','POST'])
def deviceinfo ():
    sysvars=classes.globalvars()
    authOK=classes.checkAuth("switchaccess","feature")
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
    result=classes.mcpolicyInfo(request.form['deviceid'], request.form['policy'])
    return result

@devices.route("/mcinterfaceInfo", methods=['GET', 'POST'])
def mcinterfaceInfo ():
    # Obtain the relevant Mobility Controller information from the database
    result=classes.mcinterfaceInfo(request.form['deviceid'])
    return result

@devices.route("/deviceStatus", methods=['GET','POST'])
def deviceStatus ():
    # Obtain the online/offline status of the device
    response={}
    response['deviceid']=request.form['deviceid']
    response['status']=classes.checkifOnline(request.form['deviceid'],request.form['ostype'])
    return json.dumps(response)

@devices.route("/cpStatus", methods=['GET','POST'])
def cpStatus ():
    # Obtain the online/offline status of ClearPass
    result={"status": classes.checkcpOnline(request.form['deviceid'])}
    return json.dumps(result)

@devices.route("/mcStatus", methods=['GET','POST'])
def mcStatus ():
    # Obtain the online/offline status of the Mobility Controller
    result={"status": classes.checkmcOnline(request.form['deviceid'])}
    return json.dumps(result)

@devices.route("/cpEndpoints", methods=['GET','POST'])
def cpEndpoints ():
    result=classes.getendpointInfo(request.args.get('deviceid'),request.args.get('epEntryperpage'),request.args.get('epPageoffset'),request.args.get('searchMacaddress'),request.args.get('searchDescription'),request.args.get('searchStatus'))
    return render_template("cpendpoints.html", endpointInfo=result['endpointInfo'], deviceInfo=result['deviceInfo'], epTotalentries=int(result['epTotalentries']), epEntryperpage=int(result['epEntryperpage']),epPageoffset=int(result['epPageoffset']), searchMacaddress=result['searchMacaddress'],searchDescription=result['searchDescription'], searchStatus=result['searchStatus'])

@devices.route("/cpTrusts", methods=['GET','POST'])
def cpTrusts ():
    result=classes.gettrustInfo(request.args.get('deviceid'),request.args.get('trEntryperpage'),request.args.get('trPageoffset'),request.args.get('searchSubject'),request.args.get('searchValid'),request.args.get('searchStatus'))
    return render_template("cptrusts.html", trustInfo=result['trustInfo'], deviceInfo=result['deviceInfo'], trTotalentries=int(result['trTotalentries']), trEntryperpage=int(result['trEntryperpage']),trPageoffset=int(result['trPageoffset']), searchSubject=result['searchSubject'],searchValid=result['searchValid'], searchStatus=result['searchStatus'])

@devices.route("/cpServices", methods=['GET','POST'])
def cpServices ():
    result=classes.getservicesInfo(request.args.get('deviceid'),request.args.get('seEntryperpage'),request.args.get('sePageoffset'),request.args.get('searchName'),request.args.get('searchType'),request.args.get('searchTemplate'),request.args.get('searchStatus'))
    return render_template("cpservices.html", servicesInfo=result['servicesInfo'], deviceInfo=result['deviceInfo'], seTotalentries=int(result['seTotalentries']), seEntryperpage=int(result['seEntryperpage']),sePageoffset=int(result['sePageoffset']),searchName=result['searchName'],searchType=result['searchType'],searchTemplate=result['searchTemplate'],searchStatus=result['searchStatus'])