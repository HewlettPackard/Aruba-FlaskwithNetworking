# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic Telemetry classes

import classes.classes
import requests, json
import psutil, sys, os, platform, subprocess
sessionid = requests.Session()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

   
def telemetrydbAction(formresult):
    # This definition is for all the database actions for telemetry
    searchAction="None"
    entryExists=0
    if(bool(formresult)==True): 
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit subscription"):
            print("Submitting a subscription")
        elif  (formresult['action']=="Change subscription"):
            print("Changing a subscription")
        elif (formresult['action']=="Delete subscription"):
            print("Delete a subscription")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchIPaddress'] or formresult['searchDescription'] or formresult['searchVersion']:
            constructQuery= " where ostype='arubaos-cx' AND "
        else:
            constructQuery="where ostype='arubaos-cx'    "
        if formresult['searchDescription']:
            constructQuery += " description like'%" + formresult['searchDescription'] + "%' AND "
        if formresult['searchVersion']:
            constructQuery += " osversion like '%" + formresult['searchVersion'] + "%' AND "
        if formresult['searchIPaddress']:
            constructQuery += " ipaddress like'%" + formresult['searchIPaddress'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from devices " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select id, description, ipaddress, platform, osversion, subscriber, subscriptions from devices " + constructQuery[:-4] + " and telemetryenable=1 LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from devices where ostype='arubaos-cx' and telemetryenable=1"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=10
        pageoffset=0
        queryStr="select id, description, ipaddress, osversion, subscriber, subscriptions from devices where ostype='arubaos-cx' and telemetryenable=1 LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def subscriptionAction(action,id, subscriber, resource, addSubscription, confirmDelete):
    resourceExists=0
    queryStr="select ipaddress, description, secinfo, switchstatus, subscriptions, subscriber from devices where id='{}'".format(id)
    deviceinfo=classes.classes.sqlQuery(queryStr,"selectone")
    subscriptions=json.loads(deviceinfo['subscriptions'])
    if action=="Unsubscribe":
        for items in subscriptions[0]:
            if items['resource']==resource:
                items['status']="0"
        subscriptions="[" + json.dumps(subscriptions[0])+",1]"
        queryStr="update devices set subscriptions='{}' where id='{}'".format(subscriptions,id)
        classes.classes.sqlQuery(queryStr,"update")
    elif action=="Subscribe":
        for items in subscriptions[0]:
            if items['resource']==resource:
                items['status']="1"
        subscriptions="[" + json.dumps(subscriptions[0])+",1]"
        queryStr="update devices set subscriptions='{}' where id='{}'".format(subscriptions,id)
        classes.classes.sqlQuery(queryStr,"update")
    elif action=="Add subscription":
        # There should not be any bogus information in the addSubscription variable. Check whether /rest/ exists in the variable. At least this is some check
        if "/rest/" in addSubscription:
            for items in subscriptions[0]:
                # First check if subscription already exists
                if items['resource']==addSubscription:
                    resourceExists=1
            if resourceExists==0:
                subscriptions[0].append({'resource':addSubscription,'status':'0','message':''})
                subscriptions="["+json.dumps(subscriptions[0])+",0]"
                queryStr="update devices set subscriptions='{}' where id='{}'".format(subscriptions,id)
                classes.classes.sqlQuery(queryStr,"update")
    elif action=="Delete" and confirmDelete=="1":
        for i in range(len(subscriptions[0])): 
            if subscriptions[0][i]['resource']==resource:
                del subscriptions[0][i]
                break
        subscriptions="["+json.dumps(subscriptions[0])+",0]"
        queryStr="update devices set subscriptions='{}' where id='{}'".format(subscriptions,id)
        classes.classes.sqlQuery(queryStr,"update")
    queryStr="select id, ipaddress, description, secinfo, switchstatus, subscriptions, subscriber from devices where id='{}'".format(id)
    return classes.classes.sqlQuery(queryStr,"selectone")

def checkRunningws(deviceid):
    for proc in psutil.process_iter():
        # Need to check whether the listener process or the scheduler process is queried
            if "python" in proc.name().lower():
                procinfo=psutil.Process(proc.pid)
                if len(procinfo.cmdline())>1:
                    if procinfo.cmdline()[1]=="/var/www/html/bash/wsclient.py":
                        # If there is a wsclient process, the device id is also attached
                        if procinfo.cmdline()[2]==str(deviceid):
                            return "Online"
    return "Offline"

def checkSubscriptions(deviceid):
    activedbsubs=[]
    totaldbsubs=[]
    queryStr="select ipaddress, description, secinfo, switchstatus, subscriptions, subscriber from devices where id='{}'".format(deviceid)
    deviceinfo=classes.classes.sqlQuery(queryStr,"selectone")
    dbsubscriptions=json.loads(deviceinfo['subscriptions'])
    if len(dbsubscriptions[0])>0:
        for items in dbsubscriptions[0]:
            if items['status']=="1":
                # This is an active subscription in the database, append it to the dbsubs list
                activedbsubs.append(items['resource'])
            totaldbsubs.append(items['resource'])
    # First check if the cookie is still ok
    isOnline=classes.classes.checkcxCookie(deviceid)
    if isOnline==100:
        response={"devicestatus":"Offline","swsubs":0,"activedbsubs":len(activedbsubs),"totaldbsubs":len(totaldbsubs),"subscriber":"Not active"}
        return json.dumps(response)
    else:
        swsubs=[]
        # Check whether the subscriptions on the switch are in sync with the subscriptions in the database   
        uri="https://{}/rest/v1/system/notification_subscribers?depth=2&filter=name%3A{}".format(deviceinfo['ipaddress'],deviceinfo['subscriber'])
        response=requests.get(uri,headers=json.loads(deviceinfo['secinfo']),verify=False,timeout=10)
        if response.status_code==200:
            swsubscriptions=json.loads(response.text)
        else:
            swsubscriptions=[]
        # Goal is to create two lists, one from the database (only the subscribed ones), and one from the switch, and then compare whether they are identical. 
        # If they are, then we are good and can return with the relevant information
        if len(swsubscriptions)>0:
            # There are active subscriptions
            for items in swsubscriptions[0]['notification_subscriptions']:
                swsubs.append(swsubscriptions[0]['notification_subscriptions'][items]['resource'][0])
        # Construct the response
        response={"devicestatus":"Online","swsubs":len(swsubs),"activedbsubs":len(activedbsubs),"totaldbsubs":len(totaldbsubs),"subscriber":deviceinfo['subscriber']}
        return json.dumps(response)