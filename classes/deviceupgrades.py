# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Generic Aruba Switch classes

import classes.classes
import requests, json
import psutil, sys, os, platform, subprocess
from datetime import datetime

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  
def upgradescheduledbAction(formresult):
    # This definition is for obtaining the upgrade schedule information for switches
    switchList=[]
    switchresult={}
    if formresult:
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""  
        if formresult['searchName'] or formresult['searchIpaddress']:
            constructdeviceQuery=" where "
            # We need to create a query that obtains the switch IP and description information from the database matching the query
            if formresult['searchName']:
                constructdeviceQuery += "description like'%" + formresult['searchName'] + "%' AND "
            if formresult['searchIpaddress']:
                constructdeviceQuery += "ipaddress like '%" + formresult['searchIpaddress'] + "%' AND "
            # Now obtain the device information
            queryStr="select id, description, ipaddress from devices "+ constructdeviceQuery[:-4]
            switchresult=classes.classes.sqlQuery(queryStr,"select")
            # Now that we have the result from the devices, create a list containing the ID's so that we can add this to the deviceupgrade query
            for items in switchresult:
                switchList.append(items['id'])
            switchList=tuple(switchList)
            switchIds=str(switchList)
            if len(switchList)==1:
                # There is only one element in the list, we need to remove the single comma
                switchIds=switchIds.replace(",","")
        constructQuery="    "
        if (formresult['searchupgradeFrom'] or formresult['searchupgradeTo'] or formresult['searchPartition']  or formresult['searchStatus']) and (formresult['searchName'] or formresult['searchIpaddress']):
            constructQuery=" and "
        elif formresult['searchupgradeFrom'] or formresult['searchupgradeTo'] or formresult['searchPartition'] or formresult['searchStatus']:
            constructQuery=" where "
        if formresult['searchupgradeFrom']:
            constructQuery += " upgradefrom like '%" + formresult['searchupgradeFrom'] + "%' AND "
        if formresult['searchupgradeTo']:
            constructQuery += " upgradeto like '%" + formresult['searchupgradeTo'] + "%' AND "
        if formresult['searchPartition']:
            constructQuery += " activepartition like '%" + formresult['searchPartition'] + "%' AND "
        if formresult['searchStatus']:
            constructQuery += " status=" + formresult['searchStatus'] + " AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        if formresult['searchName'] or formresult['searchIpaddress']:
            queryStr="select COUNT(*) as totalentries from softwareupdate where switchid in {} ".format(switchIds) + constructQuery[:-4]
        else:
            queryStr="select COUNT(*) as totalentries from softwareupdate " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        if formresult['searchName'] or formresult['searchIpaddress']:
            queryStr = "select * from softwareupdate where switchid in {}".format(switchIds) + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
            result=classes.classes.sqlQuery(queryStr,"select")
        else:
            # There is no search for IP address or device information. However we still need to obtain that information 
            queryStr = "select * from softwareupdate " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
            result=classes.classes.sqlQuery(queryStr,"select")
            for items in result:
                switchList.append(items['switchid'])
            switchList=tuple(switchList)
            switchIds=str(switchList)
            if len(switchList)==1:
                # There is only one element in the list, we need to remove the single comma
                switchIds=switchIds.replace(",","")
            if len(switchList)>0:
                queryStr="select id, ipaddress, description from devices where id in {}".format(switchIds)
                switchresult=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from softwareupdate"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        totalentries=navResult['totalentries']
        entryperpage=10
        pageoffset=0
        queryStr="select * from softwareupdate LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
        # Also obtain the switch information based on the switch ID's in the result
        for items in result:
            switchList.append(items['switchid'])
        switchList=tuple(switchList)
        switchIds=str(switchList)
        if len(switchList)==1:
            # There is only one element in the list, we need to remove the single comma
            switchIds=switchIds.replace(",","")
            queryStr="select id, ipaddress, description from devices where id in {}".format(switchIds)
            switchresult=classes.classes.sqlQuery(queryStr,"select")
        elif len(switchList)==0:
            switchresult={}
        else:
            queryStr="select id, ipaddress, description from devices where id in {}".format(switchIds)
            switchresult=classes.classes.sqlQuery(queryStr,"select")
    return {'upgraderesult':result, 'switchresult': switchresult, 'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage}



def upgradeprofiledbAction(formresult):
    # This definition is for obtaining the upgrade schedule information for switches
    if formresult:
        # If profileAction is add or edit, we need to add/edit first, then continue with this function
        if "profileAction"  in formresult:
            if formresult['profileAction']=="add":
                addupgradeProfile(formresult)
            elif formresult['profileAction']=="edit":
                changeupgradeProfile(formresult)
            elif formresult['profileAction']=="Remove":
                removeupgradeProfile(formresult['profileid'])
        try:
           searchAction=formresult['searchAction']
        except:
            searchAction=""  
        if formresult['searchName']:
            constructQuery=" where "
        else:
            constructQuery="    "
        if formresult['searchName']:
            constructQuery += " name like '%" + formresult['searchName'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from upgradeprofiles " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from upgradeprofiles " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from upgradeprofiles"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        totalentries=navResult['totalentries']
        entryperpage=10
        pageoffset=0
        queryStr="select * from upgradeprofiles LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'profileresult':result, 'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def addupgradeProfile(profileInfo):
    # First, the upgrade profile is stored in the upgradeprofile table. After that, for each device an entry is created in the softwareupgrade table that is tied to the profile that has been created
    if "addrebootafterupgrade" in profileInfo:
        reboot=1
    else:
        reboot=0
    if profileInfo['addscheduletime']!="":
        # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
        if datetime.fromisoformat(profileInfo['addscheduletime'].replace(',',''))<datetime.now():
            queryStr="insert into upgradeprofiles (name, devicelist, activepartition, upgradepartition, schedule, reboot, softwareimages,status) values ('{}','{}','{}','{}','{}','{}','{}',1)".format(profileInfo['addprofilename'],profileInfo['assignedDevices'],profileInfo['addupgradepartition'],profileInfo['addactivepartition'],profileInfo['addscheduletime'],reboot,profileInfo['softwareImages'])
        else:
            queryStr="insert into upgradeprofiles (name, devicelist, activepartition, upgradepartition, schedule, reboot, softwareimages,status) values ('{}','{}','{}','{}','{}','{}','{}',0)".format(profileInfo['addprofilename'],profileInfo['assignedDevices'],profileInfo['addactivepartition'],profileInfo['addupgradepartition'],profileInfo['addscheduletime'],reboot,profileInfo['softwareImages'])
    else:
        queryStr="insert into upgradeprofiles (name, devicelist, activepartition, upgradepartition, reboot, softwareimages,status) values ('{}','{}','{}','{}','{}','{}',0)".format(profileInfo['addprofilename'],profileInfo['assignedDevices'],profileInfo['addactivepartition'],profileInfo['addupgradepartition'],reboot,profileInfo['softwareImages'])
    profileid=classes.classes.sqlQuery(queryStr,"insert")
    # the result is the profile id. Now we need to create the entries in the softwareupdate table for each device
    assignedDevices=json.loads(profileInfo['assignedDevices'])
    for items in assignedDevices:
        # First we need to obtain the right software from the repository. This can be tricky because the best way to check is on the device itself. If the device is offline, then we have to base the software
        # version on the information in the database
        queryStr="select id, ipaddress, username, password, ostype, osversion, platform from devices where id='{}'".format(items['id'])
        deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
        bootInfo=getofflineupgradeInfo(deviceInfo)
        if "devicefamily" in bootInfo:
            # We have the devicefamily for this device. Now we need to get a match of the software in the softwareimages
            queryStr="select id from deviceimages where id in ({}) and devicefamily='{}'".format(profileInfo['softwareImages'], bootInfo['devicefamily'])
            imageResult=classes.classes.sqlQuery(queryStr,"selectone")
            # imageresult['id'] is the id for the software image that is attached to this device
            if profileInfo['addscheduletime']!="":
                # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
                if datetime.fromisoformat(profileInfo['addscheduletime'].replace(',',''))<datetime.now():
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom,upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values({},{},'{}','{}','{}',{},'','','','','',{},1)".format(items['id'],imageResult['id'],profileInfo['addupgradepartition'], profileInfo['addactivepartition'],profileInfo['addscheduletime'],reboot,profileid)
                else:
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom,upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values({},{},'{}','{}','{}',{},'','','','','',{},0)".format(items['id'],imageResult['id'],profileInfo['addupgradepartition'], profileInfo['addactivepartition'],profileInfo['addscheduletime'],reboot,profileid)
            else:
                queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values({},{},'{}','{}',{},'','','','','',{},0)".format(items['id'],imageResult['id'],profileInfo['addupgradepartition'], profileInfo['addactivepartition'],reboot,profileid)
            result=classes.classes.sqlQuery(queryStr,"insert")


def removeupgradeProfile(profileid):
    # First, remove all the software upgrades that are tied to this profile
    queryStr="delete from softwareupdate where upgradeprofile={}".format(profileid)
    classes.classes.sqlQuery(queryStr,"delete")
    # Second, remove the upgrade profile
    queryStr="delete from upgradeprofiles where id={}".format(profileid)
    classes.classes.sqlQuery(queryStr,"delete")


def changeupgradeProfile(profileInfo):
    if "editrebootafterupgrade" in profileInfo:
        reboot=1
    else:
        reboot=0
    if profileInfo['editscheduletime']!="":
        # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
        if datetime.fromisoformat(profileInfo['editscheduletime'].replace(',',''))<datetime.now():
            queryStr="update upgradeprofiles set name='{}', devicelist='{}', activepartition='{}', upgradepartition='{}', schedule='{}', reboot={}, softwareimages='{}',status=1 where id='{}'".format(profileInfo['editprofilename'],profileInfo['assignedDevices'],profileInfo['editupgradepartition'],profileInfo['editactivepartition'],profileInfo['editscheduletime'],reboot,profileInfo['softwareImages'], profileInfo['profileid'])
        else:
            queryStr="update upgradeprofiles set name='{}', devicelist='{}', activepartition='{}', upgradepartition='{}', schedule='{}', reboot={}, softwareimages='{}',status=0 where id='{}'".format(profileInfo['editprofilename'],profileInfo['assignedDevices'],profileInfo['editactivepartition'],profileInfo['editupgradepartition'],profileInfo['editscheduletime'],reboot,profileInfo['softwareImages'],profileInfo['profileid'])
    else:
        # There is no schedule time
        queryStr="update upgradeprofiles set name='{}', devicelist='{}', activepartition='{}', upgradepartition='{}', schedule=null, reboot={}, softwareimages='{}',status=1 where id='{}'".format(profileInfo['editprofilename'],profileInfo['assignedDevices'],profileInfo['editactivepartition'],profileInfo['editupgradepartition'],reboot,profileInfo['softwareImages'],profileInfo['profileid'])
    classes.classes.sqlQuery(queryStr,"update")
    assignedDevices=json.loads(profileInfo['assignedDevices'])
    for items in assignedDevices:
        # First we need to obtain the right software from the repository. This can be tricky because the best way to check is on the device itself. If the device is offline, then we have to base the software
        # version on the information in the database
        queryStr="select id, ipaddress, username, password, ostype, osversion from devices where id='{}'".format(items['id'])
        deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
        bootInfo=getofflineupgradeInfo(deviceInfo)
        if "devicefamily" in bootInfo:
            # We have the devicefamily for this device. Now we need to get a match of the software in the softwareimages
            queryStr="select id from deviceimages where id in ({}) and devicefamily='{}'".format(profileInfo['softwareImages'], bootInfo['devicefamily'])
            imageResult=classes.classes.sqlQuery(queryStr,"selectone")
            # imageresult['id'] is the id for the software image that is attached to this device
            if profileInfo['editscheduletime']!="":
                # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
                if datetime.fromisoformat(profileInfo['addscheduletime'].replace(',',''))<datetime.now():
                    queryStr="update softwareupdate set software={},imagepartition='{}',activepartition='{}',schedule='{}',reboot={},upgradeprofile={}, status=1 where (switchid={} and profileid={})".format(imageResult['id'],profileInfo['editupgradepartition'], profileInfo['editactivepartition'],profileInfo['editscheduletime'],reboot,profileInfo['profileid'],items['id'],profileInfo['profileid'])
                else:
                    queryStr="update softwareupdate set software={},imagepartition='{}',activepartition='{}',schedule='{}',reboot={},upgradeprofile={}, status=0 where (switchid={} and profileid={})".format(imageResult['id'],profileInfo['editupgradepartition'], profileInfo['editactivepartition'],profileInfo['editscheduletime'],reboot,profileInfo['profileid'],items['id'],profileInfo['profileid'])
            else:
                # There is no schedule time
                queryStr="update softwareupdate set software={},imagepartition='{}',activepartition='{}', schedule=null, reboot={},upgradeprofile={}, status=1 where (switchid={} and profileid={})".format(imageResult['id'],profileInfo['editupgradepartition'], profileInfo['editactivepartition'],reboot,profileInfo['profileid'],items['id'],profileInfo['profileid'])
            result=classes.classes.sqlQuery(queryStr,"update")


def scheduledbAction(formresult):
    message=""
    # Obtain the device information
    if formresult['action']=="submitUpgrade":
        # If there is already an upgrade entry (status set to 0 which means not active), then we should not add the upgrade
        # If the upgrade status is >0 then the upgrade is in progress and we should be able to add a new upgrade, however, this upgrade should not be executed. This is handled in the upgrade scheduler
        queryStr="select * from softwareupdate where switchid='{}' and status=0".format(formresult['switchid'])
        checkResult=classes.classes.sqlQuery(queryStr,"select")
        if checkResult:
            message="There is already an upgrade entry"
        else:
            if formresult['schedule']!="":
                # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
                if datetime.fromisoformat(formresult['schedule'].replace(',',''))<datetime.now():
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values ('{}','{}','{}','{}','{}','{}','','','','','',0,1)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['schedule'],formresult['reboot'])
                else:
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values ('{}','{}','{}','{}','{}','{}','','','','','',0,0)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['schedule'],formresult['reboot'])
            else:
                queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,upgradeprofile,status) values ('{}','{}','{}','{}','{}','','','','','',0,1)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['reboot'])
            classes.classes.sqlQuery(queryStr,"insert")
    elif formresult['action']=="submitupgradeChanges":
        if formresult['schedule']!="":
            queryStr="update softwareupdate set software='{}',imagepartition='{}',activepartition='{}',schedule='{}',reboot={} where id='{}'".format(formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['schedule'],formresult['reboot'],formresult['id'])
        else:
            queryStr="update softwareupdate set software='{}',imagepartition='{}',activepartition='{}',schedule=NULL,reboot={} where id='{}'".format(formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['reboot'],formresult['id'])
        classes.classes.sqlQuery(queryStr,"update")
    queryStr="select id, ipaddress, description, ostype, platform, osversion from devices where id='{}'".format(formresult['switchid'])
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    bootInfo=classes.classes.getupgradeInfo(deviceInfo)
    bootInfo['message']=message
    bootInfo['deviceInfo']=deviceInfo
    return bootInfo



def getupgradeInfo(deviceInfo):
    # Obtain software version and partition information from the switch based on ostype. 
    bootInfo={}
    if deviceInfo['ostype']=="arubaos-switch":
        # There is no REST call available for AOS-Switch, therefore we have to use anycli
        cliResult=False
        while cliResult==False:
            try:
                header=classes.classes.checkswitchCookie(deviceInfo['id'])
                url="http://{}/rest/v7/cli".format(deviceInfo['ipaddress'])
                sendcmd={'cmd':'show flash'}
                response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd), timeout=4)
                response=response.json()
                if "error_msg" in response:
                    if response['error_msg']=="":
                        cliResult=True
            except:
                pass
        # Now that the image and partition information has been obtained, we need to format this.
        flashInfo=classes.classes.b64decode(response['result_base64_encoded']).decode('utf_8').splitlines()
        res = [i for i in flashInfo if "Primary Image" in i]
        bootInfo['primaryImage'] = res[0].split()[-1]
        res = [i for i in flashInfo if "Secondary Image" in i]
        bootInfo['secondaryImage'] = res[0].split()[-1]
        res = [i for i in flashInfo if "Default Boot Image" in i]
        bootInfo['defaultImage'] = res[0].split()[-1]
        # Next, we need to obtain the software versions that are available for this switch. This means that we first have to identify which switch we have, and then obtain the images
        if "WC" in deviceInfo['osversion']:
            # It's a 2930 series. Obtain all the images that are available for the 2930 series
            bootInfo['devicefamily']="2930"
            queryStr="select * from deviceimages where devicefamily='2930'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "KB" in deviceInfo['osversion']:
            bootInfo['deviceimage']="3810/5400"
            # It's a 38x0/5400 series. Obtain all the images that are available for the 38x0/5400 series
            queryStr="select * from deviceimages where devicefamily='3810/5400'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        # Another thing to check is whether there is already an active upgrade scheduled. This is identified by the in the softwareupdate table with an existing switchid and a status that is set to 0
        # Status set to 0 means that the upgrade has not started yet and the upgrade can still be edited
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    elif deviceInfo['ostype']=="arubaos-cx":
        url="firmware"
        response = classes.classes.getcxREST(deviceInfo['id'],url)
        if "errormessage" in response:
            # Something went wrong with the rest call. 
            return response
        elif response:
            bootInfo['primaryImage']=response['primary_version']
            bootInfo['secondaryImage']=response['secondary_version']
            bootInfo['defaultImage']=response['default_image'].capitalize()
            if "osversion" in deviceInfo:
                if "FL" in deviceInfo['osversion']:
                    # It's a 6300/6400 series. Obtain all the images that are available for the 6300/6400 series
                    bootInfo['devicefamily']="6300/6400"
                    queryStr="select * from deviceimages where devicefamily='6300/6400'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "ML" in deviceInfo['osversion']:
                    # It's a 6200 series. Obtain all the images that are available for the 6200 series
                    bootInfo['devicefamily']="6200"
                    queryStr="select * from deviceimages where devicefamily='6200'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "PL" in deviceInfo['osversion']:
                    # It's a 6100 series. Obtain all the images that are available for the 6100 series
                    bootInfo['devicefamily']="6100"
                    queryStr="select * from deviceimages where devicefamily='6100'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "TL" in deviceInfo['osversion']:
                    # It's a 8320 series. Obtain all the images that are available for the 8320 series
                    bootInfo['devicefamily']="8320"
                    queryStr="select * from deviceimages where devicefamily='8320'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "GL" in deviceInfo['osversion']:
                    # It's a 8325 series. Obtain all the images that are available for the 8325 series
                    bootInfo['devicefamily']="8325"
                    queryStr="select * from deviceimages where devicefamily='8325'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "LL" in deviceInfo['osversion']:
                    # It's a 8360 series. Obtain all the images that are available for the 8360 series
                    bootInfo['devicefamily']="8360"
                    queryStr="select * from deviceimages where devicefamily='8360'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                elif "DL" in deviceInfo['osversion']:
                    # It's a 10000 series. Obtain all the images that are available for the 10000 series
                    bootInfo['devicefamily']="10000"
                    queryStr="select * from deviceimages where devicefamily='10000'"
                    imageResult=classes.classes.sqlQuery(queryStr,"select")
                else:
                    imageResult=[]
            else:
                imageResult=[]
        else:
            imageResult=[]
            bootInfo['primaryImage']=""
            bootInfo['secondaryImage']=""
            bootInfo['defaultImage']=""
        bootInfo['images']=imageResult
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    # Update the devices database so that the osversion matches the version running on the switch
    if bootInfo['defaultImage'] !="":
        if bootInfo['defaultImage']=="Primary":
            queryStr="update devices set osversion='{}' where id='{}'".format(bootInfo['primaryImage'],deviceInfo['id'])
        elif bootInfo['defaultImage']=="Secondary":
            queryStr="update devices set osversion='{}' where id='{}'".format(bootInfo['secondaryImage'],deviceInfo['id'])
        classes.classes.sqlQuery(queryStr,"update")
    return bootInfo


def getofflineupgradeInfo(deviceInfo):
    bootInfo={}
    if deviceInfo['ostype']=="arubaos-switch":
        if "WC" in deviceInfo['osversion']:
            # It's a 2930 series. Obtain all the images that are available for the 2930 series
            bootInfo['devicefamily']="2930"
            queryStr="select * from deviceimages where devicefamily='2930'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "KB" in deviceInfo['osversion']:
            # It's a 38x0/5400 series. Obtain all the images that are available for the 38x0/5400 series
            bootInfo['devicefamily']="3810/5400"
            queryStr="select * from deviceimages where devicefamily='3810/5400'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        # Another thing to check is whether there is already an active upgrade scheduled. This is identified by the in the softwareupdate table with an existing switchid and a status that is set to 0
        # Status set to 0 means that the upgrade has not started yet and the upgrade can still be edited
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    elif deviceInfo['ostype']=="arubaos-cx":
        if "osversion" in deviceInfo:
            if "FL" in deviceInfo['osversion']:
                # It's a 6300/6400 series. Obtain all the images that are available for the 6300/6400 series
                bootInfo['devicefamily']="6300/6400"
                queryStr="select * from deviceimages where devicefamily='6300/6400'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "ML" in deviceInfo['osversion']:
                # It's a 6200 series. Obtain all the images that are available for the 6200 series
                bootInfo['devicefamily']="6200"
                queryStr="select * from deviceimages where devicefamily='6200'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "PL" in deviceInfo['osversion']:
                # It's a 6100 series. Obtain all the images that are available for the 6100 series
                bootInfo['devicefamily']="6100"
                queryStr="select * from deviceimages where devicefamily='6100'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "TL" in deviceInfo['osversion']:
                # It's a 8320 series. Obtain all the images that are available for the 8320 series
                bootInfo['devicefamily']="8320"
                queryStr="select * from deviceimages where devicefamily='8320'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "GL" in deviceInfo['osversion']:
                # It's a 8325 series. Obtain all the images that are available for the 8325 series
                bootInfo['devicefamily']="8325"
                queryStr="select * from deviceimages where devicefamily='8325'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "LL" in deviceInfo['osversion']:
                # It's a 8360 series. Obtain all the images that are available for the 8360 series
                bootInfo['devicefamily']="8360"
                queryStr="select * from deviceimages where devicefamily='8360'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            elif "DL" in deviceInfo['osversion']:
                # It's a 10000 series. Obtain all the images that are available for the 10000 series
                bootInfo['devicefamily']="10000"
                queryStr="select * from deviceimages where devicefamily='10000'"
                imageResult=classes.classes.sqlQuery(queryStr,"select")
            else:
                imageResult=[]
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    return bootInfo


def bootSwitch(ostype, upgradeid, deviceid, activepartition):
    response={}
    try:
        if ostype=="arubaos-cx":
            # We need to reboot the switch with the proper boot partition
            url="boot?image=" + activepartition
            print(url)
            response=classes.classes.postcxREST(deviceid,url,"")
            print("Reboot switch")
            print(response)
            queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeid)
            classes.classes.sqlQuery(queryStr,"update")
        elif ostype=="arubaos-switch":
            url="system/reboot"
            parameters={ "boot_image":activepartition}
            response=classes.classes.postswitchREST(deviceid,url,parameters)
            queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeid)
            classes.classes.sqlQuery(queryStr,"update")
    except Exception as e:
        print(e)
    return response


def upgradeprofilesearchDevices(searchOptions):
    # A couple of stages here. First check which searchtype (ipaddress, description or attribute)
    if searchOptions['searchType']=="ipaddress":
        # Need to search the devices table with the ip address search criteria
        queryStr="select id, ipaddress, description, ostype from devices where ipaddress like '%{}%' and (ostype='arubaos-cx' or ostype='arubaos-switch')".format(searchOptions['ipaddress'])
        result=classes.classes.sqlQuery(queryStr, "select")
    elif searchOptions['searchType']=="description":
        # Need to search the devices table with the description search criteria
        queryStr="select id, ipaddress, description, ostype from devices where description like '%{}%' and (ostype='arubaos-cx' or ostype='arubaos-switch')".format(searchOptions['description'])
        result=classes.classes.sqlQuery(queryStr, "select") 
    elif searchOptions['searchType']=="attribute":
        result=[]
        # Need to search the devices table with the attribute search criteria. This is a more complex query.
        # First we need to get the list of switches that are assigned to the attribute (isassigned information in the table)
        if searchOptions['attribute']:
            queryStr="select isassigned from deviceattributes where id='{}'".format(searchOptions['attribute'])
            assignedResult=classes.classes.sqlQuery(queryStr, "selectone") 
            # We need to convert the result (this is a list in string format) into an sql query readable format. First, convert to list
            assignedResult = json.loads(assignedResult['isassigned'])
            assignedResult = ','.join(assignedResult)
            # Now query the devices list that have this attribute assigned
            try:
                queryStr="select id, ipaddress, description, ostype, deviceattributes from devices where id in ({})".format(assignedResult)
                deviceResult = classes.classes.sqlQuery(queryStr, "select")
                # Now, we need to go through the items and check whether the attribute that we are looking for is there
                for items in deviceResult:
                    deviceAttributes=json.loads(items['deviceattributes'])
                    # Remove the device attributes, they are not needed in the result
                    del items['deviceattributes']
                    for items2 in deviceAttributes:
                        # Now go through the device attributes and check whether the value is in there. We can search on the device attribute id first
                        if searchOptions['attribute']==str(items2['id']):
                            # The attribute id matches, we need to check this item
                            if searchOptions['attributeType']=="value":
                                if searchOptions['attributevalueValue'].lower() in items2['value'].lower():
                                    # We have a match, append the switch information
                                    result.append(items.copy())
                            elif searchOptions['attributeType']=="boolean":
                                if searchOptions['attributebooleanValue']==items2['value']:
                                    # We have a match, append the switch information
                                    result.append(items.copy())
                            elif searchOptions['attributeType']=="list":
                                if searchOptions['attributelistValue']==items2['value']:
                                    # We have a match, append the switch information
                                    result.append(items.copy())
            except:
                # Exception typically happens when no devices were found
                result=[]
        else:
            result=[]
    return json.dumps(result)


def getsoftwareimageList(devicelist):
    swInfo=[]
    response={}
    onlineDevices=[]
    offlineDevices=[]
    # The device list contains different switch models (CX, AOS-Switch, etc). We need to make a distinction and return the software images that are stored in the repository for the devices that are in this list
    for items in devicelist['devicelist[]']:
        queryStr="select id, ipaddress, ostype, osversion from devices where id='{}'".format(items)
        deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
        # We should only check for software information if the device is online. If the device is offline, we will mark it in the return information
        isOnline=classes.classes.checkifOnline(deviceInfo['id'],deviceInfo['ostype'])
        if isOnline=="Online":
            bootInfo=getupgradeInfo(deviceInfo)
            swInfo.append(bootInfo['images'].copy())
            onlineDevices.append(deviceInfo['id'])
        else:
            # The device is offline. Let's obtain the information from the database instead of the latest information that comes from the switch
            bootInfo=getofflineupgradeInfo(deviceInfo)
            swInfo.append(bootInfo['images'].copy())
            offlineDevices.append(deviceInfo['id'])
    swInfo = [i for n, i in enumerate(swInfo) if i not in swInfo[n + 1:]]
    swInfo = [x for x in swInfo if x]
    response['swInfo']=swInfo
    response['onlineDevices']=onlineDevices
    response['offlineDevices']=offlineDevices
    return response


def getupgradeprofileName(profileid):
    queryStr="select name from upgradeprofiles where id='{}'".format(profileid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    return result['name']


def getupgradeprofileInfo(profileid):
    queryStr="select * from upgradeprofiles where id='{}'".format(profileid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    return result


def getupgradeprofileDevices(profileid):
    queryStr="select devicelist from upgradeprofiles where id='{}'".format(profileid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    return result['devicelist']


def getupgradeprofiledeviceInfo(profileid):
    queryStr="select * from softwareupdate where upgradeprofile='{}'".format(profileid)
    result=classes.classes.sqlQuery(queryStr,"select")
    return result


def getupgradeprofileStatus(profileid):
    switchList=[]
    upgradestatus = {0: 'Not started', 1: 'Upgrade initiated', 5: 'Copy software onto the switch', 10: 'Software copied successfully', 20: 'Software copied successfully: switch is rebooted', 50: 'There is another software upgrade in progress', 100: 'Software upgrade completed successfully', 110: 'Software upgrade completed successfully: reboot is required' }
    # Obtain the obtain information
    queryStr="select * from softwareupdate where upgradeprofile={}".format(profileid)
    upgradeInfo=classes.classes.sqlQuery(queryStr,"select")
    for items in upgradeInfo:
        switchList.append(items['switchid'])
    switchList=tuple(switchList)
    switchIds=str(switchList)
    if len(switchList)==1:
        # There is only one element in the list, we need to remove the single comma
        switchIds=switchIds.replace(",","")
    # Now obtain the switch information
    try:
        queryStr="select id,ipaddress, description, ostype, platform, osversion from devices where id in {} ".format(switchIds)
        deviceInfo=classes.classes.sqlQuery(queryStr,"select")
        # Now iterate through the software update items and add the switch information, status information and optionally (if the upgrade has been completed) the upgrade time
        for items in upgradeInfo:
            items['status']=upgradestatus[items['status']]
            if items['endtime']:
                # Calculate the upgrade duration
                upgradeDuration=items['endtime']-items['starttime']
                days = upgradeDuration.days
                hours, remainder = divmod(upgradeDuration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                items['duration']=str(days) + " days, " + str(hours) + " hour(s), " + str(minutes) + " minute(s), " + str(seconds) + " second(s)"
            else:
                items['duration']=""
            for items2 in deviceInfo:
                if items2['id']==items['switchid']:
                    # Found the switch information, add this to the upgradeInfo
                    items['ipaddress']=items2['ipaddress']
                    items['description']=items2['description']
                    items['ostype']=items2['ostype']
                    items['platform']=items2['platform']
                    items['osversion']=items2['osversion']
    except:
        return {}
    return upgradeInfo