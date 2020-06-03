# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

import pyshark
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
    trackerslog = open('/var/www/html/log/trackers.log', 'a')
    pathname = os.path.dirname(sys.argv[0])
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
        pkts=pyshark.FileCapture('/var/www/html/bash/trace.pcap')
        pkts.load_packets()
    except:
        pkts=""
    # Check for DHCP, Syslog and SNMP packets
    
    for i in range(len(pkts)):
        print("Packet {} destination port {}".format(i,pkts[i].udp.dstport))
        # trackerslog.write('Analyze packets\n')
        try:
            if pkts[i].udp.dstport=="67" or pkts[i].udp.dstport=="68":
                # Tshark returns different layer information for DHCP/bootp. It might be either "bootp" or "dhcp"
                # Therefore we need to check whether the bootp or dhcp fieldnames exist and make the changed accordingly
                if "BOOTP" in str(pkts[i].layers):
                    bord="bootp"
                else:
                    bord="dhcp"
                # trackerslog.write('Analyze DHCP packet\n')
                # Match DHCP Discover
                if bord=="bootp":
                    fieldnames=list(pkts[i].bootp.field_names)
                else:
                    fieldnames=list(pkts[i].dhcp.field_names)
                if bord=="dhcp":
                    if pkts[i].dhcp.option_value == "01":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                information="Host " + pkts[i].dhcp.hw_mac_addr + " asked for an IP address"
                                options=""
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Discover','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP discover packet")
                    # Match DHCP offer
                    elif pkts[i].dhcp.option_value == "02":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "ip_server" in fieldnames:
                                    dhcpserver=pkts[i].dhcp.ip_server
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    offeredip=pkts[i].dhcp.ip_your
                                else:
                                    offeredip="Unknown"
                                if "option_subnet_mask" in fieldnames:
                                    subnetmask=pkts[i].dhcp.option_subnet_mask
                                else:
                                    subnetmask="Unknown"
                                if "option_ip_address_lease_time" in fieldnames:
                                    leasetime=pkts[i].dhcp.option_ip_address_lease_time
                                else:
                                    leasetime="Unknown"
                                if "option_router" in fieldnames:
                                    router=pkts[i].dhcp.option_router
                                else:
                                    router="Unknown"
                                if "option_domain_name_server" in fieldnames:
                                    nameserver=pkts[i].dhcp.option_domain_name_server
                                else:
                                    nameserver="Unknown"
                                if "option_domain_name" in fieldnames:
                                    domainname=pkts[i].dhcp.option_domain_name
                                else:
                                    domainname="Unknown"
                                if domainname!="Unknown" and nameserver!="Unknown" and router!="Unknown" and leasetime!="Unknown" and offeredip!="Unknown" and dhcpserver!="Unknown":
                                    information="DHCP Server " + dhcpserver + " offered " + offeredip
                                    options="Subnet mask: " + subnetmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + nameserver + ", domain: " + domainname
                                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Offer','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                    cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP offer packet in packet {}".format[i])
                    # Match DHCP request
                    elif pkts[i].dhcp.option_value == "03":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "hw_mac_addr" in fieldnames:
                                    macaddress=pkts[i].dhcp.hw_mac_addr
                                else:
                                    macaddress="Unknown"
                                if "option_requested_ip_address" in fieldnames:
                                    requestedip=pkts[i].dhcp.option_requested_ip_address
                                else:
                                    requestedip="Unknown"
                                information="Host " + macaddress + " requested " + requestedip
                                options=""
                                if macaddress!="Unknown" and requestedip!="Unknown":
                                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                    cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP request in packet {}".format(i))
                    # Match DHCP ack
                    elif pkts[i].dhcp.option_value == "05":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
    
                                if "option_subnet_mask" in fieldnames:
                                    netmask=pkts[i].dhcp.option_subnet_mask
                                else:
                                    netmask="Unknown"
                                if "option_ip_address_lease_time" in fieldnames:
                                    leasetime=pkts[i].dhcp.option_ip_address_lease_time
                                else:
                                    leasetime="Unknown"
                                if "option_router" in fieldnames:
                                    router=pkts[i].dhcp.option_router
                                else:
                                    router="Unknown"
                                if "option_domain_name_server" in fieldnames:
                                    dnsserver=pkts[i].dhcp.option_domain_name_server
                                else:
                                    dnsserver="Unknown"
                                if "option_dhcp_server_id" in fieldnames:
                                    dhcpserver=pkts[i].dhcp.option_dhcp_server_id
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    clientip=pkts[i].dhcp.ip_your
                                else:
                                    clientip="Unknown"
                                # The tracker class is also used for ZTP. Goal is to have the switch keep it's DHCP IP address. 
                                try:
                                    if "hw_mac_addr" in fieldnames and "ip_your" in fieldnames and netmask!="Unknown" and router!="Unknown":
                                        ztpmacaddress=pkts[i].dhcp.hw_mac_addr
                                        ztpmacaddress=ztpmacaddress.replace(":","")
                                        ztpnetmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
                                        queryStr="select * from ztpdevices where macaddress='{}'".format(ztpmacaddress)
                                        cursor.execute(queryStr)
                                        result=cursor.fetchall()
                                        if result:
                                            # We found a ZTP device entry and need to update the IP address information, but only if DHCP ZTP is enabled
                                            timeStamp=float(pkts[i].sniff_timestamp)
                                            trackerslog.write('{}: Found ZTP entry for {}\n'.format(datetime.fromtimestamp(int(timeStamp)),ztpmacaddress))
                                            if result[0]['ztpdhcp']==1:
                                                queryStr="update ztpdevices set ipaddress='{}', netmask='{}', gateway='{}' where id='{}'".format(clientip,ztpnetmask,router,result[0]['id'])
                                                cursor.execute(queryStr)
                                                trackerslog.write('{}: {} Updated ZTP Device with MAC Address {}: {}\n'.format(bord,datetime.fromtimestamp(int(timeStamp)).strftime('%-m/%-d/%Y, %H:%M:%S %p'),ztpmacaddress, clientip))
                                except:
                                    print("Cannot analyze ZTP packet {}".format(i))
                                information="DHCP Server " + dhcpserver + " acknowledged " + clientip                         
                                options="Subnet_mask: " + netmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + dnsserver
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP ack packet")
                    # Match DHCP NAK
                    elif pkts[i].dhcp.option_value == "06":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "option_dhcp_server_id" in fieldnames:
                                    dhcpserver=pkts[i].dhcp.option_dhcp_server_id
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    ip_your=pkts[i].dhcp.ip_your
                                else:
                                    ip_your="Unknown"
                                if "ip_client" in fieldnames:
                                    clientip=pkts[i].dhcp.ip_client
                                else:
                                    clientip="Unknown"
                                if "hw_mac_addr" in fieldnames:
                                    hwmacaddr=pkts[i].dhcp.hw_mac_addr
                                else:
                                    hwmacaddr="Unknown"
                                if "option_message" in fieldnames:
                                    optionmessage=pkts[i].dhcp.option_message
                                else:
                                    optionmessage="Unknown"
                                information="DHCP NAK: " + optionmessage + ". " + ip_your + "  not available on " + dhcpserver
                                options="IP client: " + clientip + ", MAC address: " + hwmacaddr
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP NAK','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP NAK packet {}".format(i))
                    # Match DHCP release
                    elif pkts[i].dhcp.option_value == "07":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "option_dhcp_server_id" in fieldnames:
                                    dhcpserver=pkts[i].dhcp.option_dhcp_server_id
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    ip_your=pkts[i].dhcp.ip_your
                                else:
                                    ip_your="Unknown"
                                if "ip_client" in fieldnames:
                                    clientip=pkts[i].dhcp.ip_client
                                else:
                                    clientip="Unknown"
                                if "hw_mac_addr" in fieldnames:
                                    hwmacaddr=pkts[i].dhcp.hw_mac_addr
                                else:
                                    hwmacaddr="Unknown"
                                if "option_hostname" in fieldnames:
                                    hostname=pkts[i].dhcp.option_hostname
                                else:
                                    hostname="Unknown"
                                information="DHCP Server " + dhcpserver + "  released " + ip_your
                                options="IP client: " + clientip + ", MAC address: " + hwmacaddr + ", Hostname: " + hostname
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Release','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP release packet {}".format(i))
                    # Match DHCP inform
                    elif pkts[i].dhcp.option_value == "08":
                        try:    
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                information="DHCP Inform from " + pkts[i].ip.src + " (" + pkts[i].eth.src + ") Hostname: " + pkts[i].dhcp.option_hostname + ", Vendor Class ID: " + pkts[i].dhcp.option_vendor_class_id
                                options=""
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Inform','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP Inform packet")
                else:
                    if pkts[i].bootp.option_value == "01":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                information="Host " + pkts[i].bootp.hw_mac_addr + " asked for an IP address"
                                options=""
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Discover','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP discover packet")
                    # Match DHCP offer
                    elif pkts[i].bootp.option_value == "02":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "ip_server" in fieldnames:
                                    dhcpserver=pkts[i].bootp.ip_server
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    offeredip=pkts[i].bootp.ip_your
                                else:
                                    offeredip="Unknown"
                                if "option_subnet_mask" in fieldnames:
                                    subnetmask=pkts[i].bootp.option_subnet_mask
                                else:
                                    subnetmask="Unknown"
                                if "option_ip_address_lease_time" in fieldnames:
                                    leasetime=pkts[i].bootp.option_ip_address_lease_time
                                else:
                                    leasetime="Unknown"
                                if "option_router" in fieldnames:
                                    router=pkts[i].bootp.option_router
                                else:
                                    router="Unknown"
                                if "option_domain_name_server" in fieldnames:
                                    nameserver=pkts[i].bootp.option_domain_name_server
                                else:
                                    nameserver="Unknown"
                                if "option_domain_name" in fieldnames:
                                    domainname=pkts[i].bootp.option_domain_name
                                else:
                                    domainname="Unknown"
                                if domainname!="Unknown" and nameserver!="Unknown" and router!="Unknown" and leasetime!="Unknown" and offeredip!="Unknown" and dhcpserver!="Unknown":
                                    information="DHCP Server " + dhcpserver + " offered " + offeredip
                                    options="Subnet mask: " + subnetmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + nameserver + ", domain: " + domainname
                                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Offer','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                    cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP offer packet in packet {}".format[i])
                    # Match DHCP request
                    elif pkts[i].bootp.option_value == "03":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "hw_mac_addr" in fieldnames:
                                    macaddress=pkts[i].bootp.hw_mac_addr
                                else:
                                    macaddress="Unknown"
                                if "option_requested_ip_address" in fieldnames:
                                    requestedip=pkts[i].bootp.option_requested_ip_address
                                else:
                                    requestedip="Unknown"
                                information="Host " + macaddress + " requested " + requestedip
                                options=""
                                if macaddress!="Unknown" and requestedip!="Unknown":
                                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                    cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP request in packet {}".format(i))
                    # Match DHCP ack
                    elif pkts[i].bootp.option_value == "05":  
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "option_subnet_mask" in fieldnames:
                                    netmask=pkts[i].bootp.option_subnet_mask
                                else:
                                    netmask="Unknown"
                                if "option_ip_address_lease_time" in fieldnames:
                                    leasetime=pkts[i].bootp.option_ip_address_lease_time
                                else:
                                    leasetime="Unknown"
                                if "option_router" in fieldnames:
                                    router=pkts[i].bootp.option_router
                                else:
                                    router="Unknown"
                                if "option_domain_name_server" in fieldnames:
                                    dnsserver=pkts[i].bootp.option_domain_name_server
                                else:
                                    dnsserver="Unknown"
                                # The tracker class is also used for ZTP. Goal is to have the switch keep it's DHCP IP address. 
                                try:
                                    if "hw_mac_addr" in fieldnames and "ip_your" in fieldnames and netmask!="Unknown" and router!="Unknown":
                                        ztpmacaddress=pkts[i].bootp.hw_mac_addr
                                        ztpmacaddress=ztpmacaddress.replace(":","")
                                        ztpnetmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
                                        queryStr="select * from ztpdevices where macaddress='{}'".format(ztpmacaddress)
                                        cursor.execute(queryStr)
                                        result=cursor.fetchall()
                                        if result:
                                            timeStamp=float(pkts[i].sniff_timestamp)
                                            trackerslog.write('{}: {} Found ZTP entry for {}\n'.format(bord,datetime.fromtimestamp(int(timeStamp)),ztpmacaddress))
                                            # We found a ZTP device entry and need to update the IP address information, but only if DHCP ZTP is enabled
                                            if result[0]['ztpdhcp']==1:
                                                queryStr="update ztpdevices set ipaddress='{}', netmask='{}', gateway='{}' where id='{}'".format(pkts[i].bootp.ip_your,ztpnetmask,router,result[0]['id'])
                                                cursor.execute(queryStr)
                                                trackerslog.write('{}: Updated ZTP Device with MAC Address {}: {}\n'.format(datetime.fromtimestamp(int(timeStamp)).strftime('%-m/%-d/%Y, %H:%M:%S %p'),ztpmacaddress, clientip))
                                except:
                                    print("Cannot analyze ZTP packet {}".format(i))
                                information="DHCP Server " + pkts[i].bootp.option_dhcp_server_id + " acknowledged " + pkts[i].bootp.ip_your
                                options="Subnet_mask: " + netmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + dnsserver
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP ack packet")
                    # Match DHCP NAK
                    elif pkts[i].bootp.option_value == "06":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "option_dhcp_server_id" in fieldnames:
                                    dhcpserver=pkts[i].bootp.option_dhcp_server_id
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    ip_your=pkts[i].bootp.ip_your
                                else:
                                    ip_your="Unknown"
                                if "ip_client" in fieldnames:
                                    clientip=pkts[i].bootp.ip_client
                                else:
                                    clientip="Unknown"
                                if "hw_mac_addr" in fieldnames:
                                    hwmacaddr=pkts[i].bootp.hw_mac_addr
                                else:
                                    hwmacaddr="Unknown"
                                if "option_message" in fieldnames:
                                    optionmessage=pkts[i].bootp.option_message
                                else:
                                    optionmessage="Unknown"
                                information="DHCP NAK: " + optionmessage + ". " + ip_your + "  not available on " + dhcpserver
                                options="IP client: " + clientip + ", MAC address: " + hwmacaddr
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP NAK','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP NAK packet {}".format(i))
                    # Match DHCP release
                    elif pkts[i].bootp.option_value == "07":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                if "option_dhcp_server_id" in fieldnames:
                                    dhcpserver=pkts[i].bootp.option_dhcp_server_id
                                else:
                                    dhcpserver="Unknown"
                                if "ip_your" in fieldnames:
                                    ip_your=pkts[i].bootp.ip_your
                                else:
                                    ip_your="Unknown"
                                if "ip_client" in fieldnames:
                                    clientip=pkts[i].bootp.ip_client
                                else:
                                    clientip="Unknown"
                                if "hw_mac_addr" in fieldnames:
                                    hwmacaddr=pkts[i].bootp.hw_mac_addr
                                else:
                                    hwmacaddr="Unknown"
                                if "option_hostname" in fieldnames:
                                    hostname=pkts[i].bootp.option_hostname
                                else:
                                    hostname="Unknown"
                                information="DHCP Server " + dhcpserver + "  released " + ip_your
                                options="IP client: " + clientip + ", MAC address: " + hwmacaddr + ", Hostname: " + hostname
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Release','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP release packet {}".format(i))
                    # Match DHCP inform
                    elif pkts[i].dhcp.option_value == "08":
                        try:
                            if float(pkts[i].sniff_timestamp) > utctimedhcp:
                                information="DHCP Inform from " + pkts[i].ip.src + " (" + pkts[i].eth.src + ") Hostname: " + pkts[i].bootp.option_hostname + ", Vendor Class ID: " + pkts[i].bootp.option_vendor_class_id
                                options=""
                                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(pkts[i].sniff_timestamp,information,options)
                                cursor.execute(queryStr)
                        except:
                            print("Could not analyze DHCP Inform packet")

            elif pkts[i].udp.dstport=="161" or pkts[i].udp.dstport=="162":
                    # trackerslog.write('Analyze SNMP packet\n')
                fieldnames=list(pkts[i].snmp.field_names)
                try:
                    if float(pkts[i].sniff_timestamp) > utctimesnmp:
                        generictraps=['Cold start','Warm start','Link down','Link up','Authentication failure','EGP Neighbor loss']
                        snmpversions=['V1', 'V2c']
                        if "generic_trap" in fieldnames:
                            if pkts[i].snmp.generic_trap=="6":
                                # This is an enterprise trap. Need to analyze a bit further
                                trapMessage="Enterprise trap"
                            else:
                                trapMessage=generictraps[int(pkts[i].snmp.generic_trap)]
                                trapMessage=trapMessage.replace("'","\\'")
                        else:
                            trapMessage=""
                        if "version" in fieldnames:
                            snmpversion=snmpversions[int(pkts[i].snmp.version)]
                        else:
                            snmpversion="Unknown"
                        if trapMessage!="":
                            queryStr="insert into snmptracker (utctime,source,version,community,information) values ('{}','{}','{}','{}','{}')".format(pkts[i].sniff_timestamp,pkts[i].ip.src_host,snmpversion,pkts[i].snmp.community,trapMessage)
                            cursor.execute(queryStr)
                except:
                    print("Could not analyze SNMP packet {}".format(i))
            elif pkts[i].udp.dstport=="514":
                # trackerslog.write('Analyze Syslog packet\n')
                try:
                    if float(pkts[i].sniff_timestamp) > utctimesyslog:
                        message=str(pkts[i].syslog.msg)
                        message=message.replace("'","\\'")
                        queryStr="insert into syslog (utctime,source,facility,severity,information) values ('{}','{}','{}','{}','{}')".format(pkts[i].sniff_timestamp,pkts[i].ip.src_host,syslogFacilities[int(pkts[i].syslog.facility)],syslogSeverity[int(pkts[i].syslog.level)],message)
                        cursor.execute(queryStr)
                except:
                    print("Could not analyze Syslog packet {}".format(i))
        except:
            print("There is something wrong with the network trace process: {}".format(i))
    trackerslog.close()
    dbconnection.close()

def ztpCheck(macaddress,ipaddress,netmask,gateway,dns,cursor):
    macaddress=macaddress.replace(":","")
    netmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
    queryStr="select * from ztpdevices where macaddress='{}'".format(macaddress)
    cursor.execute(queryStr)
    result=cursor.fetchall()
    if result:
        # We found a ZTP device entry and need to update the IP address information
        queryStr="update ztpdevices set ipaddress='{}', netmask='{}', gateway='{}' where id='{}'".format(ipaddress,netmask,gateway,result[0]['id'])
        cursor.execute(queryStr)