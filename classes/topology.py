# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic Aruba Topology classes

import classes.classes
import requests
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    
def topodbAction(formresult):
    # This definition is for all the database actions for topology, based on the user click on the pages
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    result={}
    if(bool(formresult)==True): 
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if formresult['searchHostname'] or formresult['searchSwitchip'] or formresult['searchSystemmac']:
            constructQuery= " where "
        else:
            constructQuery="      "
        if formresult['searchHostname']:
            constructQuery += " hostname like'%" + formresult['searchHostname'] + "%' AND "
        if formresult['searchSwitchip']:
            constructQuery += " switchip like '%" + formresult['searchSwitchip'] + "%' AND "
        if formresult['searchSystemmac']:
            constructQuery += " systemmac like'%" + formresult['searchSystemmac'] + "%' AND "

        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from topology " + constructQuery[:-4] + " GROUP BY switchip"
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="SELECT switchip, MAX(id) AS id, MAX(systemmac) AS systemmac, MAX(hostname) as hostname FROM topology " + constructQuery[:-4]  + " GROUP BY switchip LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from topology GROUP BY switchip"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        if navResult:
            totalentries=navResult['totalentries']
        else:
            totalentries=0
        entryperpage=10
        pageoffset=0
        queryStr="SELECT switchip, MAX(id) AS id, MAX(systemmac) AS systemmac, MAX(hostname) as hostname FROM topology GROUP BY switchip"  + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result,'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def endpointInfo(id):
    # First, obtain the IP address of the device, so that we can obtain all the topology information
    queryStr="select switchip from topology where id='{}'".format(id)
    ipresult=classes.classes.sqlQuery(queryStr,"selectone")
    # Now, select all the entries
    queryStr="select * from topology where switchip='{}'".format(ipresult['switchip']) + " order by interface"
    result=classes.classes.sqlQuery(queryStr,"select")
    return result

def checktopoDevice(deviceid):
    # Obtain IP address from the topology table first
    queryStr="select switchip from topology where id='{}'".format(deviceid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    queryStr="select id,ostype from devices where ipaddress='{}'".format(result['switchip'])
    result=classes.classes.sqlQuery(queryStr,"selectone")
    # Based on the switch type, check if the device is online
    return classes.classes.checkifOnline(result['id'],result['ostype'])

def topoInfo(deviceid):
    # Obtain IP address from the topology table first
    queryStr="select * from topology where id='{}'".format(deviceid)
    sourceresult=classes.classes.sqlQuery(queryStr,"selectone")
    nodes=[{'name': sourceresult['switchip'], 'label': sourceresult['hostname']}]
    links=[]
    # Now, select all the entries
    queryStr="select * from topology where switchip='{}'".format(sourceresult['switchip']) + " order by interface"
    linkresult=classes.classes.sqlQuery(queryStr,"select")
    # Now construct the nodes and links
    for items in linkresult:
        lldpinfo=json.loads(items['lldpinfo'])
        nodes.append({'name':items['remoteswitchip'],'label':items['remotehostname']})
        links.append({'target':items['remoteswitchip'],'remoteinterface':items['remoteinterface'],'source': sourceresult['switchip'],'localinterface':items['interface']})
    return nodes,links



