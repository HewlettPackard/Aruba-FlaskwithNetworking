# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#/usr/bin/python3

from datetime import datetime, time, timedelta
import time
import socket
import subprocess
from paramiko.client import SSHClient, AutoAddPolicy
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
import ipaddress

sessionid = requests.Session()

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def ztpupdate():
    # Obtain the active IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    hostip=s.getsockname()[0]
    '''
    EnableZTP status defines the status of the ZTP process
    0 = disabled
    STAGE 1: Initial ZTP configuration push through DHCP
    STAGE 2: Check software version and upgrade if needed. If not needed, go to stage 3. If needed go to stage 21
    STAGE 21: Switch is upgrading. Once upgraded, go to stage 22
    STAGE 22: VSF member rebooted. Check whether VSF member is back online. If back online go to stage 24
    STAGE 23: VSF master rebooted. Check if VSF master is back online. If back online go to stage 4 for VSF configuration
    STAGE 24: For the VSF Member. VSF Member is back online. Only go to stage 4 (VSF configuration) if the master is back online
    STAGE 28: Stand alone switch has been upgraded and is rebooting. Check when switch is back online, if back online go to stage 6
    STAGE 3: Check if this is a VSF enabled switch. If switch is VSF, go to stage 4, else go to stage 6
    STAGE 4: It is a VSF switch, provision the VSF links and renumber the member switches. Check if it is Master or member. If switch is master go to stage 5, if member switch go to stage 41
    STAGE 41: Check is VSF member is secondary. If secondary, wait until VSF is complete, then designate secondary, if not secondary ZTP completed (stage 100)
    STAGE 42: Wait until the secondary is back online. If back online, set to completed (stage 100)
    STAGE 5: If VSF on master is successful, check whether all VSF members have joined. If not, loop in this stage. If VSF is completed, go to stage 6
    STAGE 6: Provision configuration to the switch
    STAGE 8: There is already an initial configuration on the switch
    STAGE 9: Once the configuration is pushed, verify whether the administrative account works
    STAGE 91: The administrative account works. Remove the initial ZTP user and save the running configuration to the startup configuration
    100 = Successfully pushed the configuration template
    '''
    ztplog = open('/var/www/html/log/ztp.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    globalconf=obtainGlobalconf(cursor)
    # Obtain device information from which ztp has been enabled
    queryStr="select * from ztpdevices where enableztp>0 and enableztp<99"
    deviceResult=cursor.execute(queryStr)
    deviceResult = cursor.fetchall()
    for items in deviceResult:
        # Define the initial username that is used for the REST calls. This username is configured in the initial config that is pushed through TFTP
        username="admin"
        password="ztpinit"
        if items['enableztp']==1:
            # STAGE 1: INITIAL ZTP CONFIGURATION PUSH THROUGH DHCP OPTIONS
            print("STAGE 1: INITIAL ZTP CONFIGURATION PUSH THROUGH DHCP OPTIONS FOR {}".format(items['ipaddress']))
            logEntry(items['id'],"Stage 1: Provision initial configuration for {}".format(items['name']),cursor)
            try:
                url="system?attributes=ztp"
                response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
                if response['ztp']['state']=="success":
                    ztpstatus=response['ztp']['configuration_file'] + " successful download from " + response['ztp']['tftp_server']
                    queryStr="update ztpdevices set vrf='{}', enableztp=2, ztpstatus='{}' where id='{}'".format(response['ztp']['vrf'],ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 1: Initial template downloaded successful", cursor)
                    ztplog.write('{}: Stage 1: Initial template downloaded successfully to {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                elif response['ztp']['failure_reason']=="non_default_startup_config" and  response['ztp']['state']=="aborted":
                    ztpstatus="Initial configuration is present"
                    queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 1: Initial configuration for {} already exists".format(items['name']),cursor)
                    ztplog.write('{}: Stage 1: Initial configuration for {} ({}) already exists. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            except:
                logEntry(items['id'],"Stage 1: Provision initial configuration for {}".format(items['name']),cursor)
                ztplog.write('{}: Stage 1: Provision initial configuration for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                pass
        # The initial configuration file has been successfully downloaded and saved to the startup-configuration. We now need to check whether the device requires a software upgrade
        elif items['enableztp']==2:
            # STAGE 2: SOFTWARE UPGRADE
            print("STAGE 2: SOFTWARE UPGRADE")
            # We have to check whether the switch is a VSF member, if this is the case, we need to get the required software version from the master switch entry
            softwareimage=""
            if (items['vsfenabled']==1 and items['vsfmaster']!=0):
                queryStr="select softwareimage from ztpdevices where id='{}'".format(items['vsfmaster'])
                cursor.execute(queryStr)
                softwareimage=cursor.fetchall()
                softwareimage=softwareimage[0]['softwareimage']
            elif items['softwareimage']!=0:
                softwareimage=items['softwareimage']
            if softwareimage:
                logEntry(items['id'],"Stage 2: There is a software image configured for this device", cursor)
                ztplog.write('{}: Stage 2: There is a software image configured for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
                # Only continue if there is a response. If there is no response, the switch might be offline
                if response:
                    # Obtain the image file name
                    queryStr="select filename from deviceimages where id='{}'".format(softwareimage)
                    cursor.execute(queryStr)
                    imageResult=cursor.fetchall()
                    # Formating the image name so that we can compare with the information from the rest call
                    imagename=getplatformName(items['ipaddress'],username,password,imageResult[0]['filename'], globalconf)
                    if imagename==response['current_version']:
                        # There is no need to upgrade the switch. Switch is already running on the right software
                        logEntry(items['id'],"Stage 2: {} already on the right software".format(items['ipaddress']), cursor)
                        ztplog.write('{}: Stage 2: {} ({}) is already on the right software. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                        ztpstatus="Switch running on " + imagename + ". Verify VSF configuration"
                        queryStr="update ztpdevices set enableztp=3, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                    else:
                        # Switch is not running on the right software, we need to upgrade
                        if items['ztpdhcp']==1 or items['vrf']=="0":
                            vrf=checkVRF(items['ipaddress'],username,password, globalconf)
                        else:
                            vrf=items['vrf']
                        if vrf!="":
                            url="firmware?image=primary&from=http://" + hostip + "/images/" + imageResult[0]['filename'] + "&vrf=" + vrf
                            response=putRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                            if response==200:
                                ztpstatus="Upgrade switch to " + imagename
                                queryStr="update ztpdevices set enableztp=21, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry (items['id'],"Stage 2: Upgrade the switch to {}".format(imagename), cursor)
                                ztplog.write('{}: Stage 2: Upgrade {} ({}) to {}. \n'.format(datetime.now(),imagename,items['ipaddress'],items['name']))
                        else:
                            # Switch is not reachable
                                ztpstatus="Switch is not reachable"
                                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry (items['id'],"Stage 2: Switch is not reachable", cursor)
                                ztplog.write('{}: Stage 2: {} ({}) is not reachable. \n'.format(datetime.now(),items['ipaddress'],items['name']))

            else:
                # There is no image attached to the device. No need to upgrade. Next stage is to verify whether switch operates in VSF or standalone (stage 3)
                logEntry (items['id'],"Stage 2: There is no software image attached. Verify VSF configuration", cursor)
                ztplog.write('{}: Stage 2: No software update required for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                ztpstatus="Verify VSF configuration"
                queryStr="update ztpdevices set enableztp=3, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==21:
            # STAGE 21: SWITCH IS UPGRADING. CHECK STATUS
            print("STAGE 21: {} IS UPGRADING. CHECK STATUS".format(items['ipaddress']))
            logEntry(items['id'],"Stage 21: {} is upgrading, checking the status".format(items['ipaddress']), cursor)
            # ztplog.write('{}: Stage 21: {} ({}) is upgrading, checking status. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            if response:
                if response['status']=="success":
                    # Another check to see whether the image has been pushed to the primary partition. If it has not been pushed, we have to re-issue the upload command
                    url="firmware"
                    response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
                    # The response content should contain the primary version information that is the updated image
                    # Obtain the image file name
                    if (items['vsfenabled']==1 and items['vsfmaster']!=0):
                        queryStr="select softwareimage from ztpdevices where id='{}'".format(items['vsfmaster'])
                        cursor.execute(queryStr)
                        softwareimage=cursor.fetchall()
                        softwareimage=softwareimage[0]['softwareimage']
                    elif items['softwareimage']!=0:
                        softwareimage=items['softwareimage']
                    queryStr="select filename from deviceimages where id='{}'".format(softwareimage)
                    cursor.execute(queryStr)
                    imageResult=cursor.fetchall()
                    # Formating the image name so that we can compare with the information from the rest call
                    # Each platform has it's own prepend code. For 6300, it's FL, for 8320 it's TL, for 8325 it's GL. We need to make sure that the image name variable is set correctly
                    # in order to be able to verify
                    url="system?attributes=platform_name"
                    imagename=getplatformName(items['ipaddress'],username,password,imageResult[0]['filename'], globalconf)
                    if response['primary_version']:
                        if imagename==response['primary_version']:
                            # upgrade is successful to the primary image. We now have to reboot the switch on the primary image
                            # CAREFUL: IF THIS IS VSF, WE HAVE TO MAKE SURE THAT THE MASTER SWITCH DOES NOT REBOOT UNTIL ALL MEMBERS HAVE BEEN UPGRADED
                            if items['vsfenabled']==1:
                                # Dealing with a VSF. Make sure that the master only reboots after all VSF members have been upgraded successfully
                                # This is easy to check because all the member switches should have the enableztp variable set to 3
                                # If it is a member switch, go ahead and reboot
                                if items['vsfmaster']!=0:
                                    # This is a member switch
                                    url="boot?image=primary"
                                    response=postRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                                    ztpstatus="Upgrade successful, preparing for reboot"
                                    queryStr="update ztpdevices set enableztp=22, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                    cursor.execute(queryStr)
                                    logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
                                    ztplog.write('{}: Stage 21: {} ({}) has been upgraded to {}. Rebooting... \n'.format(datetime.now(),items['ipaddress'],items['name'], imagename))
                                else:   
                                    # This is the master switch
                                    queryStr="select enableztp from ztpdevices where vsfmaster='{}'".format(items['id'])
                                    cursor.execute(queryStr)
                                    upgradeStatus=cursor.fetchall()
                                    goodtoBoot=1
                                    for statusItems in upgradeStatus:
                                        if statusItems['enableztp']!=24:
                                            goodtoBoot=0
                                            logEntry(items['id'],"Stage 21: Waiting for the member switches to be online", cursor)
                                            ztpstatus="Waiting for the member switches to be online"
                                            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                            cursor.execute(queryStr)
                                    if goodtoBoot==1:
                                        # All the VSF members have been upgraded and are back online
                                        url="boot?image=primary"
                                        response=postRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                                        ztpstatus="Upgrade successful, rebooting the switch"
                                        queryStr="update ztpdevices set enableztp=23, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        cursor.execute(queryStr)
                                        logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
                                        ztplog.write('{}: Stage 21: {} ({}) has been upgraded to {}. Rebooting... \n'.format(datetime.now(),items['ipaddress'],items['name'], imagename))
                            else: 
                                # It's not a VSF, so we can reboot the switch straight away
                                url="boot?image=primary"
                                response=postRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                                ztpstatus="Upgrade successful, preparing for reboot"
                                queryStr="update ztpdevices set enableztp=28, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
                                ztplog.write('{}: Stage 21: {} ({}) has been upgraded to {}. Rebooting... \n'.format(datetime.now(),items['ipaddress'],items['name'], imagename))
                        else:
                            pass           
                elif response['status']=="in_progress":
                    ztpstatus="Upgrade in progress"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                elif response['status']=="failure" or response['status']=="none":
                    ztpstatus="Failed to upgrade switch, retrying.."
                    queryStr="update ztpdevices set enableztp=2, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 21: Failed to upgrade {}, retrying..".format(items['ipaddress']), cursor)
                    ztplog.write('{}: Stage 21: {} ({}) failed to upgrade to {}. Retrying... \n'.format(datetime.now(),items['ipaddress'],items['name'], imagename))
        elif items['enableztp']==22:
            #STAGE 22: VSF MEMBER REBOOTED. CHECK WHETHER VSF MEMBER IS BACK ONLINE
            url="firmware"
            response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            if not bool(response):
                # VSF Member is not online yet. Loop this stage
                ztpstatus="VSF member switch is starting up"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            else:
                # VSF member is back online. Only go to stage 4 (provision VSF), when the master is also back online (master switch should be set to stage 4)
                queryStr="select softwareimage from ztpdevices where id='{}'".format(items['vsfmaster'])
                cursor.execute(queryStr)
                softwareimage=cursor.fetchall()
                softwareimage=softwareimage[0]['softwareimage']
                queryStr="select filename from deviceimages where id='{}'".format(softwareimage)
                cursor.execute(queryStr)
                imageResult=cursor.fetchall()
                # Formating the image name so that we can compare with the information from the rest call
                imagename=getplatformName(items['ipaddress'],username,password,imageResult[0]['filename'], globalconf)
                if response:
                    if imagename!=response['current_version']:
                        # Software is not on the right level yet. Stay in this stage
                        pass
                    else:
                        ztpstatus="Member switch is back online"
                        queryStr="update ztpdevices set enableztp=24, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                        logEntry(items['id'],"Stage 22: Member is back online", cursor)
                        ztplog.write('{}: Stage 2: {} ({}) member switch is back online. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==23:
            # STAGE 23: VSF MASTER REBOOTED. CHECK WHETHER VSF MASTER IS BACK ONLINE. IF BACK ONLINE, GOTO STAGE 4 FOR THE VSF CONFIGURATION
            queryStr="select filename from deviceimages where id='{}'".format(items['softwareimage'])
            cursor.execute(queryStr)
            imageResult=cursor.fetchall()
            # Formating the image name so that we can compare with the information from the rest call
            imagename=getplatformName(items['ipaddress'],username,password,imageResult[0]['filename'], globalconf)
            url="firmware"
            response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            if not bool(response):
                # VSF Master is not online yet. Loop this stage
                ztpstatus="VSF master switch is starting up"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            elif response['current_version']==imagename:
                # Master switch is back online and on the right software Go to stage 4
                ztpstatus="Switch is back online"
                queryStr="update ztpdevices set enableztp=4, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 23: Switch is back online. Provision VSF to the master switch", cursor)
                ztplog.write('{}: Stage 23: {} ({}) Master switch is back online. Provision VSF. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==24:
            # STAGE 24: VSF MEMBER IS BACK ONLINE. ONLY PROVISION VSF WHEN THE MASTER IS BACK ONLINE (stage 4)
            ztpstatus="Member switch is back online. Check if master is online"
            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
            cursor.execute(queryStr)
            queryStr="select enableztp from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            masterStatus=cursor.fetchall()
            if masterStatus[0]['enableztp']==4:
                # The master is back online, members can be provisioned for VSF
                ztpstatus="Master switch is back online"
                queryStr="update ztpdevices set enableztp=4, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 22: Master Switch is back online. Provision VSF to the member switch", cursor)
                ztplog.write('{}: Stage 22: {} ({}) master switch is back online. Provision VSF to the member switch. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            else:
                # Master switch is not back online yet
                # The master is back online, members can be provisioned for VSF
                ztpstatus="Waiting for master switch to come online"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==28:
            # STAGE 28: STANDALONE SWITCH HAS BEEN UPGRADED AND IS REBOOTING
            logEntry(items['id'],"Stage 28: {} is rebooting".format(items['ipaddress']), cursor)
            ztplog.write('{}: Stage 28: {} ({}) is rebooting. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            if not bool(response):
                # Standalone switch not online yet. Loop this stage
                ztpstatus="Rebooting switch"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            else:
                # Standalone switch is (back) online
                # Check if the switch is running on the right software. If not, keep in this loop. 
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
                # The response content should contain the primary version information that is the updated image
                # Obtain the image file name
                if (items['vsfenabled']==1 and items['vsfmaster']!=0):
                    queryStr="select softwareimage from ztpdevices where id='{}'".format(items['vsfmaster'])
                    cursor.execute(queryStr)
                    softwareimage=cursor.fetchall()
                    softwareimage=softwareimage[0]['softwareimage']
                elif items['softwareimage']!=0:
                    softwareimage=items['softwareimage']
                queryStr="select filename from deviceimages where id='{}'".format(softwareimage)
                cursor.execute(queryStr)
                imageResult=cursor.fetchall()
                # Formating the image name so that we can compare with the information from the rest call

                imagename=getplatformName(items['ipaddress'],username,password, imageResult[0]['filename'], globalconf)
                if response['primary_version']:
                    if imagename!=response['current_version']:
                        # Software is not on the right level yet. Stay in this stage
                        pass
                    else:
                        # go to configuration provisioning stage
                        ztpstatus="Upgrade successful, provision configuration"
                        queryStr="update ztpdevices set enableztp=6, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                        logEntry(items['id'],"Stage 28: Upgrade has been successful, provision configuration", cursor)
                        ztplog.write('{}: Stage 28: Upgrade of {} ({}) has been successful, provision configuration. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==3:
            # STAGE 3: CHECK WHETHER VSF IS CONFIGURED. IF YES, GOTO STAGE 4 (PROVISION VSF), IF NOT, GOTO STAGE 6 (PROVISION CONFIGURATION)
            # This stage runs if there was no software image attached
            if items['vsfenabled']==1:
                ztpstatus="Switch is configured for VSF"
                queryStr="update ztpdevices set enableztp=4, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            else:
                ztpstatus="Provision stand alone switch configuration"
                queryStr="update ztpdevices set enableztp=6, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==4:
            # STAGE 4: VSF CONFIGURATION REQUIRED.
            # We have to push the ID and VSF port information to the switch. At the moment this can only be done through SSH.
            try:
                client=SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy)
                client.connect(items['ipaddress'],username=username,password=password, timeout=5)
                # Logging in could take some time. Pause a bit
                connection=client.invoke_shell()
                connection.send("\n")
                time.sleep(10)
                connection.send("configure terminal\n")
                time.sleep(3)
                logEntry(items['id'],"Stage 4: Configure the VSF ports", cursor)
                ztplog.write('{}: Stage 4: Configure VSF ports for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                if items['vsfmember']==0:
                    vsfmember="1"
                else:
                    vsfmember=items['vsfmember']
                ztpstatus="Configure the VSF ports on member {}".format(vsfmember)
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                try:
                    connection.send("vsf member 1\n")
                    time.sleep(3)
                    link1=json.loads(items['link1'])
                    link2=json.loads(items['link2']) 
                    if items['link1']:
                        if len(link1)>0:
                            link1Cmd="link 1 "
                            for l1Items in link1:
                                link1Cmd+=unquote(l1Items) +","
                            link1Cmd=link1Cmd[:-1]+" \n"
                            connection.send(link1Cmd)
                            time.sleep(3)
                    if items['link2']:
                        if len(link2)>0:
                            link2Cmd="link 2 "
                            for l2Items in link2:
                                link2Cmd+=unquote(l2Items) +","
                            link2Cmd=link2Cmd[:-1]+" \n"
                            connection.send(link2Cmd)
                            time.sleep(3)
                except:
                    pass
                # IF THE SWITCH IS NOT MASTER, WE HAVE TO RENUMBER THE SWITCH
                if items['vsfmaster']!=0:
                    logEntry(items['id'],"Stage 4: Renumber the VSF member", cursor)
                    ztplog.write('{}: Stage 4: Renumber VSF member switch {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                    ztpstatus="Renumber the VSF switch to {}".format(items['vsfmember'])
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    renumberCmd="vsf renumber-to " + str(items['vsfmember']) + "\n"
                    connection.send(renumberCmd)
                    time.sleep(4)
                    connection.send('y\n')
                    time.sleep(5)
                    output = connection.recv(65532).decode(encoding='utf-8')
                    try:
                        connection.close()
                        client.close()
                    except:
                        pass
                    # If the output contains 'transaction success', VSF is provisioned
                    # Setting the ZTP status to , this is a substage, waiting until the switch comes back. When the switch is back online, we need to verify the VSF status and optionally configure for secondary
                    if "transaction success" in output:
                        logEntry(items['id'],"Stage 4: VSF has been deployed to the member switch, rebooting switch", cursor)
                        ztplog.write('{}: Stage 4: VSF has been deployed to member switch {} ({}), rebooting the switch. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                        ztpstatus="VSF has been deployed to the member switch, rebooting switch"
                        queryStr="update ztpdevices set enableztp=41, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                # SWITCH IS MASTER
                else:
                    # We need to doublecheck whether VSF has been deployed to the master switch by checking the VSF link before going to stage 5
                    url="system/vsf_members/1/links"
                    checkVSF=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
                    if checkVSF:
                        # We can go into the next stage, which is for the master switch to wait until all members have joined the stack
                        logEntry(items['id'],"Stage 4: VSF has been deployed to the master switch. Waiting for member switches", cursor)
                        ztplog.write('{}: Stage 4: VSF has been deployed to master switch {} ({}). Waiting for all member switches to be back online. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                        ztpstatus="VSF has been deployed. Waiting for member switches"
                        queryStr="update ztpdevices set enableztp=5, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                    else:
                        # There is no VSF link on the master switch, repeat VSF configuration
                        pass
                    try:
                        connection.close()
                        client.close()
                    except:
                        pass

            except:
                # First, get the VSF topology from the master
                if items['vsfmaster']!=0:
                     queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
                     cursor.execute(queryStr)
                     vsfmasterResult=cursor.fetchall()
                     url="system/vsf_members?attributes=id%2Crole%2Cstatus&depth=2"
                     roleResponse=getRESTcxIP(vsfmasterResult[0]['ipaddress'],username,password,url, globalconf)
                     # Now check if the VSF member exists in the VSF and status is ready
                     if len(roleResponse)>1:
                        memberInfo=next(item for item in roleResponse if item["id"] == items['vsfmember'])
                        if memberInfo['id']==items['vsfmember'] and memberInfo['status']=="ready":
                            logEntry(items['id'],"Stage 4: VSF has been deployed to the member switch", cursor)
                            ztplog.write('{}: Stage 4: VSF has been deployed to member switch {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                            ztpstatus="VSF has been deployed to the member switch"
                            queryStr="update ztpdevices set enableztp=41, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr)
        elif items['enableztp']==41:
            # CHECK WHETHER VSF MEMBER IS CONFIGURED TO BE SECONDARY
            print("STAGE 41: CHECK WHETHER {} IS CONFIGURED TO BE VSF SECONDARY".format(items['ipaddress']))
            # First check is to verify whether the member is back online and whether it has joined the stack.
            # If it has joined the stack, check whether the member is designated secondary. If not, set the ZTP to completed (stage 100)
            # If member is designated secondary, set the secondary member on the master switch
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            vsfmasterResult=cursor.fetchall()
            url="system/vsf_members?attributes=id%2Crole%2Cstatus&depth=2"
            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],"ztpuser",globalconf['ztppassword'],url, globalconf)
            if items['vsfrole']=="Secondary":
                # Additional check is to verify whether the secondary switch member id exists in the VSF. If it does, we can assign the secondary role to the member switch
                # We should only push the secondary role to the master switch when the master switch has been completed and the VSF is ready (stage 61)
                if vsfmasterResult[0]['enableztp']==61:
                    # At the moment there is no API call for configuring the secondary role, therefore we have to set this using SSH. And for this we need to login to the master switch
                    try:
                        client=SSHClient()
                        client.set_missing_host_key_policy(AutoAddPolicy)
                        client.connect(vsfmasterResult[0]['ipaddress'],username="ztpuser",password=globalconf['ztppassword'])
                        connection=client.invoke_shell()
                        connection.send("\n")
                        time.sleep(1)
                        connection.send("configure terminal\n")
                        time.sleep(1)
                        vsfCmd="vsf secondary-member " + str(items['vsfmember']) + "\n"
                        connection.send(vsfCmd)
                        time.sleep(4)
                        output = connection.recv(65532).decode(encoding='utf-8')
                        # If the output is empty, the secondary switch has already been configured
                        if "save the configuration" in output:
                            ztpstatus="Member is designated secondary switch"
                            queryStr="update ztpdevices set enableztp=42, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr)
                            logEntry(vsfmasterResult[0]['id'],"Stage 41: Configured the secondary member", cursor)
                            ztplog.write('{}: Stage 41: {} ({}) has been configured as secondary member. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                            connection.send('y\n')
                            time.sleep(3)
                            connection.close()
                            client.close()  
                        else:
                            # Secondary is already configured. Now check the VSF status again. If the member is up and running again, we can set the status to completed
                            url="system/vsf_members/"+str(items['vsfmember'])
                            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],"ztpuser",globalconf['ztppassword'],url, globalconf)
                            if response['status']=="ready":
                                # It is done. The member switch has been provisioned
                                ztpstatus="ZTP has been completed"
                                queryStr="update ztpdevices set ipaddress='0.0.0.0',netmask='0',gateway='0.0.0.0',enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry(items['id'],"Stage 100: ZTP is successful", cursor)
                                ztplog.write('{}: Stage 100: ZTP is successful for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                                connection.close()
                                client.close()  
                    except:
                        pass
            else:
                # Switch is a member switch and it has been provisioned
                print("STAGE 100: ZTP HAS BEEN COMPLETED")
                ztpstatus="ZTP has been completed"
                queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: ZTP is successful", cursor)
                ztplog.write('{}: Stage 100: ZTP is successful for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==42:
            # STAGE 42: SWITCH HAS BEEN CONFIGURED AS SECONDARY. CHECK WHEN SECONDARY IS BACK ONLINE AGAIN
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            masterResult=cursor.fetchall()
            masterResult[0]['adminpassword']=globalconf['ztppassword']
            url="system/vsf_members/"+ str(items['vsfmember'])+"?attributes=role&depth=1"
            if masterResult[0]['enableztp']==100:
                # ZTP has been completed, we have to use the configured admin user. If not completed, we can use the ztpinit user account
                response=getRESTcxIP(masterResult[0]['ipaddress'],masterResult[0]['adminuser'],masterResult[0]['adminpassword'],url, globalconf)
            else:
                response=getRESTcxIP(masterResult[0]['ipaddress'],"ztpuser",password,url, globalconf)
            if "role" in response:
                if response['role']=="standby":
                    # The switch has been designated secondary. The switch is ready
                    ztpstatus="Secondary switch is back online"
                    queryStr="update ztpdevices set enableztp=92, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 42: Secondary switch is back online", cursor)
                    ztplog.write('{}: Stage 42: Secondaru switch {} ({}) is back online. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            else:
                # System is not ready yet
                ztpstatus="Secondary switch is rebooting"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 42: Waiting for secondary member to come online", cursor)
                ztplog.write('{}: Stage 42: Waiting for secondary switch {} ({}) to come back online. \n'.format(datetime.now(),items['ipaddress'],items['name']))

        elif items['enableztp']==5:
            # VSF MASTER TO WAIT WITH CONFIGURATION PUSH UNTIL ALL MEMBERS HAVE JOINED THE STACK
            # We will do two checks. First check is to verify the '100' status for the VSF. If the numbers match the total number of switches configured for the VSF
            # Then the next check is to verify whether the VSF if operational. If that is the case, we can go to stage 6, which is provisioning the master switch configuration
            # Total successfully configured VSF members
            queryStr="select count(*) as total from ztpdevices where vsfmaster='{}'".format(items['id'])
            cursor.execute(queryStr)
            totalinVSF=cursor.fetchall()
            # Total members in VSF. We will check this with a REST call
            # Check whether the VSF is completely operational
            url="system/vsf_members?depth=1"
            response=getRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            # The number of entries (minus 1 for the master switch) identify the number of members in the VSF. If this is the same as the number of VSF switches
            # And the status of all switches is "ready", then we are good to go for the provisioning of the VSF master configuration
            if (len(response)-1)==totalinVSF[0]['total']:
                # VSF seems to be completed, before provisioning, check whether the status of all members is "ready"
                for statusItems in response:
                    if (statusItems['status']!="ready"):
                        notReady=1
                    else:
                        notReady=0
                if notReady==0:
                    ztpstatus="VSF Master setup completed. Provision switch configuration"
                    queryStr="update ztpdevices set enableztp=6, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 5: VSF master has been setup. Provision the switch configuration", cursor)
                    ztplog.write('{}: Stage 5: VSF Master {} ({}) has been setup. Provision the switch configuration. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                else:
                    ztpstatus="Waiting for VSF ready state"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 5: VSF master has been setup. Waiting for VSF ready state", cursor)
                    ztplog.write('{}: Stage 5: VSF master {} ({}) has been setup. Waiting for VSF ready state. \n'.format(datetime.now(),items['ipaddress'],items['name']))

        elif items['enableztp']==6:
            # STAGE 6: PROVISION THE CONFIGURATION
            logEntry(items['id'],"Stage 6: Push configuration template to {}".format(items['ipaddress']), cursor)
            ztplog.write('{}: Stage 6: Push configuration template to {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
            if items['template']!=0:
                # It could be possible that the configuration was pushed successfully, however the initial request timed out.
                # If that is the case, we still want to provision again, but we have to use the ztpuser account
                if checkztpUser(items['ipaddress'],password):
                    username="ztpuser"
                # There is a template. Get the template information
                queryStr="select template from ztptemplates where id='{}'".format(items['template'])
                templateResult=cursor.execute(queryStr)
                templateResult=cursor.fetchall()
                # Create the template
                # Because the template overwrites the complete configuration, we have to add the initial user
                addUser="user ztpuser group administrators password plaintext {}".format(globalconf['ztppassword'])
                jinjaTemplate=Template(templateResult[0]['template'])
                # Template is loaded successfully. Now try to push the parameters into the template
                templateOutput=jinjaTemplate.render(json.loads(items['templateparameters']))
                templateOutput=templateOutput + "\n" + addUser + "\n"
                # Template parameters successfully assigned. Now store the configuration template onto the tftp server
                filename="/home/tftpboot/" + items['macaddress'] + "template.cfg"
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except OSError as e:
                        print (e.filename,e.strerror)
                outFileName="/home/tftpboot/" + items['macaddress'] + "template.cfg"
                outFile=open(outFileName, "w")
                outFile.write(templateOutput)
                outFile.close()
                if items['ztpdhcp']==1 or items['vrf']=="0" or items['vrf']=="" or items['vrf']=="swns":
                    vrf=checkVRF(items['ipaddress'],username,password, globalconf)
                    queryStr="update ztpdevices set vrf='{}' where ipaddress='{}' and macaddress='{}'".format(items['ipaddress'],vrf,items['macaddress']) 
                    cursor.execute(queryStr)
                else:
                    vrf=items['vrf']
                # IMPORTANT: If the IP address of the management interface or vlan 1 interface is changed in the template, we need to make sure that the IP address
                # in the ztpdevice is changed as well, otherwise we cannot complete the ztp process
                deviceIP=checkztpIPaddress(items['ipaddress'],items['netmask'],items['macaddress'],cursor)
                # If the configuration has already been pushed but something went wrong and the IP address and or username has not changed in the database, we have to make that change
                configChange=checkifChanged(deviceIP,items['ipaddress'],password,items['id'],cursor, globalconf)
                print("Configuration change number is {}".format(configChange))
                if configChange==0:
                    username="admin"
                if configChange==1:
                    # The configuration has been pushed and the admin user has changed. IP address is unchanged
                    username="ztpuser"
                elif configChange==2:
                    # The IP address has changed, but admin still has access
                    queryStr="update ztpdevices set ipaddress='{}', vrf='{}' where ipaddress='{}' and macaddress='{}'".format(deviceIP,vrf,items['ipaddress'],items['macaddress']) 
                    print(queryStr)
                    cursor.execute(queryStr)
                    items['ipaddress']=deviceIP
                elif configChange==3:
                    # IP address and admin access has changed. For pushing the configuration we need to use the ztpuser account
                    # It implies that the configuration has already been pushed but something went wrong
                    username="ztpuser"
                    items['ipaddress']=deviceIP
                    vrf=checkVRF(items['ipaddress'],username,password, globalconf)
                    queryStr="update ztpdevices set ipaddress='{}', vrf='{}' where ipaddress='{}' and macaddress='{}'".format(deviceIP,vrf,items['ipaddress'],items['macaddress']) 
                    cursor.execute(queryStr)
                url="fullconfigs/running-config?from=tftp%3A%2F%2F" + hostip + "%2F" + items['macaddress'] + "template.cfg&vrf=" + vrf
                try:
                    response=putRESTcxIP(items['ipaddress'],username,password,url,'', globalconf) 
                    if response==200:
                        logEntry(items['id'],"Stage 6: The push to the running configuration was successful. Now put the configuration in the startup", cursor)
                        ztplog.write('{}: Stage 6: Configuration has been pushed to {} ({}) successfully. Copy the running configuration to the startup configuration. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                        # Now that the push has been successful, if there was a change in IP address of the management interface, or VLAN 1 interface, we have to update 
                        # the device IP address in the database
                        # The push to the running configuration was successful. Now put the configuration in the startup
                        # And from here, we have to use the ztpuser account that was added to the configuration template
                        if deviceIP!=items['ipaddress']:
                            items['ipaddress']=deviceIP
                        # The push to the running configuration was successful. Now repeat the push and store the configuration to the startup-config
                        response=putRESTcxIP(items['ipaddress'],"ztpuser",globalconf['ztppassword'],url,'', globalconf)
                        if response==200:
                            # The put to the startup config was successful
                            url="system?attributes=platform_name"
                            response=getRESTcxIP(items['ipaddress'],"ztpuser",globalconf['ztppassword'],url, globalconf)
                            if response['platform_name']:
                                queryStr="update ztpdevices set ipaddress='{}' where macaddress='{}'".format(items['ipaddress'],items['macaddress']) 
                                cursor.execute(queryStr)
                                filename="/home/tftpboot/" + items['macaddress'] + "template.cfg"
                                if os.path.exists(filename):
                                    try:
                                        os.remove(filename)
                                    except OSError as e:
                                        print (e.filename,e.strerror) 
                                    # Switch is reachable. Final check is whether the switch is a VSF master. If stand alone switch, the ZTP is completed
                                    # If VSF, we need to check whether there is a secondary switch designated. If this is the case, we have to wait until the designated secondary is back online
                                    if items['vsfenabled']==1:
                                        # This is a VSF Master. Go to stage 61
                                        ztpstatus="Verify whether secondary exists"
                                        queryStr="update ztpdevices set enableztp=61, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        cursor.execute(queryStr)
                                        logEntry(items['id'],"Stage 6: Check whether there is a designated secondary switch configured", cursor)
                                        ztplog.write('{}: Stage 6: Verify whether there is a secondary designated switch for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
                                    else:
                                        # ZTP was done through the default DHCP ZTP username password credentials. We need to remove that user from the switch
                                        ztpstatus="Configuration provisioned, finalize ZTP"
                                        queryStr="update ztpdevices set enableztp=9, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        cursor.execute(queryStr)
                                        logEntry(items['id'],"Stage 6: Configuration stored, finalizing ZTP", cursor)
                                        ztplog.write('{}: Stage 6: Configuration stored to {} ({}). Finalizing ZTP. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                            else:
                                # Seems that the switch is not reachable anymore. Update the status.
                                ztpstatus="Switch is not reachable anymore, retrying.."
                                logEntry(items['id'],"Stage 6: Switch is not reachable anymore, retrying..", cursor)
                                ztplog.write('{}: Stage 6: {} ({}) is not reachable anymore. Retrying... \n'.format(datetime.now(),items['ipaddress'],items['name']))
                                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                        else:
                            # Configuration not pushed to the switch, something went wrong with the push. We need to try again
                            ztpstatus="Could not push the configuration template, retrying.."
                            logEntry(items['id'],"Stage 6: Could not push the configuration template, retrying..", cursor)
                            ztplog.write('{}: Stage 6: Unable to push the configuration to {} ({}). Retrying... \n'.format(datetime.now(),items['ipaddress'],items['name']))
                            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr)
                    else:
                        # We received a response that was not 200
                        ztpstatus="Could not push the configuration template, retrying.."
                        logEntry(items['id'],"Stage 6: Could not push the configuration template, retrying..", cursor)
                        ztplog.write('{}: Stage 6: Unable to push the configuration to {} ({}). Retrying... \n'.format(datetime.now(),items['ipaddress'],items['name']))
                        queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                except:
                    logEntry(items['id'],"Stage 6: Error pushing configuration template to running configuration for {}, IP address might have changed.".format(items['ipaddress']), cursor)
                    ztplog.write('{}: Stage 6: Unable to push the configuration template to the running configuration of {} ({}), IP address might have changed. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            else:
                logEntry(items['id'],"Stage 6: There is no template configured for {}".format(items['ipaddress']), cursor)
                ztplog.write('{}: Stage 6: There is no template configured for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==61:
            # STAGE 61: VERIFY WHETHER A SECONDARY SWITCH HAS BEEN CONFIGURED IN ZTP
            # If this is the case, we need to wait until the secondary switch has joined the VSF again and the VSF is completed. Only then the ZTP process is completed
            # First check, is there a secondary member
            queryStr="select * from ztpdevices where vsfenabled=1 and vsfrole='Secondary' and vsfmaster={}".format(items['id'])
            cursor.execute(queryStr)
            checkSecondary = cursor.fetchall()
            if checkSecondary:
                # There is a secondary switch in the VSF. We have to check whether the secondary switch has joined the VSF. If it has (status=ready and role=secondary), then ZTP is completed
                url="system/vsf_members?depth=1"
                response=getRESTcxIP(items['ipaddress'],"ztpuser",globalconf['ztppassword'],url, globalconf)
                # First check, are all switches up and running (status ready)
                notReady=1
                for statusItems in response:
                    if (statusItems['status']!="ready"):
                        notReady=1
                    else:
                        # Switch is ready. Now check if the member ID is the same as the designated secondary. From the sql query we know the member id, so we can check against the member id
                        if statusItems['id']==checkSecondary[0]['vsfmember']:
                            # This is the designated secondary. What is the role? If it is not secondary, the system is not ready yet
                            if statusItems['role']=="standby":
                                notReady=0
                            else:
                                notReady=1
                if notReady==0:                 
                    # ZTP was done through the default DHCP ZTP username password credentials. We need to remove that user from the switch
                    ztpstatus = "Configuration stored, finalizing ZTP"
                    queryStr="update ztpdevices set enableztp=9, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 61: Configuration stored, finalizing ZTP", cursor)
                    ztplog.write('{}: Stage 61: Configuration stored to {} ({}), finalizing ZTP. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                else:
                    # System is not ready yet
                    ztpstatus="Waiting for secondary switch"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 61: Waiting for secondary member to come online", cursor)
                    ztplog.write('{}: Stage 61: Waiting for secondary member to come online for {} ({}). \n'.format(datetime.now(),items['ipaddress'],items['name']))
            else:
                # ZTP was done through the default DHCP ZTP username password credentials. We need to remove that user from the switch
                ztpstatus="Configuration stored. Finalizing ZTP"
                queryStr="update ztpdevices set enableztp=9, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 61: Configuration stored, finalizing ZTP", cursor)
                ztplog.write('{}: Stage 61: Configuration stored to {} ({}), finalizing ZTP. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==8:
            # STAGE 8: THERE IS ALREADY AN INITIAL CONFIGURATION ON THE SWITCH
            print("STAGE 8: INITIAL CONFIGURATION ALREADY EXISTS")
            ztpstatus="Try to access the {} through SSH or HTTPS".format(items['ipaddress'])
            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
            cursor.execute(queryStr)
            logEntry(items['id'],"Stage 8: Try to access the {} through SSH or HTTPS".format(items['ipaddress']), cursor)
            ztplog.write('{}: Stage 8: Trying to access {} ({}) through SSH or HTTPS. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==9:
            # STAGE 9: ZTP PERFORMED. NEED TO REMOVE THE ZTP USER
            # Admin has to verify the admin user credentials first through the app. If the credentials are ok, the app will set the stage to 91, and then we can remove the ztp user
            pass
        elif items['enableztp']==91:
            # STAGE 91: ADMIN USER VERIFICATION WAS SUCCESSFUL. REMOVE THE ZTP USER
            # The administrative user account should have been stored in the database (encrypted password), so we should delete the ztp user with the admin account credentials
            queryStr="select adminuser, adminpassword from ztpdevices where id='{}'".format(items['id'])
            cursor.execute(queryStr)
            adminaccount=cursor.fetchall()
            username=adminaccount[0]['adminuser']
            password=decryptPassword(globalconf['secret_key'], adminaccount[0]['adminpassword'])
            # Now that we have the admin account, we can delete the ztp user account
            url="system/users/ztpuser"
            result=deleteRESTcxIP(items['ipaddress'],username,password,url, globalconf)
            if result==204:
                # The ztpuser has been removed from the running configuration. Now copy the running configuration to the startup configuration
                url="fullconfigs/startup-config?from=%2Frest%2F" + globalconf['cxapi'] + "%2Ffullconfigs%2Frunning-config"
                # The push to the running configuration was successful. Now repeat the push and store the configuration to the startup-config
                response=putRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                ztpstatus="ZTP has been completed".format(items['ipaddress'])
                queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: ZTP user removed, ZTP has been completed", cursor)
                ztplog.write('{}: Stage 100: ZTP user removed from {} ({}), ZTP has been completed. \n'.format(datetime.now(),items['ipaddress'],items['name']))
            elif result==404:
                # It seems that the ztpuser does not exist anymore, so we are also good here. Now copy the running configuration to the startup configuration
                url="fullconfigs/startup-config?from=%2Frest%2F" + globalconf['cxapi'] + "%2Ffullconfigs%2Frunning-config"
                # The push to the running configuration was successful. Now repeat the push and store the configuration to the startup-config
                response=putRESTcxIP(items['ipaddress'],username,password,url,'', globalconf)
                ztpstatus="ZTP has been completed"
                queryStr="update ztpdevices set enableztp=100,ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: Non existent ZTP user, ZTP has been completed", cursor)
                ztplog.write('{}: Stage 100: ZTP user does not exist on {} ({}), ZTP has been completed. \n'.format(datetime.now(),items['ipaddress'],items['name']))
        elif items['enableztp']==92:
            # STAGE 9: ZTP PERFORMED FOR THE SECONDARY SWITCH
            # Only update the database if the master switch ZTP has been completed
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            masterStatus=cursor.fetchall()
            if masterStatus[0]['enableztp']==100:
                # ZTP has been completed for the master, set the stage for the member to 100
                ztpstatus="ZTP has been completed"
                queryStr="update ztpdevices set ipaddress='0.0.0.0', netmask='0', gateway='0.0.0.0', enableztp=100,ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: ZTP has been completed", cursor)
                ztplog.write('{}: Stage 100: ZTP of {} ({}) has been completed. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                print("STAGE 100: ZTP HAS BEEN COMPLETED")
    ztplog.close()
    
def getRESTcxIP(ip,username,password,url, globalconf):
    global sessionid
    baseurl="https://{}/rest/{}/".format(ip, globalconf['cxapi'])
    credentials={'username': username,'password': password }
    try:
        response=sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
        if "session limit reached" in response.text:
        #    # We need to clear the https sessions. For some reason there are too many logins
            cs=clearSessions(ip, username,password)
            if cs=="ok":
                sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                response = sessionid.get(baseurl + url, verify=False, timeout=10)
                sessionid.post(baseurl + "logout", verify=False, timeout=5)
                response=json.loads(response.content)
                return response

            else:
                response={}
                ztplog.write('{}: Error obtaining information from {} ({}) through REST GET. \n'.format(datetime.now(),items['ipaddress'],items['name']))
                pass
        else:
            response = sessionid.get(baseurl + url, verify=False, timeout=10)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            try:
                sessionid.post(baseurl + "logout", verify=False, timeout=5)
                return {}
            except ConnectionError as e:
                ztplog.write('{}: Connection error from {} ({}) through REST GET: {} \n'.format(datetime.now(),items['ipaddress'],items['name']),e)
                return {}
        try:
            sessionid.post(baseurl + "logout", verify=False, timeout=5)
        except ConnectionError as e:
            ztplog.write('{}: Connection error from {} ({}) through REST GET: {} \n'.format(datetime.now(),items['ipaddress'],items['name']),e)
            return {}
    except ConnectionError as e:
        ztplog.write('{}: Connection error from {} ({}) through REST GET: {} \n'.format(datetime.now(),items['ipaddress'],items['name']),e)
        return {}
    except:
        return {}
    return response

def putRESTcxIP(ip,username,password,url,parameters, globalconf):
    global sessionid
    baseurl="https://{}/rest/{}/".format(ip, globalconf['cxapi'])
    credentials={'username': username,'password': password }
    try:
        response = sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
        response = sessionid.put(baseurl + url, data=parameters, verify=False, timeout=10)
        sessionid.post(baseurl + "logout", verify=False, timeout=5)
        return response.status_code
    except:
        sessionid.post(baseurl + "logout", verify=False, timeout=5)
        return 401


def postRESTcxIP(ip,username,password,url,parameters, globalconf):
    global sessionid
    baseurl="https://{}/rest/{}/".format(ip, globalconf['cxapi'])
    credentials={'username': username,'password': password }
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=10)
        response = sessionid.post(baseurl + url, data=parameters,verify=False, timeout=20)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            response=response.status_code
        sessionid.post(baseurl + "logout", verify=False, timeout=10)
    except:
        return {}
    return response

def deleteRESTcxIP(ip,username,password,url, globalconf):
    global sessionid
    baseurl="https://{}/rest/{}/".format(ip, globalconf['cxapi'])
    credentials={'username': username,'password': password }
    statuscode=0
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
        response = sessionid.delete(baseurl + url, verify=False, timeout=5)
        try:
            # If the response contains information, the content is converted to json format
            statuscode=response.status_code
        except:
            statuscode=404
        sessionid.post(baseurl + "logout", verify=False, timeout=10)
    except:
        return statuscode
    return statuscode

def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def logEntry(ztpdevice,message, cursor):
    # First, check whether there is an existing logging entry for this device
    queryStr="select * from ztplog where ztpdevice='{}'".format(ztpdevice)
    result=cursor.execute(queryStr)
    result = cursor.fetchall()
    if not result:
        timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        logEntry=[{"datetime": timestamp ,"logEntry": message}]
        queryStr="insert into ztplog (ztpdevice,logging) values ('{}','{}')".format(ztpdevice,json.dumps(logEntry))
        cursor.execute(queryStr)
    else:
        # There is a log entry. We need to check whether the last four messages are the same message as the current one. If it is not, then update
        logging=json.loads(result[0]['logging'])
        lastEntries=logging[len(logging)-4:]
        messageExists=0
        for items in lastEntries:
            if message in items.values():
                messageExists=1
        if messageExists==0:
            # The last entry is not the same, we can update
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            logEntry={"datetime": timestamp ,"logEntry": message}
            logging.append(logEntry)
            queryStr="update ztplog set logging='{}' where ztpdevice='{}'".format(json.dumps(logging),ztpdevice)
            cursor.execute(queryStr)

def checkVRF(ip,username,password, globalconf):
    # Check which VRF has the active IP address
    # Check the management VRF IP address against the configured IP address. If there is a match we need to return the mgmt VRF, else the default VRF
    url="system?attributes=mgmt_intf%2Cmgmt_intf_status&depth=2"
    response=getRESTcxIP(ip,username,password,url, globalconf)
    if response:
        if "ip" in response['mgmt_intf_status']:
            if response['mgmt_intf_status']['ip']==ip:
                return "mgmt"
            else:
                return "default"
        else:
            return "default"
    else:
        return "default"

def checkztpIPaddress(ztpip,netmask,macaddress,cursor):
    try:
        with open("/home/tftpboot/" + macaddress + "template.cfg", 'r') as template:
            lines = template.readlines()
            # Checking the IP addresses in the configuration. If the IP address exists and if it is in the same subnet, we need to update the ztp device
            for line in lines:
                if "ip address" in line or "ip static" in line:
                    # Check whether the IP address of the ztp device is in the same subnet as the IP address in the template
                    # First, extract the IP address. Note that this is unstructured data, so we need to split and create a list
                    templateIP=line.split(" ")
                    devIP=templateIP[len(templateIP)-1].split("/")
                    if ipaddress.ip_address(devIP[0]) in ipaddress.ip_network(ztpip + "/" + netmask,strict=False):
                        # There is an IP address configured in the template...
                        return devIP[0]
    except:
        # There was an issue checking the ZTP and Template IP address
        pass
    return ztpip

def getplatformName(ip,username,password, dbimage, globalconf):
    # Formating the image name so that we can compare with the information from the rest call
    platformNames={"6300":"FL","8320":"TL","8325":"GL"}
    url="system?attributes=platform_name"
    platformName=getRESTcxIP(ip,username,password,url, globalconf)
    if platformName:
        platformCode=platformNames[platformName['platform_name']]
        imagename=platformCode+"."+dbimage.split('_',2)[2].rsplit('.',1)[0].replace("_",".")
        return imagename
    else:
        return "none"

def checkztpUser(ip,password):
    # Check if the ztp user exists in the switch configuration. If it does exist, this means that the configuration template has been pushed
    url="system?attributes=platform_name"
    platformName=getRESTcxIP(ip,"ztpuser",password,url, globalconf)
    if platformName:
        return 1
    else:
        return 0

def checkifChanged(deviceIP,ztpip,password,id,cursor, globalconf):
    url="system?attributes=platform_name"
    # First check if the IP address has changed
    if (deviceIP==ztpip):
        adminResult=getRESTcxIP(ztpip,"admin",password,url, globalconf)
        ztpResult=getRESTcxIP(ztpip,"ztpuser",password,url, globalconf)
        if adminResult:
            # Nothing has changed
            return 0
        elif ztpResult:
            # The configuration has been pushed and the admin user has changed
            return 1
        else:
           return 0
    else:
        adminResult=getRESTcxIP(deviceIP,"admin",password,url, globalconf)
        ztpResult=getRESTcxIP(deviceIP,"ztpuser",password,url, globalconf) 
        # There is a third situation, where the configuration has not been pushed, so the IP address of the device has not changed
        # This means that we also have to check admin access on the ztp ip address
        ztpinitResult=getRESTcxIP(ztpip,"admin",password,url, globalconf)
        if ztpinitResult:
            # Nothing has changed
            return 0
        elif adminResult:
            # IP address has changed, but admin still has access
            return 2
        elif ztpResult:
            # IP address and admin access has changed
            return 3
        else:
            return 4
    return 0

def clearSessions(ipaddr, username,password):
    try:
        client=SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy)
        client.connect(ipaddr,username=username,password=password, timeout=5)
        # Logging in could take some time. Pause a bit
        connection=client.invoke_shell()
        connection.send("\n")
        time.sleep(10)
        connection.send("https session close all \n")
        time.sleep(3)
        connection.close()
        client.close()
        return "ok"
    except:
        return "nok"


def obtainGlobalconf(cursor):
    queryStr="select datacontent from systemconfig where configtype='system'"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    globalconf=result[0]
    if isinstance(globalconf,str):
        globalconf=json.loads(globalconf)
    globalconf=globalconf['datacontent']
    if isinstance(globalconf,str):
        globalconf=json.loads(globalconf)
    return globalconf