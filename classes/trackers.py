# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic DHCP Tracker classes

import classes.classes
import requests

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def dhcpdbAction(formresult):
    # This definition is for all DHCP tracker actions
    queryStr="select distinct dhcptype from dhcptracker"
    dhcptypeInfo=classes.classes.sqlQuery(queryStr,"select")
    # Checkout orderby column and whether desc or asc
    newdescasc="DESC"
    neworderBy="order by utctime"
    searchAction="None"
    try:
        if formresult['searchType'] or formresult['searchInfo']:
            constructQuery= " where "
        else:
            constructQuery=""
        if formresult['searchType']:
            constructQuery += " dhcptype like'%" + formresult['searchType'] + "%' AND "
        if formresult['searchInfo']:
            constructQuery += " information like '%" + formresult['searchInfo'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from dhcptracker " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        pageoffset=navResult['pageoffset']
        queryStr="select * from dhcptracker " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    except:
        # There is no formresult, start with default query
        queryStr="select COUNT(*) as totalentries from dhcptracker"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from dhcptracker ORDER BY utctime DESC LIMIT {} offset 0".format(entryperpage)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'dbresult':result,'dhcptypeInfo': dhcptypeInfo, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def snmpdbAction(formresult):
    # This definition is for all SNMP tracker actions
    # First obtain all the SNMP versions that exists in the database
    queryStr="select distinct version from snmptracker"
    versionInfo=classes.classes.sqlQuery(queryStr,"select")
    # Then obtain all the communities that exist in the database
    queryStr="select distinct community from snmptracker"
    communityInfo=classes.classes.sqlQuery(queryStr,"select")
    try:
        if formresult['searchSource'] or formresult['searchVersion'] or formresult['searchCommunity'] or formresult['searchInfo']:
            constructQuery= " where "
        else:
            constructQuery=""
        if formresult['searchSource']:
            constructQuery += " source like'%" + formresult['searchSource'] + "%' AND "
        if formresult['searchVersion']:
            constructQuery += " version='" + formresult['searchVersion'] + "' AND "
        if formresult['searchCommunity']:
            constructQuery += " community='" + formresult['searchCommunity'] + "' AND "
        if formresult['searchInfo']:
            constructQuery += " information like '%" + formresult['searchInfo'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from snmptracker " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        pageoffset=navResult['pageoffset']
        queryStr="select * from snmptracker " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    except:
        # There is no formresult, start with default query
        queryStr="select COUNT(*) as totalentries from snmptracker"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from snmptracker ORDER BY utctime DESC LIMIT {} offset 0".format(entryperpage)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'dbresult':result, 'versionInfo':versionInfo, 'communityInfo':communityInfo, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def syslogdbAction(formresult):
    # This definition is for all Syslog actions
    # First obtain all the facilities that exists in the database
    queryStr="select distinct facility from syslog"
    facilityInfo=classes.classes.sqlQuery(queryStr,"select")
    # Then obtain all the severities that exist in the database
    queryStr="select distinct severity from syslog"
    severityInfo=classes.classes.sqlQuery(queryStr,"select")
    try:
        if formresult['searchSource'] or formresult['searchFacility'] or formresult['searchSeverity'] or formresult['searchInfo']:
            constructQuery= " where "
        else:
            constructQuery=""
        if formresult['searchSource']:
            constructQuery += " source like'%" + formresult['searchSource'] + "%' AND "
        if formresult['searchFacility']:
            constructQuery += " facility='" + formresult['searchFacility'] + "' AND "
        if formresult['searchSeverity']:
            constructQuery += " severity='" + formresult['searchSeverity'] + "' AND "
        if formresult['searchInfo']:
            constructQuery += " information like '%" + formresult['searchInfo'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from syslog " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        pageoffset=navResult['pageoffset']
        queryStr="select * from syslog " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    except:
        # There is no formresult, start with default query
        queryStr="select COUNT(*) as totalentries from syslog"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from syslog ORDER BY utctime DESC LIMIT {} offset 0".format(entryperpage)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'dbresult':result, 'facilityInfo':facilityInfo, 'severityInfo':severityInfo, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}
