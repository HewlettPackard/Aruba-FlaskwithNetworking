# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic ClearPass classes
import classes.classes
import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def str_to_bool(s):
        if s == 'True':
            return True
        elif s == 'False':
            return False

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
    if deviceCreds:
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
            print("Cannot obtain information from ClearPass")
            return 401
    else:
        return 401


def checkcpOnline(deviceid):
    # Login and logout of the device to see if the device is online
    result=getRESTcp(deviceid,"cppm-version")
    if result==401:
        return "Offline"
    else:
        return "Online"

def getendpointInfo(deviceid,epEntryperpage,epPageoffset, searchMacaddress, searchDescription, searchStatus):
    if not epEntryperpage:
        epEntryperpage=25
    if not epPageoffset:
        pageOffset=0
    else:
        pageOffset=int(epPageoffset)*int(epEntryperpage)
    queryStr="select id, ipaddress, description from devices where id='{}'".format(deviceid)
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Check out whether there are any filters
    if searchMacaddress or searchDescription or searchStatus:
        searchFilter="{\"$and\":["
        if searchMacaddress:
            searchFilter+="{\"mac_address\":{\"$contains\":\"" + searchMacaddress + "\"}},"
        if searchDescription:
            searchFilter+="{\"description\":{\"$contains\":\"" + searchDescription + "\"}},"
        if searchStatus:
            searchFilter+="{\"status\":{\"$eq\":\"" + searchStatus + "\"}},"
        searchFilter=searchFilter[:-1]
        searchFilter+="]}"
    else:
        searchFilter="{}"
    # Obtain the ClearPass endpoint information from ClearPass
    url="endpoint?filter=" + searchFilter + "&sort=%2Bid&offset=" + str(pageOffset) + "&limit=" + str(epEntryperpage) + "&calculate_count=true"
    endpointInfo=classes.classes.getRESTcp(deviceid,url)
    if endpointInfo==401:
        # Something went wrong with the query. Obtain the information without search criteria
        url="endpoint?sort=%2Bid&offset=" + str(pageOffset) + "&limit=" + str(epEntryperpage) + "&calculate_count=true"
        endpointInfo=classes.classes.getRESTcp(deviceid,url)
        return {'endpointInfo': endpointInfo,'deviceInfo': deviceInfo, 'epTotalentries': endpointInfo['count'], 'epEntryperpage': epEntryperpage, 'epPageoffset': 0 , 'searchMacaddress': searchMacaddress, 'searchDescription': searchDescription, 'searchStatus': searchStatus }
    elif len(endpointInfo)==0:
        # It might also be that the pageOffset is too far off finding information, if that is the case, set the pageOffset to 0 and query again
        url="endpoint?filter=" + searchFilter + "&sort=%2Bid&offset=0&limit=" + str(epEntryperpage) + "&calculate_count=true"
        endpointInfo=classes.classes.getRESTcp(deviceid,url)
        return {'endpointInfo': endpointInfo,'deviceInfo': deviceInfo, 'epTotalentries': endpointInfo['count'], 'epEntryperpage': epEntryperpage, 'epPageoffset': 0 , 'searchMacaddress': searchMacaddress, 'searchDescription': searchDescription, 'searchStatus': searchStatus }
    else:
        return {'endpointInfo': endpointInfo,'deviceInfo': deviceInfo, 'epTotalentries': endpointInfo['count'], 'epEntryperpage': epEntryperpage, 'epPageoffset': pageOffset , 'searchMacaddress': searchMacaddress, 'searchDescription': searchDescription, 'searchStatus': searchStatus }

def gettrustInfo(deviceid,trEntryperpage,trPageoffset, searchSubject, searchValid, searchStatus):
    if not trEntryperpage:
        trEntryperpage=25
    if not trPageoffset:
        pageOffset=0
    else:
        pageOffset=int(trPageoffset)*int(trEntryperpage)
    queryStr="select id, ipaddress, description from devices where id='{}'".format(deviceid)
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Obtain the ClearPass trusted certificates information from ClearPass
    url="cert-trust-list-details?filter=%7B%7D&sort=%2Bid&offset=" + str(pageOffset) + "&limit=" + str(trEntryperpage) + "&calculate_count=true"
    trustInfo=classes.classes.getRESTcp(deviceid,url)
    trustItems=[]
    # Now that we have all the certs, check whether we need to filter based on search criteria and adapt the counts
    if searchSubject:
        # We need to filter the items
        for li in trustInfo['_embedded']['items']:
            if searchSubject in li['subject_DN']:
                trustItems.append(li)
            trustInfo['_embedded']['items']=trustItems
        trustItems=[]
    if searchStatus:
        # We need to filter the items
        for li in trustInfo['_embedded']['items']:         
            if li['enabled'] == str_to_bool(searchStatus):
                trustItems.append(li)
            trustInfo['_embedded']['items']=trustItems
        trustItems=[]
    if searchValid:
        for li in trustInfo['_embedded']['items']:
            if searchValid in li['valid']:
                trustItems.append(li)
            trustInfo['_embedded']['items']=trustItems
        trustItems=[]
    if trustInfo==401:
        trustInfo={}
        return {'trustInfo': trustInfo,'deviceInfo': deviceInfo, 'trTotalentries': 0, 'trEntryperpage': trEntryperpage, 'trPageoffset': 0 , 'searchSubject': searchSubject, 'searchValid': searchValid, 'searchStatus': searchStatus }
    elif len(trustInfo)==0:
        # It might also be that the pageOffset is too far off finding information, if that is the case, set the pageOffset to 0 and query again
        url="cert-trust-list-details?filter=%7B%7D&sort=%2Bid&offset=0&limit=" + str(trEntryperpage) + "&calculate_count=true"
        trustInfo=classes.classes.getRESTcp(deviceid,url)
        return {'trustInfo': trustInfo,'deviceInfo': deviceInfo, 'trTotalentries': trustInfo['count'], 'trEntryperpage': trEntryperpage, 'trPageoffset': 0 , 'searchSubject': searchSubject, 'searchValid': searchValid, 'searchStatus': searchStatus }
    else:
        return {'trustInfo': trustInfo,'deviceInfo': deviceInfo, 'trTotalentries': trustInfo['count'], 'trEntryperpage': trEntryperpage, 'trPageoffset': trPageoffset , 'searchSubject': searchSubject, 'searchValid': searchValid, 'searchStatus': searchStatus }

def getservicesInfo(deviceid,seEntryperpage,sePageoffset, searchName, searchType, searchTemplate, searchStatus):
    if not seEntryperpage:
        seEntryperpage=25
    if not sePageoffset:
        pageOffset=0
    else:
        pageOffset=int(sePageoffset)*int(seEntryperpage)
    queryStr="select id, ipaddress, description from devices where id='{}'".format(deviceid)
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Obtain the ClearPass services information from ClearPass
    url="config/service?filter=%7B%7D&sort=%2Bid&offset=" + str(pageOffset) + "&limit=" + str(seEntryperpage) + "&calculate_count=true"
    servicesInfo=classes.classes.getRESTcp(deviceid,url)
    servicesItems=[]
    # Now that we have all the certs, check whether we need to filter based on search criteria and adapt the counts
    if searchName:
        # We need to filter the items
        for li in servicesInfo['_embedded']['items']:
            if searchName in li['name']:
                servicesItems.append(li)
            servicesInfo['_embedded']['items']=servicesItems
        servicesItems=[]
    if searchStatus:
        # We need to filter the items
        for li in servicesInfo['_embedded']['items']: 
            if li['enabled'] == str_to_bool(searchStatus):
                servicesItems.append(li)
            servicesInfo['_embedded']['items']=servicesItems
        servicesItems=[]
    if searchTemplate:
        for li in servicesInfo['_embedded']['items']:
            if searchTemplate in li['template']:
                servicesItems.append(li)
            servicesInfo['_embedded']['items']=servicesItems
        servicesItems=[]
    if searchType:
        for li in servicesInfo['_embedded']['items']:
            if searchType in li['type']:
                servicesItems.append(li)
        servicesItems=[]
    if servicesInfo==401:        
        servicesInfo={}
        return {'servicesInfo': servicesInfo,'deviceInfo': deviceInfo, 'seTotalentries': 0, 'seEntryperpage': seEntryperpage, 'sePageoffset': 0, 'searchName':searchName, 'searchType': searchType,'searchTemplate': searchTemplate,'searchStatus':searchStatus }
    elif len(servicesInfo)==0:
        # It might also be that the pageOffset is too far off finding information, if that is the case, set the pageOffset to 0 and query again
        url="config/service?filter=%7B%7D&sort=%2Bid&offset=0&limit=" + str(seEntryperpage) + "&calculate_count=true"
        servicesInfo=classes.classes.getRESTcp(deviceid,url)
        return {'servicesInfo': servicesInfo,'deviceInfo': deviceInfo, 'seTotalentries': servicesInfo['count'], 'seEntryperpage': seEntryperpage, 'sePageoffset': 0, 'searchName':searchName, 'searchType': searchType,'searchTemplate': searchTemplate,'searchStatus':searchStatus }
    else:
        return {'servicesInfo': servicesInfo,'deviceInfo': deviceInfo, 'seTotalentries': servicesInfo['count'], 'seEntryperpage': seEntryperpage, 'sePageoffset': pageOffset, 'searchName':searchName, 'searchType': searchType,'searchTemplate': searchTemplate,'searchStatus':searchStatus }