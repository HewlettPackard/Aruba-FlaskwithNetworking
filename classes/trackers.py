# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic DHCP Tracker classes

import classes.classes
import requests

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def dhcpdbAction():
    # This definition is when the DHCP tracker page is clicked
    # Obtain the DHCP types that exist in the database
    queryStr="select distinct dhcptype from dhcptracker"
    dhcptypeInfo=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select COUNT(*) as totalentries from dhcptracker"
    navResult=classes.classes.sqlQuery(queryStr,"selectone")
    return {'dhcptypeInfo': dhcptypeInfo, 'totalentries': navResult['totalentries']}

def snmpdbAction():
    # This definition is when the SNMP tracker page is clicked
    # Obtain all the SNMP versions that exist in the database
    queryStr="select distinct version from snmptracker"
    versionInfo=classes.classes.sqlQuery(queryStr,"select")
    # Obtain all the communities that exist in the database
    queryStr="select distinct community from snmptracker"
    communityInfo=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select COUNT(*) as totalentries from snmptracker"
    navResult=classes.classes.sqlQuery(queryStr,"selectone")
    return {'versionInfo':versionInfo, 'communityInfo':communityInfo, 'totalentries': navResult['totalentries']}

def syslogdbAction():
    # This definition is when the Syslog page is clicked
    # Obtain all the facilities that exist in the database
    queryStr="select distinct facility from syslog"
    facilityInfo=classes.classes.sqlQuery(queryStr,"select")
    # Obtain all the severities that exist in the database
    queryStr="select distinct severity from syslog"
    severityInfo=classes.classes.sqlQuery(queryStr,"select")
    queryStr="select COUNT(*) as totalentries from syslog"
    navResult=classes.classes.sqlQuery(queryStr,"selectone")
    return {'facilityInfo':facilityInfo, 'severityInfo':severityInfo, 'totalentries': navResult['totalentries']}
