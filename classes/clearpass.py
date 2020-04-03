# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic ClearPass classes
import classes.classes
import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def clearpassdbAction(formresult):
    # This definition is for all the database actions for ClearPass, based on the user click on the pages
    globalsconf=classes.classes.globalvars()
    if(bool(formresult)==True):
        if(formresult['action']=="Submit device"):
            queryStr="insert into devices (description,ipaddress,username,password,secinfo, ostype) values ('{}','{}','{}','{}','{}','{}')"\
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),formresult['usersecret'],"ClearPass")
            deviceid=classes.classes.sqlQuery(queryStr,"insert")
            # Obtain the ClearPass server information
            osresult=getRESTcp(deviceid,"server/version")
            platformresult=getRESTcp(deviceid,"cppm-version")
            # If there is a result, then obtaining the token was successful, otherwise we should 
            if type(platformresult) is dict:
                #Get this information stored in the database
                queryStr="update devices set osversion='{}', platform='{}' where id='{}' ".format(osresult['cppm_version'],platformresult['hardware_version'],deviceid)
                classes.classes.sqlQuery(queryStr,"update")
            else:
                queryStr="update devices set osversion='Not reachable', platform='Not reachable' where id='{}' ".format(deviceid)
                classes.classes.sqlQuery(queryStr,"update")
            # Build the list
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, secinfo, platform, osversion from devices where ostype='ClearPass'","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}',secinfo='{}' where id='{}' "\
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']), formresult['usersecret'],formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
            # Obtain the ClearPass server information
            osresult=getRESTcp(formresult['id'],"server/version")
            platformresult=getRESTcp(formresult['id'],"cppm-version")
            # If there is a result, then obtaining the token was successful, otherwise we should 
            if type(platformresult) is dict:
                #Get this information stored in the database
                queryStr="update devices set osversion='{}', platform='{}' where id='{}' ".format(osresult['cppm_version'],platformresult['hardware_version'],formresult['id'])
                classes.classes.sqlQuery(queryStr,"update")
            else:
                queryStr="update devices set osversion='Not reachable', platform='Not reachable' where id='{}' ".format(formresult['id'])
                classes.classes.sqlQuery(queryStr,"update")
            #Build the list
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, secinfo, platform, osversion from devices where ostype='ClearPass'","select")
        elif (formresult['action']=="Delete"):
            queryStr="delete from devices where id='{}'".format(formresult['id'])
            classes.classes.sqlQuery(queryStr,"delete")
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, secinfo, platform, osversion from devices where ostype='ClearPass'","select")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchIpaddress'] or formresult['searchDescription'] or formresult['searchOsversion'] or formresult['searchPlatform']:
            constructQuery= " where (ostype='ClearPass') AND "
        else:
            constructQuery="where (ostype='ClearPass')      "
        if formresult['searchDescription']:
            constructQuery += " description like'%" + formresult['searchDescription'] + "%' AND "
        if formresult['searchOsversion']:
            constructQuery += " osversion like '%" + formresult['searchOsversion'] + "%' AND "
        if formresult['searchIpaddress']:
            constructQuery += " ipaddress like'%" + formresult['searchIpaddress'] + "%' AND "
        if formresult['searchPlatform']:
            constructQuery += " platform like'%" + formresult['searchPlatform'] + "%' AND "


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
        queryStr = "select * from devices " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")         
    else:
        # Initial page access. Obtain information from the devices database
        pageoffset=0
        entryperpage=10
        queryStr="select COUNT(*) as totalentries from devices  where ostype='ClearPass'"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, secinfo, platform, osversion from devices where ostype='ClearPass'","select")
    queryStr="select distinct platform from devices where ostype='ClearPass'"
    platformResult=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select distinct osversion from devices where ostype='ClearPass'"
    osversionResult=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'platformResult': platformResult,'osversionResult': osversionResult, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def getRESTcp (deviceid,geturl):
    # Renew the ClearPass tokens
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password, secinfo from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}:443/api/".format(deviceCreds['ipaddress'])
    url="oauth"
    credentials={"grant_type": "password","client_id": deviceCreds['username'], "client_secret": deviceCreds['secinfo'],"username": deviceCreds['username'],"password": classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password'])}
    header={'Content-Type':'application/json'}
    try:
        # Obtain the new token.
        response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials),headers=header, timeout=2)
        # if the status code equals 200, then the call was successful, so we can use the token in the header.
        if response.status_code==200:
            # Now, obtain the information from ClearPass
            authtoken="Bearer " + response.json()['access_token']
            header={'Content-Type':'application/json','Authorization': authtoken }
            response = requests.get(baseurl+geturl, verify=False, data=json.dumps(credentials),headers=header, timeout=2)
            return response.json()
        else:
            return 401
    except:
        print("Error Renewing the ClearPass token")
        return 401


def checkcpOnline(deviceid):
    # Login and logout of the device to see if the device is online
    result=getRESTcp(deviceid,"cppm-version")
    if result==401:
        return "Offline"
    else:
        return "Online"