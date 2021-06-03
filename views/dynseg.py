# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
import time
dynseg = Blueprint('dynseg', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@dynseg.route("/dsprofile",methods=['GET','POST'])
def dsprofile():
    authOK=classes.checkAuth("ubtprofileaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        result={}
        editProfile={}
        devInfo={}
        cpInfo={}
        mcInfo={}
        message=[]
        authMethod = ["EAP PEAP", "EAP-TLS", "Allow All MAC", "Mac Auth", "PAP", "CHAP"]
        authSource = ["Active Directory", "Local User Database", "Guest User Repository"]
        try:
            formresult=request.form
            members=formresult.getlist("members")
            macauthsource=formresult.getlist("macauthsource")
            macauthmethod=formresult.getlist("macauthmethod")
            dot1xsource=formresult.getlist("dot1xsource")
            dot1xmethod=formresult.getlist("dot1xmethod")
            # Perform the database action for the dynamic segmentation profile (add, edit, delete)
            result,message=classes.dsprofiledbAction(formresult,members,macauthsource,macauthmethod,dot1xsource,dot1xmethod)
            # Obtain ArubaOS-Switch information from the database
            queryStr="select id, description, ipaddress from devices where ostype='arubaos-switch'"
            devInfo=classes.sqlQuery(queryStr,"select")
            # Obtain ClearPass information
            queryStr="select id, description, ipaddress from devices where ostype='ClearPass'"
            cpInfo=classes.sqlQuery(queryStr,"select")
            queryStr="select id, description, ipaddress from devices where ostype='Mobility Controller'"
            mcInfo=classes.sqlQuery(queryStr,"select")
            if formresult['action']=="Edit":
                editProfile=classes.sqlQuery("select * from dsprofiles where id='{}'".format(formresult['id']),"selectone")
        except:
            formresult=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("dsprofile.html",result=result,formresult=formresult, cpInfo=cpInfo,mcInfo=mcInfo,devInfo=devInfo, editProfile=editProfile,authMethod=authMethod,authSource=authSource,message=message, authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@dynseg.route("/dsservice",methods=['GET','POST'])
def dsservice():
    authOK=classes.checkAuth("ubtserviceaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        authMethod = ["EAP PEAP", "EAP-TLS", "Allow All MAC", "Mac Auth", "PAP", "CHAP"]
        authSource = ["Active Directory", "Local User Database", "Guest User Repository"]
        result={}
        editService={}
        mcInfo={}
        profileInfo={}
        profileresult={}
        message=[]
        try:
            formresult=request.form
            result=classes.dsservicedbAction(formresult)
            queryStr="select id, description, ipaddress from devices where ostype='Mobility Controller'"
            mcInfo=classes.sqlQuery(queryStr,"select")
            queryStr="select * from dsprofiles"
            profileInfo=classes.sqlQuery(queryStr,"select")
            if formresult['action']=="Edit":
                editService=classes.sqlQuery("select * from dsservices where id='{}'".format(formresult['id']),"selectone")
                profileresult=classes.getProfile()
        except:
            formresult=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("dsservice.html",result=result,formresult=formresult,mcInfo=mcInfo,profileInfo=profileInfo,editService=editService,profileresult=profileresult,authMethod=authMethod,authSource=authSource,message=message,authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@dynseg.route('/profileInfo/<profile>')
def profileInfo(profile):
    profileInfo={}
    queryStr="select * from dsprofiles where id='{}'".format(profile)
    profileInfo=classes.sqlQuery(queryStr,"selectone")
    queryStr="select id,ipaddress,description from devices where id='{}'".format(profileInfo['clearpass'])
    clearpassInfo={"clearpass":classes.sqlQuery(queryStr,"selectone")}
    queryStr="select id,ipaddress,description from devices where id='{}'".format(profileInfo['primarycontroller'])
    primarycontrollerInfo={"primarycontroller":classes.sqlQuery(queryStr,"selectone")}
    queryStr="select id,ipaddress,description from devices where id='{}'".format(profileInfo['backupcontroller'])
    backupcontrollerInfo={"backupcontroller":classes.sqlQuery(queryStr,"selectone")}
    if backupcontrollerInfo['backupcontroller']:
        profileInfo.update(backupcontrollerInfo)
    profileInfo.update(clearpassInfo)
    profileInfo.update(primarycontrollerInfo)  
    return json.dumps(profileInfo)

@dynseg.route('/devauth/<profile>/<devauth>')
def devauth(profile,devauth):
    # Obtain the authentication methods and source from the profile
    if devauth=="dot1x":
        queryStr="select dot1xmethod,dot1xsource from dsprofiles where id='{}'".format(profile)
    elif devauth=="macauth":
        queryStr="select macauthmethod,macauthsource from dsprofiles where id='{}'".format(profile)
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@dynseg.route('/mcVLAN/<mcid>')
def mcVLAN(mcid):
    #Definition that obtains the VLAN information from the selected Mobility Controller
    if mcid=="None":
        vlanresult={'vlan_name_id': [{'name': 'Primary Controller', 'vlan-ids': 'Select'}]}
    else:
        vlanresult=classes.getVLANinfo(mcid)   
    return json.dumps(vlanresult)

@dynseg.route('/mcROLE/<mcid>')
def mcROLE(mcid):
    #Definition that obtains the VLAN information from the selected Mobility Controller
    if mcid=="None":
        roleresult={'vlan_name_id': [{'name': 'Primary Controller', 'vlan-ids': 'Select'}]}
    else:
        roleresult=classes.getRolesinfo(mcid)    
    return json.dumps(roleresult)

@dynseg.route('/serviceVLAN/<mcid>/<vlan>')
def serviceVLAN(mcid,vlan):
    if vlan=="None":
        vlanresult={"action":"select"}
    elif vlan=="Create VLAN":
        vlanresult={"action":"create"}
    else:
        vlanresult=classes.getVLANint(mcid,vlan)
        vlaninfo=classes.getVLANidname(mcid,vlan)
        vlanresult.update(vlaninfo)
    return json.dumps(vlanresult)

@dynseg.route('/serviceRole/<mcid>/<role>')
def serviceROLE(mcid,role):
    if role=="None":
        roleresult={"action":"select"}
    elif role=="Create role":
        roleresult={"action":"create"}
    else:
        roleresult=[{"role":role}]
        roleresult.append(classes.getRoleinfo(mcid,role))
    return json.dumps(roleresult[1])

@dynseg.route('/mergeRole/<roles>/<role>')
def mergeRole(roles,role):
    roles=classes.converttoJSON(roles)
    role=json.loads(role)
    if isinstance(roles, str):
        roles=[role]    
    else:
        roles.append(role)
    return json.dumps(roles)

@dynseg.route('/serviceInfo',methods=['GET', 'POST'])
def serviceInfo():
    serviceInfo=classes.getService(request.form['serviceid'])
    return serviceInfo

@dynseg.route('/provisionSwitch',methods=['GET', 'POST'])
def provisionSwitch():
    result=classes.provisionSwitch(request.form['deviceid'],json.loads(request.form['workflow']))
    return json.dumps(result)

@dynseg.route('/provisionCPProfile',methods=['GET', 'POST'])
def provisionCPProfile():
    result=[]
    time.sleep(1)
    return json.dumps(result)

@dynseg.route('/provisionCPPolicy',methods=['GET', 'POST'])
def provisionCPPolicy():
    result=[]
    time.sleep(1)
    return json.dumps(result)

@dynseg.route('/provisionCPService',methods=['GET', 'POST'])
def provisionCPService():
    result=[]
    time.sleep(1)
    return json.dumps(result)