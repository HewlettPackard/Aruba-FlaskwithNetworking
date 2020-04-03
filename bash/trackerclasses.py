# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from scapy.all import *
from datetime import datetime, time, timedelta
import time
import json
import pymysql.cursors
import re
import sys
import os
import platform
import requests
from jinja2 import Template
import urllib3
from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def trackers():
    pathname = os.path.dirname(sys.argv[0])
    if platform.system()=="Windows":
        appPath = os.path.abspath(pathname) + "\\globals.json"      
    else:
        appPath = os.path.abspath(pathname) + "/globals.json"
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    syslogFacilities=("Kernel messages","User-level","Mail system","System daemons","Security authorization","Messages generated internally by syslogd",\
"Line printer subsystem","Network news subsystem","UUCP subsystem","Clock daemon","Security authorization","FTP daemon","NTP subsystem",\
"Log audit","Log alert","Clock daemon","Local use 0 (local0)","Local use 1 (local1)","Local use 2 (local2)","Local use 3 (local3)","Local use 4 (local4)",\
"Local use 5 (local5)","Local use 6 (local6)","Local use 7 (local7))")
    syslogSeverity=("Emergency","Alert","Critical","Error","Warning","Notice","Informational","Debug")
    #select the latest timestamp from the database. Only events that have a newer timestamp should be stored in the database
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    #Get the latest timestamp from the DHCP tracker table
    queryStr="SELECT MAX(utctime) as utctime from dhcptracker"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    if result[0]['utctime']:
        utctimedhcp=float(result[0]['utctime'])
    else:
        utctimedhcp=0.00000
        utctimedhcp=float(utctimedhcp)
    #Get the latest timestamp from the SNMP tracker table
    queryStr="SELECT MAX(utctime) as utctime from snmptracker"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    if result[0]['utctime']:
        utctimesnmp=float(result[0]['utctime'])
    else:
        utctimesnmp=0.00000
        utctimesnmp=float(utctimesnmp)
    #Get the latest timestamp from the Syslog table
    queryStr="SELECT MAX(utctime) as utctime from syslog"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    if result[0]['utctime']:
        utctimesyslog=float(result[0]['utctime'])
    else:
        utctimesyslog=0.00000
        utctimesyslog=float(utctimesyslog)
    # Open the pcap file
    try:
        if os.path.isfile(globalconf['pcap_location']):
            pkts=rdpcap(globalconf['pcap_location'])
        else:
            pkts=""
    except:
        pkts=""

    # Check for DHCP, Syslog and SNMP packets
    for i in range(len(pkts)):
        try:
            if pkts[i].dport==67 or pkts[i].dport==68 or pkts[i].dport=="bootps" or pkts[i].dport=="bootpc":
                # Match DHCP Discover
                if DHCP in pkts[i] and pkts[i]['DHCP'].options[0][1] == 1:
                    hostname = getOption(pkts[i]['DHCP'].options, 'hostname')
                    if pkts[i].time > utctimedhcp:
                        information="Host " + str(hostname) + " (" + pkts[i][Ether].src + ") asked for an IP"
                        options=""
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Discover','{}','{}')".format(pkts[i].time,information,options)
                        cursor.execute(queryStr)
                # Match DHCP offer
                elif DHCP in pkts[i] and pkts[i][DHCP].options[0][1] == 2:
                    subnet_mask = getOption(pkts[i][DHCP].options, 'subnet_mask')
                    lease_time = getOption(pkts[i][DHCP].options, 'lease_time')
                    router = getOption(pkts[i][DHCP].options, 'router')
                    name_server = getOption(pkts[i][DHCP].options, 'name_server')
                    domain = getOption(pkts[i][DHCP].options, 'domain')
                    if pkts[i].time > utctimedhcp:
                        information="DHCP Server " + pkts[i][IP].src + "(" + pkts[i][Ether].src + ") offered " + pkts[i][BOOTP].yiaddr
                        options="Subnet mask: " + subnet_mask + ", Lease time: " + str(lease_time) + ", Router: " + router + ", Name Server: " + name_server + ", domain: " + str(domain)
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Offer','{}','{}')".format(pkts[i].time,information,options)
                        cursor.execute(queryStr)
                # Match DHCP request
                elif DHCP in pkts[i] and pkts[i][DHCP].options[0][1] == 3:
                    requested_addr = getOption(pkts[i][DHCP].options, 'requested_addr')
                    hostname = getOption(pkts[i][DHCP].options, 'hostname')
                    if pkts[i].time > utctimedhcp:
                        information="Host " + str(hostname) + " (" + pkts[i][Ether].src + ") requested " + str(requested_addr)
                        options=""
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].time,information,options)
                        cursor.execute(queryStr)
                # Match DHCP ack
                elif DHCP in pkts[i] and pkts[i][DHCP].options[0][1] == 5:
                    subnet_mask = getOption(pkts[i][DHCP].options, 'subnet_mask')
                    lease_time = getOption(pkts[i][DHCP].options, 'lease_time')
                    router = getOption(pkts[i][DHCP].options, 'router')
                    name_server = getOption(pkts[i][DHCP].options, 'name_server')
                    if pkts[i].time > utctimedhcp:
                        information="DHCP Server " + pkts[i][IP].src + " (" + pkts[i][Ether].src + ") acked " + str(pkts[i][BOOTP].yiaddr)
                        options="Subnet_mask: " + str(subnet_mask) + ", Lease time: " + str(lease_time) + ", Router: " + str(router) + ", Name Server: " + str(name_server)
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].time,information,options)
                        cursor.execute(queryStr)
                # Match DHCP inform
                elif DHCP in pkts[i] and pkts[i][DHCP].options[0][1] == 8:
                    hostname = getOption(pkts[i][DHCP].options, 'hostname')
                    vendor_class_id = getOption(pkts[i][DHCP].options, 'vendor_class_id')
                    if pkts[i].time > utctimedhcp:
                        information="DHCP Inform from " + pkts[i][IP].src + " (" + pkts[i][Ether].src + ") Hostname: " + str(hostname) + ", Vendor Class ID: " + str(vendor_class_id)
                        options=""
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].time,information,options)
                        cursor.execute(queryStr)
            elif pkts[i].dport==162 or pkts[i].dport=="snmp":
                snmpInfo=getSNMPinfo(pkts[i][SNMP].show(dump=True))
                # If there is SNMP information we should create a database entry. So snmpInfo[1] should contain information and the timestamp of the packet should be
                # later than the latest timestamp in the database
                if pkts[i].time > utctimesnmp and snmpInfo[0] and snmpInfo[1] and snmpInfo[2]:
                    queryStr="insert into snmptracker (utctime,source,version,community,information) values ('{}','{}','{}','{}','{}')".format(pkts[i].time,pkts[i][IP].src,snmpInfo[0],snmpInfo[1],snmpInfo[2])
                    cursor.execute(queryStr)
            elif pkts[i].dport==514 or pkts[i].dport=="syslog":
                # The first part between brackets <> shows the syslog type. This has to be converted to a binary value and then split.
                # The syslogFacility and syslogSeverity values can then be applied
                # In addition, a syslog entry can have single quotes. If this is the situation, the syslog message is enclosed by double quotes
                if pkts[i]['Raw'].show(dump=True).count('\"')==2:
                    syslogInfo=re.findall(r"\"(.*?)\"", pkts[i]['Raw'].show(dump=True), re.DOTALL)
                else:
                    syslogInfo=re.findall(r"'(.*?)'", pkts[i]['Raw'].show(dump=True), re.DOTALL)
                try:
                    infoType=str(bin(int(syslogInfo[0][1:3])))
                    # Now we need to split the binary. The last three bits represent the severity, the first bits represent the facility
                    # For this, we have to convert to string again, and then split on the 5th character 
                    infoType=infoType.replace("0b","")
                    sevInfo=int(infoType[-3:],base=2)
                    facInfo=int(infoType[:-3],base=2)
                    information=syslogInfo[0][4:].replace('\'','')
                    # If the first character in the information var is still >, then also remove that one
                    if information[0:1]==">":
                        information=information[1:]
                    if pkts[i].time > utctimesyslog:
                        queryStr="insert into syslog (utctime,source,facility,severity,information) values ('{}','{}','{}','{}','{}')".format(pkts[i].time,pkts[i][IP].src,syslogFacilities[facInfo],syslogSeverity[sevInfo],information)
                        cursor.execute(queryStr)
                except:
                    pass
        except:
            print("There is something wrong with the network trace process")
    dbconnection.close()
    
def getSNMPinfo(snmpinfo):
    snmpList=snmpinfo.split("\\PDU")
    snmpVars=snmpList[1].split("|")
    trapInfo=""
    additionalInfo=""
    # Get generic trap info
    for i in range(len(snmpVars)):
        if "generic_trap" in snmpVars[i]:
            trapInfo=re.search(r"(?<=').*?(?=')", snmpVars[i]).group(0)
        elif "SNMPinform" in snmpVars[i]:
            trapInfo="SNMP Inform"
    # Get additional trap information. Only the entries that contain information are interesting. Need to search on [b'
    if trapInfo!="enterprise_specific":
        for i in range(len(snmpVars)):
            if "[b" in snmpVars[i]:
                addInfo=re.search(r"(?<=').*?(?=')", snmpVars[i]).group(0) 
                if addInfo:
                    additionalInfo += addInfo + ", "
        if additionalInfo:
            trapInfo=trapInfo + " (" + additionalInfo[:-2] + ")"
        else:
            trapInfo=""
    else:
        trapInfo=""
    # snmpArr[0] contains version and community information. I only need that information so strip all the other info.
    VersionAndCommunity=re.findall(r"'(.*?)'", snmpList[0], re.DOTALL)
    # VersionAndCommunity[0] contains version, VersionAndCommunity[1] contains community
    return [VersionAndCommunity[0],VersionAndCommunity[1], trapInfo]
   
def getOption(dhcpOptions, key):
    mustDecode = ['hostname', 'domain', 'vendor_class_id']
    try:
        for i in dhcpOptions:
            if i[0] == key:
                # If DHCP Server Returned multiple name servers 
                # return all as comma seperated string.
                if key == 'name_server' and len(i) > 2:
                    return ",".join(i[1:])
                # domain and hostname are binary strings,
                # decode to unicode string before returning
                elif key in mustDecode:
                    return i[1].decode()
                else: 
                    return i[1]        
    except:
        pass