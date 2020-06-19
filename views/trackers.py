# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
import time
trackers = Blueprint('trackers', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@trackers.route("/snmptracker",methods=['GET','POST'])
def snmptracker():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("snmptracker",formresult['id'])
        except:
            pass
        result=classes.snmpdbAction()
        return render_template("snmptracker.html",formresult=formresult,totalentries=result['totalentries'],versionInfo=result['versionInfo'], communityInfo=result['communityInfo'],pageoffset=0,entryperpage=25, authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@trackers.route("/dhcptracker",methods=['GET','POST'])
def dhcptracker():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("dhcptracker",formresult['id'])
        except:
            pass
        result=classes.dhcpdbAction()
        return render_template("dhcptracker.html",formresult=formresult,totalentries=result['totalentries'],dhcptypeInfo=result['dhcptypeInfo'],pageoffset=0,entryperpage=25, authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@trackers.route("/syslog",methods=['GET','POST'])
def syslog():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("syslog",formresult['id'])
        except:
            pass
        result=classes.syslogdbAction()
        return render_template("syslog.html",formresult=formresult,totalentries=result['totalentries'],severityInfo=result['severityInfo'],facilityInfo=result['facilityInfo'],pageoffset=0,entryperpage=25, authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@trackers.route("/updateDHCPtracker",methods=['GET','POST'])
def updateDHCPtracker():
    formresult=request.form
    response={}
    if int(formresult['pageoffset'])<1:
        pageoffset=0
    else:
        pageoffset = (int(formresult['pageoffset'])-1) * int(formresult['entryperpage'])
    queryStr="select * from dhcptracker where dhcptype like '%{}%' AND information like '%{}%' ORDER BY utctime DESC LIMIT {} offset {} ".format(formresult['searchType'],formresult['searchInfo'],formresult['entryperpage'],pageoffset)
    result=classes.sqlQuery(queryStr,"select")
    response['result']=result
    queryStr="select COUNT(*) as totalentries from dhcptracker where dhcptype like '%{}%' AND information like '%{}%'".format(formresult['searchType'],formresult['searchInfo'])
    totalentries=classes.sqlQuery(queryStr,"selectone")
    response['totalentries']=totalentries['totalentries']
    return json.dumps(response)

@trackers.route("/updateSNMPtracker",methods=['GET','POST'])
def updateSNMPtracker():
    formresult=request.form
    response={}
    if int(formresult['pageoffset'])<1:
        pageoffset=0
    else:
        pageoffset = (int(formresult['pageoffset'])-1) * int(formresult['entryperpage'])
    queryStr="select * from snmptracker where source like '%{}%' AND version like '%{}%' AND community like '%{}%' AND information like '%{}%' ORDER BY utctime DESC LIMIT {} offset {} ".format(formresult['searchSource'],formresult['searchVersion'],formresult['searchCommunity'],formresult['searchInfo'],formresult['entryperpage'],pageoffset)
    result=classes.sqlQuery(queryStr,"select")
    response['result']=result
    queryStr="select COUNT(*) as totalentries from snmptracker where source like '%{}%' AND version like '%{}%' AND community like '%{}%' AND information like '%{}%'".format(formresult['searchSource'],formresult['searchVersion'],formresult['searchCommunity'],formresult['searchInfo'])
    totalentries=classes.sqlQuery(queryStr,"selectone")
    response['totalentries']=totalentries['totalentries']
    return json.dumps(response)

@trackers.route("/updateSyslogtracker",methods=['GET','POST'])
def updateSyslogtracker():
    formresult=request.form
    response={}
    if int(formresult['pageoffset'])<1:
        pageoffset=0
    else:
        pageoffset = (int(formresult['pageoffset'])-1) * int(formresult['entryperpage'])
    queryStr="select * from syslog where source like '%{}%' AND facility like '%{}%'AND severity like '%{}%' AND information like '%{}%' ORDER BY utctime DESC LIMIT {} offset {} ".format(formresult['searchSource'],formresult['searchFacility'],formresult['searchSeverity'],formresult['searchInfo'],formresult['entryperpage'],pageoffset)
    result=classes.sqlQuery(queryStr,"select")
    response['result']=result
    queryStr="select COUNT(*) as totalentries from syslog where source like '%{}%' AND facility like '%{}%'AND severity like '%{}%' AND information like '%{}%'".format(formresult['searchSource'],formresult['searchFacility'],formresult['searchSeverity'],formresult['searchInfo'])
    totalentries=classes.sqlQuery(queryStr,"selectone")
    response['totalentries']=totalentries['totalentries']
    return json.dumps(response)

@trackers.route("/getTrackercount",methods=['GET','POST'])
def getTrackercount():
    formresult=request.form
    totalentries=classes.sqlQuery(formresult['queryStr'],"selectone")
    return str(totalentries['totalentries'])

@trackers.route("/deleteTrackerentry",methods=['GET','POST'])
def deleteTrackerentry():
    formresult=request.form
    try:
        queryStr="delete from {} where id='{}'".format(formresult['dbtable'],formresult['id'])
        result=classes.sqlQuery(queryStr,"selectone")
        return "200"
    except:
        return "400"