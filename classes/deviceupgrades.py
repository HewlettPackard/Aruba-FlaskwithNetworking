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
        if (formresult['searchupgradeFrom'] or formresult['searchupgradeTo'] or formresult['searchPartition']) and (formresult['searchName'] or formresult['searchIpaddress']):
            constructQuery=" and "
        elif formresult['searchupgradeFrom'] or formresult['searchupgradeTo'] or formresult['searchPartition']:
            constructQuery=" where "
        if formresult['searchupgradeFrom']:
            constructQuery += " upgradefrom like '%" + formresult['searchupgradeFrom'] + "%' AND "
        if formresult['searchupgradeTo']:
            constructQuery += " upgradeto like '%" + formresult['searchupgradeTo'] + "%' AND "
        if formresult['searchPartition']:
            constructQuery += " activepartition like '%" + formresult['searchPartition'] + "%' AND "
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


def scheduledbAction(formresult):
    message=""
    # Obtain the device information
    if formresult['action']=="submitUpgrade":
        print("Submit upgrade")
        # If there is already an upgrade entry (status set to 0 which means not active), then we should not add the upgrade
        # If the upgrade status is >0 then the upgrade is in progress and we should be able to add a new upgrade, however, this upgrade should not be executed. This is handled in the upgrade scheduler
        queryStr="select * from softwareupdate where switchid='{}' and status=0".format(formresult['switchid'])
        print(queryStr)
        checkResult=classes.classes.sqlQuery(queryStr,"select")
        if checkResult:
            message="There is already an upgrade entry"
        else:
            if formresult['schedule']!="":
                # If the schedule time is smaller than the actual time, then the scheduled time has been set in the past and the upgrade is considered to be run immediately
                if datetime.fromisoformat(formresult['schedule'].replace(',',''))<datetime.now():
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,status) values ('{}','{}','{}','{}','{}','{}','','','','','',1)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['schedule'],formresult['reboot'])
                else:
                    queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,schedule,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,status) values ('{}','{}','{}','{}','{}','{}','','','','','',0)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['schedule'],formresult['reboot'])
            else:
                queryStr="insert into softwareupdate (switchid,software,imagepartition,activepartition,reboot,policy,upgradefrom, upgradeto,softwareinfo,softwareinfoafter,status) values ('{}','{}','{}','{}','{}','','','','','',1)".format(formresult['switchid'],formresult['software'],formresult['imagepartition'],formresult['activepartition'],formresult['reboot'])
            print(queryStr)
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
            queryStr="select * from deviceimages where devicefamily='2930'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "KB" in deviceInfo['osversion']:
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
        bootInfo['primaryImage']=response['primary_version']
        bootInfo['secondaryImage']=response['secondary_version']
        bootInfo['defaultImage']=response['default_image']
        if "FL" in deviceInfo['osversion']:
            # It's a 6300/6400 series. Obtain all the images that are available for the 6300/6400 series
            queryStr="select * from deviceimages where devicefamily='6300/6400'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "TL" in deviceInfo['osversion']:
            # It's a 8320 series. Obtain all the images that are available for the 8320 series
            queryStr="select * from deviceimages where devicefamily='8320'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "GL" in deviceInfo['osversion']:
            # It's a 8325 series. Obtain all the images that are available for the 8325 series
            queryStr="select * from deviceimages where devicefamily='8325'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    return bootInfo


def bootSwitch(ostype, upgradeid, deviceid, activepartition):
    response={}
    if ostype=="arubaos-cx":
        # We need to reboot the switch with the proper boot partition
        url="boot?image=" + activepartition
        response=classes.classes.postcxREST(deviceid,url,"")
        queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeid)
        classes.classes.sqlQuery(queryStr,"update")
    elif ostype=="arubaos-switch":
        url="system/reboot"
        parameters={ "boot_image":activepartition}
        response=classes.classes.postswitchREST(deviceid,url,parameters)
        queryStr="update softwareupdate set status=20 where id='{}'".format(upgradeid)
        classes.classes.sqlQuery(queryStr,"update")
    return response