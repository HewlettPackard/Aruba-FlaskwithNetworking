import pyshark
from datetime import datetime, time, timedelta
import time
import json
import os
import sys
import pymysql.cursors

pathname = os.path.dirname(sys.argv[0])
appPath = os.path.abspath(pathname) + "/globals.json"
with open(appPath, 'r') as myfile:
    data=myfile.read()
globalconf=json.loads(data)
listenerlog = open('/var/www/html/log/listener.log', 'a')
activeInterface=str(sys.argv[1])

syslogFacilities=("Kernel messages","User-level","Mail system","System daemons","Security authorization","Messages generated internally by syslogd",\
"Line printer subsystem","Network news subsystem","UUCP subsystem","Clock daemon","Security authorization","FTP daemon","NTP subsystem",\
"Log audit","Log alert","Clock daemon","Local use 0 (local0)","Local use 1 (local1)","Local use 2 (local2)","Local use 3 (local3)","Local use 4 (local4)",\
"Local use 5 (local5)","Local use 6 (local6)","Local use 7 (local7))")
syslogSeverity=("Emergency","Alert","Critical","Error","Warning","Notice","Informational","Debug")

dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)

def capture_live_packets(network_interface,listenerlog,cursor,syslogFacilities,syslogSeverity):
    # Need to capture GRE, DHCP, SNMP and Syslog packets
    capture = pyshark.LiveCapture(interface=network_interface, bpf_filter='udp port 47 or udp port 67 or udp port 68 or udp port 161 or udp port 514')
    for raw_packet in capture.sniff_continuously():
        filter_udp_traffic_file(raw_packet,listenerlog,cursor,syslogFacilities,syslogSeverity)

def analyzeDHCP(packet,listenerlog,cursor):
    if "BOOTP" in str(packet.layers):
        bord="bootp"
    else:
        bord="dhcp"
    # listenerlog.write('Analyze DHCP packet\n')
    if bord=="bootp":
        fieldnames=list(packet.bootp.field_names)
    else:
        fieldnames=list(packet.dhcp.field_names)
    if bord=="dhcp":
        # Match DHCP Discover
        if packet.dhcp.option_value == "01":
            try:
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","") 
                else:
                    macaddress="000000000000"
                if not macaddress.startswith("204c03"):
                    information="Host " + macaddress + " asked for an IP address"
                    options=""
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Discover','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP discover packet")
                    # Match DHCP offer
        elif packet.dhcp.option_value == "02":
            try:
                if "ip_server" in fieldnames:
                    dhcpserver=packet.dhcp.ip_server
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    offeredip=packet.dhcp.ip_your
                else:
                    offeredip="Unknown"
                if "option_subnet_mask" in fieldnames:
                    subnetmask=packet.dhcp.option_subnet_mask
                else:
                    subnetmask="Unknown"
                if "option_ip_address_lease_time" in fieldnames:
                    leasetime=packet.dhcp.option_ip_address_lease_time
                else:
                    leasetime="Unknown"
                if "option_router" in fieldnames:
                    router=packet.dhcp.option_router
                else:
                    router="Unknown"
                if "option_domain_name_server" in fieldnames:
                    nameserver=packet.dhcp.option_domain_name_server
                else:
                    nameserver="Unknown"
                if "option_domain_name" in fieldnames:
                    domainname=packet.dhcp.option_domain_name
                else:
                    domainname="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","") 
                else:
                    macaddress="000000000000"
                if domainname!="Unknown" and nameserver!="Unknown" and router!="Unknown" and leasetime!="Unknown" and offeredip!="Unknown" and dhcpserver!="Unknown":
                    if not macaddress.startswith("204c03"):
                        information="DHCP Server " + dhcpserver + " offered " + offeredip
                        options="Subnet mask: " + subnetmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + nameserver + ", domain: " + domainname
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Offer','{}','{}')".format(packet.sniff_timestamp,information,options)
                        cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP offer packet in packet")
        # Match DHCP request
        elif packet.dhcp.option_value == "03":
            try:
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","") 
                else:
                    macaddress="000000000000"
                if "option_requested_ip_address" in fieldnames:
                    requestedip=packet.dhcp.option_requested_ip_address
                else:
                    requestedip="Unknown"
                if not macaddress.startswith("204c03"):
                    information="Host " + macaddress + " requested " + requestedip
                    options=""
                    if macaddress!="000000000000" and requestedip!="Unknown":
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(packet.sniff_timestamp,information,options)
                        cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP request in packet")
        # Match DHCP ack
        elif packet.dhcp.option_value == "05":
            try:
                if "option_subnet_mask" in fieldnames:
                    netmask=packet.dhcp.option_subnet_mask
                else:
                    netmask="Unknown"
                if "option_ip_address_lease_time" in fieldnames:
                    leasetime=packet.dhcp.option_ip_address_lease_time
                else:
                    leasetime="Unknown"
                if "option_router" in fieldnames:
                    router=packet.dhcp.option_router
                else:
                    router="Unknown"
                if "option_domain_name_server" in fieldnames:
                    dnsserver=packet.dhcp.option_domain_name_server
                else:
                    dnsserver="Unknown"
                if "option_dhcp_server_id" in fieldnames:
                    dhcpserver=packet.dhcp.option_dhcp_server_id
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    clientip=packet.dhcp.ip_your
                else:
                    clientip="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","")                 
                else:
                    macaddress="000000000000"
                # The listener class is also used for ZTP. Goal is to have the switch keep it's DHCP IP address.
                try:
                    if macaddress!="000000000000" and clientip!="Unknown" and netmask!="Unknown" and router!="Unknown":
                        ztpnetmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
                        queryStr="select * from ztpdevices where macaddress='{}'".format(macaddress)
                        cursor.execute(queryStr)
                        result=cursor.fetchall()
                        if result:
                            # We found a ZTP device entry and need to update the IP address information, but only if DHCP ZTP is enabled
                            if result[0]['ztpdhcp']==1:
                                queryStr="update ztpdevices set ipaddress='{}', netmask='{}', gateway='{}' where id='{}'".format(clientip,ztpnetmask,router,result[0]['id'])
                                cursor.execute(queryStr)
                                logEntry="{}: {} Updated ZTP Device with MAC Address {}: {}\n".format(bord,datetime.now(),macaddress, clientip)
                                listenerlog.write(logEntry)
                except:
                    print("Cannot analyze ZTP packet")
                if not macaddress.startswith("204c03"):
                    information="DHCP Server " + dhcpserver + " acknowledged " + clientip                         
                    options="Subnet_mask: " + netmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + dnsserver
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Ack','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP ack packet")

        # Match DHCP NAK
        elif packet.dhcp.option_value == "06":
            try:
                if "option_dhcp_server_id" in fieldnames:
                    dhcpserver=packet.dhcp.option_dhcp_server_id
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    ip_your=packet.dhcp.ip_your
                else:
                    ip_your="Unknown"
                if "ip_client" in fieldnames:
                    clientip=packet.dhcp.ip_client
                else:
                    clientip="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","")                 
                else:
                    macaddress="000000000000"
                if "option_message" in fieldnames:
                    optionmessage=packet.dhcp.option_message
                else:
                    optionmessage="Unknown"
                if not macaddress.startswith("204c03"):
                    information="DHCP NAK: " + optionmessage + ". " + ip_your + "  not available on " + dhcpserver
                    options="IP client: " + clientip + ", MAC address: " + macaddress
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP NAK','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP NAK packet")
        # Match DHCP release
        elif packet.dhcp.option_value == "07":
            try:
                if "option_dhcp_server_id" in fieldnames:
                    dhcpserver=packet.dhcp.option_dhcp_server_id
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    ip_your=packet.dhcp.ip_your
                else:
                    ip_your="Unknown"
                if "ip_client" in fieldnames:
                    clientip=packet.dhcp.ip_client
                else:
                    clientip="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if "option_hostname" in fieldnames:
                    hostname=packet.dhcp.option_hostname
                else:
                    hostname="Unknown"
                if not macaddress.startswith("204c03"):
                    information="DHCP Server " + dhcpserver + "  released " + ip_your
                    options="IP client: " + clientip + ", MAC address: " + macaddress + ", Hostname: " + hostname
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Release','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP release packet")
        # Match DHCP inform
        elif packet.dhcp.option_value == "08":
            try:    
                information="DHCP Inform from " + packet.ip.src + " (" + packet.eth.src + ") Hostname: " + packet.dhcp.option_hostname + ", Vendor Class ID: " + packet.dhcp.option_vendor_class_id
                options=""
                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Inform','{}','{}')".format(packet.sniff_timestamp,information,options)
                cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP Inform packet")
    else:
        # Match bootp discover
        if packet.bootp.option_value == "01":
            try:
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.bootp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if not macaddress.startswith("204c03"):
                    information="Host " + macaddress + " asked for an IP address"
                    options=""
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Discover','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP discover packet")
        # Match bootp offer
        elif packet.bootp.option_value == "02":
            try:
                if "ip_server" in fieldnames:
                    dhcpserver=packet.bootp.ip_server
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    offeredip=packet.bootp.ip_your
                else:
                    offeredip="Unknown"
                if "option_subnet_mask" in fieldnames:
                    subnetmask=packet.bootp.option_subnet_mask
                else:
                    subnetmask="Unknown"
                if "option_ip_address_lease_time" in fieldnames:
                    leasetime=packet.bootp.option_ip_address_lease_time
                else:
                    leasetime="Unknown"
                if "option_router" in fieldnames:
                    router=packet.bootp.option_router
                else:
                    router="Unknown"
                if "option_domain_name_server" in fieldnames:
                    nameserver=packet.bootp.option_domain_name_server
                else:
                    nameserver="Unknown"
                if "option_domain_name" in fieldnames:
                    domainname=packet.bootp.option_domain_name
                else:
                    domainname="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.bootp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if domainname!="Unknown" and nameserver!="Unknown" and router!="Unknown" and leasetime!="Unknown" and offeredip!="Unknown" and dhcpserver!="Unknown":
                    if not macaddress.startswith("204c03"):
                        information="DHCP Server " + dhcpserver + " offered " + offeredip
                        options="Subnet mask: " + subnetmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + nameserver + ", domain: " + domainname
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Offer','{}','{}')".format(packet.sniff_timestamp,information,options)
                        cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP offer packet in packet")
        # Match bootp request
        elif packet.bootp.option_value == "03":
            try:
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if "option_requested_ip_address" in fieldnames:
                    requestedip=packet.bootp.option_requested_ip_address
                else:
                    requestedip="Unknown"
                if not macaddress.startswith("204c03"):
                    information="Host " + macaddress + " requested " + requestedip
                    options=""
                    if macaddress!="000000000000" and requestedip!="Unknown":
                        queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Request','{}','{}')".format(packet.sniff_timestamp,information,options)
                        cursor.execute(queryStr)
            except:
                print("Could not analyze bootp request in packet")
        # Match bootp ack
        elif packet.bootp.option_value == "05":  
            try:
                if "option_subnet_mask" in fieldnames:
                    netmask=packet.bootp.option_subnet_mask
                else:
                    netmask="Unknown"
                if "option_ip_address_lease_time" in fieldnames:
                    leasetime=packet.bootp.option_ip_address_lease_time
                else:
                    leasetime="Unknown"
                if "option_router" in fieldnames:
                    router=packet.bootp.option_router
                else:
                    router="Unknown"
                if "option_domain_name_server" in fieldnames:
                    dnsserver=packet.bootp.option_domain_name_server
                else:
                    dnsserver="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.bootp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                # The listener class is also used for ZTP. Goal is to have the switch keep it's DHCP IP address. 
                try:
                    if "hw_mac_addr" in fieldnames and "ip_your" in fieldnames and netmask!="Unknown" and router!="Unknown":
                        ztpnetmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
                        queryStr="select * from ztpdevices where macaddress='{}'".format(ztpmacaddress)
                        cursor.execute(queryStr)
                        result=cursor.fetchall()
                        if result:
                            # We found a ZTP device entry and need to update the IP address information, but only if DHCP ZTP is enabled
                            if result[0]['ztpdhcp']==1:
                                queryStr="update ztpdevices set ipaddress='{}', netmask='{}', gateway='{}' where id='{}'".format(packet.bootp.ip_your,ztpnetmask,router,result[0]['id'])
                                cursor.execute(queryStr)
                                listenerlog.write('{}: Updated ZTP Device with MAC Address {}: {}\n'.format(datetime.now(),ztpmacaddress, clientip))
                except:
                    print("Cannot analyze ZTP packet")
                if not macaddress.startswith("204c03"):
                    information="DHCP Server " + packet.bootp.option_dhcp_server_id + " acknowledged " + packet.bootp.ip_your
                    options="Subnet_mask: " + netmask + ", Lease time: " + leasetime + ", Router: " + router + ", Name Server: " + dnsserver
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Ack','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP ack packet")
        # Match bootp NAK
        elif packet.bootp.option_value == "06":
            try:
                if "option_dhcp_server_id" in fieldnames:
                    dhcpserver=packet.bootp.option_dhcp_server_id
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    ip_your=packet.bootp.ip_your
                else:
                    ip_your="Unknown"
                if "ip_client" in fieldnames:
                    clientip=packet.bootp.ip_client
                else:
                    clientip="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.bootp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if "option_message" in fieldnames:
                    optionmessage=packet.bootp.option_message
                else:
                    optionmessage="Unknown"
                if not macaddress.startswith("204c03"):
                    information="DHCP NAK: " + optionmessage + ". " + ip_your + "  not available on " + dhcpserver
                    options="IP client: " + clientip + ", MAC address: " + macaddress
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP NAK','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze bootp NAK packet")
        # Match bootp release
        elif packet.bootp.option_value == "07":
            try:
                if "option_dhcp_server_id" in fieldnames:
                    dhcpserver=packet.bootp.option_dhcp_server_id
                else:
                    dhcpserver="Unknown"
                if "ip_your" in fieldnames:
                    ip_your=packet.bootp.ip_your
                else:
                    ip_your="Unknown"
                if "ip_client" in fieldnames:
                    clientip=packet.bootp.ip_client
                else:
                    clientip="Unknown"
                if "hw_mac_addr" in fieldnames:
                    macaddress=packet.dhcp.hw_mac_addr
                    macaddress=macaddress.replace(":","")  
                else:
                    macaddress="000000000000"
                if "option_hostname" in fieldnames:
                    hostname=packet.bootp.option_hostname
                else:
                    hostname="Unknown"
                if not macaddress.startswith("204c03"):
                    information="DHCP Server " + dhcpserver + "  released " + ip_your
                    options="IP client: " + clientip + ", MAC address: " + macaddress + ", Hostname: " + hostname
                    queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Release','{}','{}')".format(packet.sniff_timestamp,information,options)
                    cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP release packet")
        # Match DHCP inform
        elif packet.bootp.option_value == "08":
            try:
                information="DHCP Inform from " + packet.ip.src + " (" + packet.eth.src + ") Hostname: " + packet.bootp.option_hostname + ", Vendor Class ID: " + packet.bootp.option_vendor_class_id
                options=""
                queryStr="insert into dhcptracker (utctime,dhcptype,information,options) values ('{}','DHCP Inform','{}','{}')".format(packet.sniff_timestamp,information,options)
                cursor.execute(queryStr)
            except:
                print("Could not analyze DHCP Inform packet")

def analyzeSNMP(packet,cursor):
    # print("Analyze SNMP packet")
    fieldnames=list(packet.snmp.field_names)
    try:
        generictraps=['Cold start','Warm start','Link down','Link up','Authentication failure','EGP Neighbor loss']
        snmpversions=['V1', 'V2c']
        if "generic_trap" in fieldnames:
            if packet.snmp.generic_trap=="6":
                # This is an enterprise trap. Need to analyze a bit further
                trapMessage="Enterprise trap"
            else:
                trapMessage=generictraps[int(packet.snmp.generic_trap)]
                trapMessage=trapMessage.replace("'","\\'")
        else:
            trapMessage=""
            if "version" in fieldnames:
                snmpversion=snmpversions[int(packet.snmp.version)]
            else:
                snmpversion="Unknown"
            if trapMessage!="":
                queryStr="insert into snmptracker (utctime,source,version,community,information) values ('{}','{}','{}','{}','{}')".format(packet.sniff_timestamp,packet.ip.src_host,snmpversion,packet.snmp.community,trapMessage)
                cursor.execute(queryStr)
    except:
        print("Could not analyze SNMP packet")

def analyzeSyslog(packet,cursor,syslogFacilities, syslogSeverity):
    # print("Analyze Syslog packet")
    try:
        message=str(packet.syslog.msg)
        message=message.replace("'","\\'")
        queryStr="insert into syslog (utctime,source,facility,severity,information) values ('{}','{}','{}','{}','{}')".format(packet.sniff_timestamp,packet.ip.src_host,syslogFacilities[int(packet.syslog.facility)],syslogSeverity[int(packet.syslog.level)],message)
        cursor.execute(queryStr)
    except:
        print("Could not analyze Syslog packet {}")


def filter_udp_traffic_file(packet,listenerlog,cursor,syslogFacilities,syslogSeverity):
    if hasattr(packet, 'udp'):
        if packet.udp.dstport=="67" or packet.udp.dstport=="68":
            print("Analyze DHCP Packet")
            analyzeDHCP(packet,listenerlog,cursor)
        elif packet.udp.dstport=="161":
            analyzeSNMP(packet,cursor)
        elif packet.udp.dstport=="514":
            analyzeSyslog(packet,cursor,syslogFacilities, syslogSeverity)
        elif packet.udp.dstport=="47":
            print("Analyze GRE packet")

capture_live_packets(activeInterface,listenerlog,cursor,syslogFacilities,syslogSeverity)
