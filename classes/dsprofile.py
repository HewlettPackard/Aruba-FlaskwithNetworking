# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic Aruba Dynamic Segmentation Profiles classes

import classes.classes
import requests, json
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def dsprofiledbAction(formresult,members,macauthsource,macauthmethod,dot1xsource,dot1xmethod):
    # This definition is for all the database actions for Dynamic Segmentation Profile, based on the user click on the pages
    message=[]
    if(bool(formresult)==True):
        # There are two checkboxes for enabling MacAuth and Dot1x. Need to convert this to 0 or 1. If the boxes are not checked, no value is returned
        # If the returned value is "on", then item is selected
        if "macauth" in formresult:
            macauth=1
        else:
            macauth=0
        if "dot1x" in formresult:
            dot1x=1
        else:
            dot1x=0
        if "maclimit" in formresult:
            maclimit=formresult['maclimit']
        else:
            maclimit=0
        if "dot1xlimit" in formresult:
            dot1xlimit=formresult['dot1xlimit']
        else:
            dot1xlimit=0
        if(formresult['action']=="Submit profile"):   
            queryStr="insert into dsprofiles (name,members,ports,macauth,maclimit,dot1x,dot1xlimit,clearpass,radiussecret,duradmin,durpassword,macauthsource,macauthmethod, \
            dot1xsource,dot1xmethod,ntpserver,ntpauth,primarycontroller,backupcontroller) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')" \
            .format(formresult['name'],json.dumps(members),formresult['ports'],macauth,maclimit,dot1x,dot1xlimit, formresult['clearpass'], \
            formresult['radiussecret'],formresult['duradmin'],formresult['durpassword'],json.dumps(macauthsource),json.dumps(macauthmethod), \
            json.dumps(dot1xsource),json.dumps(dot1xmethod), formresult['ntpserver'],formresult['ntpauth'],formresult['primarycontroller'], \
            formresult['backupcontroller']) 
            deviceid=classes.classes.sqlQuery(queryStr,"insert")
            # Build the list
            result=classes.classes.sqlQuery("select * from dsprofiles","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update dsprofiles set name='{}',members='{}', ports='{}',macauth='{}',maclimit='{}',dot1x='{}',dot1xlimit='{}',clearpass='{}', \
            radiussecret='{}',duradmin='{}',durpassword='{}',macauthsource='{}',macauthmethod='{}',dot1xsource='{}',dot1xmethod='{}',ntpserver='{}', \
            ntpauth='{}',primarycontroller='{}', backupcontroller='{}' where id='{}'".format(formresult['name'],json.dumps(members),formresult['ports'], \
            macauth,maclimit,dot1x, dot1xlimit,formresult['clearpass'],formresult['radiussecret'],formresult['duradmin'],formresult['durpassword'], \
            json.dumps(macauthsource),json.dumps(macauthmethod), json.dumps(dot1xsource),json.dumps(dot1xmethod),formresult['ntpserver'], \
            formresult['ntpauth'],formresult['primarycontroller'], formresult['backupcontroller'],formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
            # Build the list
            result=classes.classes.sqlQuery("select * from dsprofiles","select")
        elif (formresult['action']=="Delete"):
            queryStr="select name from dsservices where profile='{}'".format(formresult['id'])
            serviceInfo=classes.classes.sqlQuery(queryStr,"select")
            if serviceInfo:
                message=["-","Profile associated to service. Not removed!"]
            else:
                queryStr="delete from dsprofiles where id='{}'".format(formresult['id'])
                classes.classes.sqlQuery(queryStr,"delete")
                message=["+","Profile deleted"]
            # Build the list
            result=classes.classes.sqlQuery("select * from dsprofiles","select")
        elif (formresult['action']=="order by name"):
            result=classes.classes.sqlQuery("select * from dsprofiles order by name ASC","select")
        else:
            result=classes.classes.sqlQuery("select * from dsprofiles","select")
    else:
        result=classes.classes.sqlQuery("select * from dsprofiles","select")
    return result,message

def dsprofileInfo(profileID,sqlfield):
    devlist=[]
    result=classes.classes.sqlQuery("select {} from dsprofiles where id='{}'".format(sqlfield,profileID),"selectone")
    # Filter on result
    if sqlfield=="members":
        memberList=json.loads(result['members'])
        for items in memberList:
            devresult=classes.classes.sqlQuery("select ipaddress,description from devices where id='{}'".format(items),"selectone")
            if devresult:
                devlist.append(devresult['ipaddress'] + " (" + devresult['description'] + ")")
        return devlist
    return devlist

    