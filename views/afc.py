# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
afc = Blueprint('afc', __name__)

from datetime import datetime
from flask import render_template
import uuid

import classes.classes as classes


@afc.route("/afcfabrics", methods=['GET','POST'])
def afcfabrics ():
    authOK=classes.checkAuth("afcfabricsaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        afcfabricuuid=[]
        afcfabrics=[]
        message=""
        try:
            formresult=request.form
        except:
            formresult=[]
        queryStr="select * from afc where infotype='fabrics'"
        afcfabrics=classes.sqlQuery(queryStr,"selectone")
        if afcfabrics is not None:
            if "jsondata" in afcfabrics:
                try:
                    if isinstance(afcfabrics['jsondata'],str):
                        afcfabricNames=json.loads(afcfabrics['jsondata'])
                    else:
                        afcfabricNames=afcfabrics['jsondata']
                    for items in afcfabricNames:
                        afcfabricuuid.append(items['uuid'])
                except:
                    if isinstance(afcfabrics['jsondata'],str):
                        message=afcfabrics['jsondata']
                    else:
                        message="Error obtaining fabric information"
                    afcfabrics['jsondata']=[]
        else:
            message="No AFC integration information available"
            afcfabrics=[]

        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("afcfabrics.html", formresult=formresult, afcfabrics=json.dumps(afcfabrics), afcfabricuuid=afcfabricuuid, message=message, authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@afc.route("/afcswitches", methods=['GET','POST'])
def afcswitches ():
    authOK=classes.checkAuth("afcswitchesaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        try:
            formresult=request.form
        except:
            formresult=[]
        result=classes.getafcSwitches(formresult)
        message=""
        if result['afcfabrics']=="Authentication token header required":
            result['afcswitches']=[]
            result['afcfabric']=""
            result['afcfabrics']=[]
            message=result['afcfabrics']
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("afcswitches.html", formresult=formresult, afcfabrics=result['afcfabrics'], afcswitches=result['afcswitches'], afcfabric=result['afcfabric'],message=message, totalentries=result['totalentries'],pageoffset=result['pageoffset'],entryperpage=result['entryperpage'], authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@afc.route("/afcintegrations", methods=['GET','POST'])
def afcintegrations ():
    authOK=classes.checkAuth("afcintegrationsaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        try:
            formresult=request.form
        except:
            formresult=[]
        queryStr="select * from afc where infotype='integrations'"
        result=classes.sqlQuery(queryStr,"selectone")
        if result is not None:
            if isinstance(result,str):
                result=json.loads(result)
            if result['jsondata']=='"Authentication token header required"':
                message="Authentication token header required"   
                afcintegrations="[]" 
            else:
                message=""
                afcintegrations=result['jsondata']
        else:
            afcintegrations="[]"
            message="No AFC integration information available"
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("afcintegrations.html", formresult=formresult, afcintegrations=afcintegrations, authOK=authOK, message=message, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK)
    else:
        return render_template("login.html")


@afc.route("/afcauditlog", methods=['GET','POST'])
def afcauditlog ():
    authOK=classes.checkAuth("afcauditlogaccess","submenu")
    if authOK!=0:
        if authOK['hasaccess']==True:
            sysvars=classes.globalvars()
            queryStr="select COUNT(*) as totalentries from afcaudit"
            navResult=classes.sqlQuery(queryStr,"selectone")
            authOK['hasaccess']="true"
            return render_template("afcauditlog.html", pageoffset=1, entryperpage=25,totalentries=navResult['totalentries'], authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK)
    else:
        return render_template("login.html")


@afc.route("/afcauditItem", methods=['GET','POST'])
def afcauditItem ():
    queryStr="select * from afcaudit where id='{}'".format(request.args.get('id'))
    auditInfo=classes.sqlQuery(queryStr,"selectone")
    auditInfo['jsondata']=json.loads(auditInfo['jsondata'])
    templateName="afcauditTemplates/" + auditInfo['jsondata']['event_type'] + ".html"
    return render_template(templateName, auditInfo=auditInfo)


@afc.route("/afcvmwareinventory", methods=['GET','POST'])
def afcvmareinventory ():
    authOK=classes.checkAuth("afcvmwareinventoryaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        try:
            formresult=request.form
        except:
            formresult=[]
        queryStr="select * from afc where infotype='vmwareinventory'"
        afcvmwareinventory=classes.sqlQuery(queryStr,"selectone")
        if afcvmwareinventory==None:
            afcvmwareinventory={}
            afcvmwareinventory['jsondata']=[]
            afcvmwareinventory['message']="No VMWare inventory information available"
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("afcvmwareinventory.html", formresult=formresult, afcvmwareinventory=json.dumps(afcvmwareinventory), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@afc.route("/afcfabricStatus", methods=['GET','POST'])
def afcfabricStatus ():
    url="api/fabrics?switches=true&tags=true&include_segments=true"
    afcfabrics=classes.getRestafc(url)
    return afcfabrics


@afc.route("/afcintegrationStatus", methods=['GET','POST'])
def afcintegrationStatus ():
    afcintegrations=[]
    queryStr="select * from afc where infotype='integrations'"
    result=classes.sqlQuery(queryStr,"selectone")
    if result is not None:
        if isinstance(result,str):
            result=json.loads(result)
        if result['jsondata']=='"Authentication token header required"':
            afcintegrations={"message":"Authentication token header required"} 
        else:
            afcintegrations=json.loads(result['jsondata'])
    else:
        afcintegrations={"message":"No AFC integration information available"}
    return json.dumps(afcintegrations)


@afc.route("/afcvmwareinventoryStatus", methods=['GET','POST'])
def afcvmwareinventoryStatus ():
    afcvmwareinventory=classes.afcvmwareInventory()
    return afcvmwareinventory


@afc.route("/afcswitchInfo", methods=['GET','POST'])
def afcswitchInfo ():   
    afcswitchInfo=classes.afcswitchInfo(request.form['uuid'])
    return afcswitchInfo


@afc.route("/afcswitchtopology", methods=['GET','POST'])
def afcswitchtopology():   
    url="api/hosts?all_data=true&uuids={}".format(request.form['uuid'])
    afctopologyInfo=classes.getRestafc(url)
    return afctopologyInfo


@afc.route("/updateafcAudit", methods=['GET','POST'])
def updateafcAudit():   
    formresult=request.form
    response={}
    if int(formresult['pageoffset'])<1:
        pageoffset=0
    else:
        pageoffset = (int(formresult['pageoffset'])-1) * int(formresult['entryperpage'])
    queryStr="select * from afcaudit where record_type like '%{}%' AND stream_id like '%{}%' AND severity like '%{}%' AND description like '%{}%' ORDER BY log_date DESC LIMIT {} offset {} ".format(formresult['searchRecordtype'],formresult['searchStreamid'],formresult['searchSeverity'],formresult['searchDescription'],formresult['entryperpage'],pageoffset)
    result=classes.sqlQuery(queryStr,"select")
    response['result']=result
    queryStr="select COUNT(*) as totalentries from afcaudit where record_type like '%{}%' AND stream_id like '%{}%' AND severity like '%{}%' AND description like '%{}%'".format(formresult['searchRecordtype'],formresult['searchStreamid'],formresult['searchSeverity'],formresult['searchDescription'])
    totalentries=classes.sqlQuery(queryStr,"selectone")
    response['totalentries']=totalentries['totalentries']
    # Verify access
    response["accessright"]=classes.verifyAccess("dhcptrackeraccess", "feature")
    return response


@afc.route("/getafcauditCount",methods=['GET','POST'])
def getafcauditCount():
    formresult=request.form
    totalentries=classes.sqlQuery(formresult['queryStr'],"selectone")
    return str(totalentries['totalentries'])
