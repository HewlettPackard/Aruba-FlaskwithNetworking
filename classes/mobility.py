# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic Aruba Mobility Controller classes

import classes.classes
import requests

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def mobilitydbAction(formresult):
    # This definition is for all the database actions for Mobility Controllers, based on the user click on the pages
    globalsconf=classes.classes.globalvars()
    header={}
    if(bool(formresult)==True):
        if(formresult['action']=="Submit device"):
            queryStr="insert into devices (description,ipaddress,username,password,ostype) values ('{}','{}','{}','{}','{}')"\
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),'Mobility Controller')
            deviceid=classes.classes.sqlQuery(queryStr,"insert")
            # Update the database with the platform information
            try:
                cookie=loginmc(deviceid)
                mcresult=getMCinfo(cookie,deviceid) 
                logoutmc(cookie,deviceid)
                if type(mcresult) is dict:
                    queryStr="update devices set platform='{}',osversion='{}',sysinfo='{}' where id='{}' ".format(mcresult['_global']['_model'],mcresult['_global']['_version']['_image_version'],json.dumps(mcresult),deviceid)
                else:
                    mcresult={"_global": {"_version": {"_image_version": "", "_supported_image_version": []}, "_switch_role": "", "_master_type": "", "_hostname": "", "_model": ""}}
                    queryStr="update devices set platform='{}',osversion='{}', sysinfo='{}' where id='{}' ".format("Not reachable","Not reachable",json.dumps(mcresult),deviceid)
                classes.classes.sqlQuery(queryStr,"update")
            except:
                mcresult={"_global": {"_version": {"_image_version": "", "_supported_image_version": []}, "_switch_role": "", "_master_type": "", "_hostname": "", "_model": ""}}
                queryStr="update devices set platform='{}',osversion='{}', sysinfo='{}' where id='{}' ".format("Not reachable","Not reachable",json.dumps(mcresult),deviceid)
                classes.classes.sqlQuery(queryStr,"update")
            # Build the list
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, platform, osversion,sysinfo from devices where ostype='Mobility Controller'","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}' where id='{}' " \
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'],formresult['password']),formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"update")
            try:
                cookie=loginmc(formresult['deviceid'])
                mcresult=getMCinfo(cookie,formresult['deviceid']) 
                logoutmc(cookie,formresult['deviceid'])
                if type(mcresult) is dict:
                    queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}', platform='{}', osversion='{}',sysinfo='{}' where id='{}' " \
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!",formresult['password']), \
                    mcresult['_global']['_model'],mcresult['_global']['_version']['_image_version'],json.dumps(mcresult),formresult['deviceid'])
                else:
                    mcresult={"_global": {"_version": {"_image_version": "", "_supported_image_version": []}, "_switch_role": "", "_master_type": "", "_hostname": "", "_model": ""}}
                    queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}', platform='{}', osversion='{}', sysinfo='{}' where id='{}' " \
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!",formresult['password']), \
            "Not reachable","Not reachable",json.dumps(mcresult),formresult['deviceid'])
                classes.classes.sqlQuery(queryStr,"update")
            except:
                mcresult={"_global": {"_version": {"_image_version": "", "_supported_image_version": []}, "_switch_role": "", "_master_type": "", "_hostname": "", "_model": ""}}
                queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}', platform='{}', osversion='{}', sysinfo='{}' where id='{}' " \
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword("ArubaRocks!!!!!!",formresult['password']), \
            "Not reachable","Not reachable",json.dumps(mcresult),formresult['deviceid'])
                classes.classes.sqlQuery(queryStr,"update")
            # Build the list
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, platform, osversion,sysinfo from devices where ostype='Mobility Controller'","select")
        elif (formresult['action']=="Delete"):
            queryStr="delete from devices where id='{}'".format(formresult['id'])
            classes.classes.sqlQuery(queryStr,"delete")
            result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, platform, osversion,sysinfo from devices where ostype='Mobility Controller'","select")
        
        # Now get the information from the database and return the info to the calling definition    

        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchIpaddress'] or formresult['searchDescription'] or formresult['searchOsversion'] or formresult['searchPlatform']:
            constructQuery= " where (ostype='Mobility Controller') AND "
        else:
            constructQuery="where (ostype='Mobility Controller')      "
        if formresult['searchDescription']:
            constructQuery += " description like'%" + formresult['searchDescription'] + "%' AND "
        if formresult['searchOsversion']:
            constructQuery += " osversion like '%" + formresult['searchOsversion'] + "%' AND "
        if formresult['searchIpaddress']:
            constructQuery += " ipaddress like'%" + formresult['searchIpaddress'] + "%' AND "
        if formresult['searchPlatform']:
            constructQuery += " platform like'%" + formresult['searchPlatform'] + "%' AND "
        

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
        queryStr = "select * from devices " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
            
    else:
        # Initial page access. Obtain information from the devices database
        pageoffset=0
        entryperpage=10
        queryStr="select COUNT(*) as totalentries from devices  where ostype='Mobility Controller'"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        result=classes.classes.sqlQuery("select id, description, ipaddress, username, password, platform, osversion,sysinfo from devices where ostype='Mobility Controller'","select")

    # Obtain distinct mobility software version information
    queryStr="select distinct platform from devices where ostype='Mobility Controller'"
    platformResult=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select distinct osversion from devices where ostype='Mobility Controller'"
    osversionResult=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'platformResult': platformResult,'osversionResult': osversionResult,  'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def loginmc (deviceid):
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="https://{}:4343/v1/api/login".format(deviceCreds['ipaddress'])
    credentials = "username=" + deviceCreds['username'] + "&password=" + classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password'])
    try:
        # Login to the mobility controller. The cookie value is returned to the calling definition. It is not stored in the cookie jar.
        response = requests.post(url, verify=False, data=credentials, timeout=5)
        cookie=response.json()['_global_result']['UIDARUBA']
        return cookie
    except:
        print("Error logging into Mobility Controller")
        return 401

def logoutmc(cookie,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="https://{}:4343/v1/api/logout".format(deviceCreds['ipaddress'])
    try:
        response = requests.post(url,timeout=5, verify=False)
    except:
        print("Error logging out of Mobility Controller")

def getRESTmc(cookie,url,deviceid):
    # Obtain device information from the database
    queryStr="select ipaddress, username, password, platform from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    aoscookie = dict(SESSION = cookie)
    fullurl="https://{}:4343/v1/{}{}".format(deviceCreds['ipaddress'],url,cookie)
    try:
       # If the response contains information, the content is converted to json format
       response=requests.get(fullurl, verify=False, cookies=aoscookie, timeout=5)
       return (response.json())
    except:
       response="No data"
    return response

def getMCinfo(cookie,deviceid):
    #Obtain the mobility controller information. Is it a standalone, a MD, or an MM. If it is an MD, what is its MM
    mcresult=getRESTmc(cookie,"configuration/object/sys_info?UIDARUBA=",deviceid) 
    mcrole=getRESTmc(cookie,"configuration/showcommand?command=show+roleinfo&UIDARUBA=",deviceid)
    if mcrole['_data'][0]=="MD":
        mcresult['mm']=mcrole['_data'][1]
    elif mcrole['_data'][0]=="master":
        # This is a master. Need to get the md's from the Master
        mcresult['mm']=mcrole['_data'][0]
        mcresult['cluster']=getRESTmc(cookie,"configuration/object/cluster_prof?config_path=%2Fmd&UIDARUBA=",deviceid)
    else:
        mcresult['mm']=""
    return mcresult


def mcinterfaceInfo(deviceid):
    response=[]
    try:
        cookie=loginmc(deviceid)
        # Obtain the VLAN interface information. If it is a standalone controller, we should not include the config path. Only required for Mobility Master
        mcrole=getRESTmc(cookie,"configuration/showcommand?command=show+roleinfo&UIDARUBA=",deviceid)
        if mcrole['_data'][0]=="master":
            url="configuration/object/int_vlan?config_path=%2Fmd&UIDARUBA=" + cookie
        else:
            url="configuration/object/int_vlan?UIDARUBA=" + cookie
        result=getRESTmc(cookie,url,deviceid)

        response.append(result['_data'])
        # Obtain the VLAN name information
        if mcrole['_data'][0]=="master":
            url="configuration/object/vlan_name_id?config_path=%2Fmd&UIDARUBA=" + cookie
        else:
            url="configuration/object/vlan_name_id?UIDARUBA=" + cookie
        result=getRESTmc(cookie,url,deviceid)
        response.append(result['_data'])
        # Obtain the DHCP pool information
        if mcrole['_data'][0]=="master":
            url="configuration/object/ip_dhcp_pool_cfg?config_path=%2Fmd&UIDARUBA=" + cookie
        else:
            url="configuration/object/ip_dhcp_pool_cfg?UIDARUBA=" + cookie
        result=getRESTmc(cookie,url,deviceid)
        response.append(result['_data'])
    except:
        pass
    logoutmc(cookie,deviceid)
    return json.dumps(response)

def mcroleInfo(deviceid):
    cookie=loginmc(deviceid)
    mcrole=getRESTmc(cookie,"configuration/showcommand?command=show+roleinfo&UIDARUBA=",deviceid)
    # We have to get all the ACL information from the controllers.
    if mcrole['_data'][0]=="master":
        url="configuration/object/role?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/role?UIDARUBA=" + cookie
    response=getRESTmc(cookie,url,deviceid)
    logoutmc(cookie,deviceid)
    return json.dumps(response['_data']['role'])

def mcpolicyInfo(deviceid):
    response=[]
    cookie=loginmc(deviceid)
    mcrole=getRESTmc(cookie,"configuration/showcommand?command=show+roleinfo&UIDARUBA=",deviceid)
    # We have to get all the ACL information from the controllers.
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_sess?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_sess?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_mac?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_mac?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_std?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_std?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_ext?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_ext?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_qinq?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_qinq?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    if mcrole['_data'][0]=="master":
        url="configuration/object/acl_route?config_path=%2Fmd&UIDARUBA=" + cookie
    else:
        url="configuration/object/acl_route?UIDARUBA=" + cookie
    result=getRESTmc(cookie,url,deviceid)
    response.append(result['_data'])
    logoutmc(cookie,deviceid)
    return json.dumps(response)

def checkmcOnline(deviceid):
    # Login and logout of the device to see if the device is online
    try:
        cookie=loginmc(deviceid)
        logoutmc(cookie,deviceid)
        if cookie==401:
            return "Offline"
        else:
            return "Online"
    except:
        return "Offline"
