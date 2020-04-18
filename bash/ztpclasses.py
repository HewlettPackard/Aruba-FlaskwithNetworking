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
    STAGE 5: If VSF on master is successful, check whether all VSF members have joined. If not, loop in this stage. If VSF is completed, go to stage 6
    STAGE 6: Provision configuration to the switch
    STAGE 8: There is already an initial configuration on the switch
    100 = Successfully pushed the configuration template
    '''
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    pathname = os.path.dirname(sys.argv[0])
    if platform.system()=="Windows":
        appPath = os.path.abspath(pathname) + "\\globals.json"      
    else:
        appPath = os.path.abspath(pathname) + "/globals.json"
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    # Obtain device information from which ztp has been enabled
    queryStr="select * from ztpdevices where enableztp>0 and enableztp<99"
    deviceResult=cursor.execute(queryStr)
    deviceResult = cursor.fetchall()
    for items in deviceResult:
        queryStr="select username,password, vrf from ztpprofiles where id='{}'".format(items['profile'])
        credentialResult=cursor.execute(queryStr)
        credentialResult = cursor.fetchall()
        credentialResult[0]['password'] = decryptPassword(globalconf['secret_key'], credentialResult[0]['password'])
        # Now that we have the IP address of the device, and the username/password. Obtain the ZTP information
        if items['enableztp']==1:
            # STAGE 1: INITIAL ZTP CONFIGURATION PUSH THROUGH DHCP OPTIONS
            print("STAGE 1: INITIAL ZTP CONFIGURATION PUSH THROUGH DHCP OPTIONS FOR {}".format(items['ipaddress']))
            logEntry(items['id'],"Stage 1: Provision initial configuration for {}".format(items['name']),cursor)
            try:
                url="system?attributes=ztp"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                print(response)
                if response['ztp']['state']=="success":
                    ztpstatus=response['ztp']['configuration_file'] + " successful download from " + response['ztp']['tftp_server']
                    queryStr="update ztpdevices set enableztp=2, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 1: Initial template downloaded successful", cursor)
                elif response['ztp']['failure_reason']=="non_default_startup_config" and  response['ztp']['state']=="aborted":
                    ztpstatus="Initial configuration is present"
                    queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 1: Initial configuration for {} already exists".format(items['name']),cursor)
            except:
                logEntry(items['id'],"Stage 1: Provision initial configuration for {}".format(items['name']),cursor)
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
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                # Only continue if there is a response. If there is no response, the switch might be offline
                if response:
                    # Obtain the image file name
                    queryStr="select filename from ztpimages where id='{}'".format(softwareimage)
                    cursor.execute(queryStr)
                    imageResult=cursor.fetchall()
                    # Formating the image name so that we can compare with the information from the rest call
                    imagename="FL."+imageResult[0]['filename'].split('_',2)[2].rsplit('.',1)[0].replace("_",".")
                    if imagename==response['current_version']:
                        # There is no need to upgrade the switch. Switch is already running on the right software
                        logEntry(items['id'],"Stage 2: {} already on the right software".format(items['ipaddress']), cursor)
                        ztpstatus="Switch running on " + imagename + ". Verify VSF configuration"
                        queryStr="update ztpdevices set enableztp=3, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                    else:
                        # Switch is not running on the right software, we need to upgrade.
                        url="firmware?image=primary&from=http://" + hostip + "/images/" + imageResult[0]['filename'] + "&vrf=" + credentialResult[0]['vrf']
                        response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                        if response==200:
                            ztpstatus="Upgrade switch to " + imagename
                            queryStr="update ztpdevices set enableztp=21, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr)
                            logEntry (items['id'],"Stage 2: Upgrade the switch to {}".format(imagename), cursor)
            else:
                # There is no image attached to the device. No need to upgrade. Next stage is to verify whether switch operates in VSF or standalone (stage 3)
                logEntry (items['id'],"Stage 2: There is no software image attached. Verify VSF configuration", cursor)
                ztpstatus="Verify VSF configuration"
                queryStr="update ztpdevices set enableztp=3, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==21:
            # STAGE 21: SWITCH IS UPGRADING. CHECK STATUS
            print("STAGE 21: {} IS UPGRADING. CHECK STATUS".format(items['ipaddress']))
            logEntry(items['id'],"Stage 21: {} is upgrading, checking the status".format(items['ipaddress']), cursor)
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response['status']=="success":
                # Another check to see whether the image has been pushed to the primary partition. If it has not been pushed, we have to re-issue the upload command
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                # The response content should contain the primary version information that is the updated image
                # Obtain the image file name
                if (items['vsfenabled']==1 and items['vsfmaster']!=0):
                    queryStr="select softwareimage from ztpdevices where id='{}'".format(items['vsfmaster'])
                    cursor.execute(queryStr)
                    softwareimage=cursor.fetchall()
                    softwareimage=softwareimage[0]['softwareimage']
                elif items['softwareimage']!=0:
                    softwareimage=items['softwareimage']
                queryStr="select filename from ztpimages where id='{}'".format(softwareimage)
                cursor.execute(queryStr)
                imageResult=cursor.fetchall()
                # Formating the image name so that we can compare with the information from the rest call
                imagename="FL."+imageResult[0]['filename'].split('_',2)[2].rsplit('.',1)[0].replace("_",".")
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
                                response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                                ztpstatus="Upgrade successful, preparing for reboot"
                                queryStr="update ztpdevices set enableztp=22, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
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
                                if goodtoBoot==1:
                                    # All the VSF members have been upgraded and are back online
                                    url="boot?image=primary"
                                    response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                                    ztpstatus="Upgrade successful, rebooting the switch"
                                    queryStr="update ztpdevices set enableztp=23, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                    cursor.execute(queryStr)
                                    logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
                        else: 
                            # It's not a VSF, so we can reboot the switch straight away
                            url="boot?image=primary"
                            response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                            ztpstatus="Upgrade successful, preparing for reboot"
                            queryStr="update ztpdevices set enableztp=28, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr)
                            logEntry(items['id'],"Stage 21: {} has been upgraded to {}. Rebooting".format(items['ipaddress'],imagename), cursor)
                    else:
                        pass           
            elif response['status']=="in_progress":
                ztpstatus="Upgrade in progress"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==22:
            #STAGE 22: VSF MEMBER REBOOTED. CHECK WHETHER VSF MEMBER IS BACK ONLINE
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if not bool(response):
                # VSF Member is not online yet. Loop this stage
                ztpstatus="VSF member switch is starting up"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            else:
                # VSF member is back online. Only go to stage 4 (provision VSF), when the master is also back online (master switch should be set to stage 4)
                ztpstatus="Member switch is back online"
                queryStr="update ztpdevices set enableztp=24, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 22: Member is back online", cursor)
        elif items['enableztp']==23:
            # STAGE 23: VSF MASTER REBOOTED. CHECK WHETHER VSF MASTER IS BACK ONLINE. IF BACK ONLINE, GOTO STAGE 4 FOR THE VSF CONFIGURATION
            queryStr="select filename from ztpimages where id='{}'".format(items['softwareimage'])
            cursor.execute(queryStr)
            imageResult=cursor.fetchall()
            # Formating the image name so that we can compare with the information from the rest call
            imagename="FL."+imageResult[0]['filename'].split('_',2)[2].rsplit('.',1)[0].replace("_",".")
            url="firmware"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
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
            else:
                # Master switch is not back online yet
                # The master is back online, members can be provisioned for VSF
                ztpstatus="Waiting for master switch to come online"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==28:
            # STAGE 28: STANDALONE SWITCH HAS BEEN UPGRADED AND IS REBOOTING
            logEntry(items['id'],"Stage 28: {} is rebooting".format(items['ipaddress']), cursor)
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if not bool(response):
                # Standalone switch not online yet. Loop this stage
                ztpstatus="Rebooting switch"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            else:
                # Standalone switch is back online, go to configuration provisioning stage
                ztpstatus="Upgrade successful, provision configuration"
                queryStr="update ztpdevices set enableztp=6, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 28: Upgrade has been successful, provision configuration", cursor)
        elif items['enableztp']==3:
            # STAGE 3: CHECK WHETHER VSF IS CONFIGURED. IF YES, GOTO STAGE 4 (PROVISION VSF), IF NOT, GOTO STAGE 6 (PROVISION CONFIGURATION)
            # This stage runs if there was no software image attached
            print("STAGE 3: CHECK IF SWITCH IS CONFIGURED FOR VSF")
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
            print("STAGE 4: CONFIGURE VSF PORTS AND RENUMBER MEMBER SWITCH")
            try:
                client=SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy)
                client.connect(items['ipaddress'],username=credentialResult[0]['username'],password=credentialResult[0]['password'])
                connection=client.invoke_shell()
                connection.send("\n")
                time.sleep(1)
                connection.send("configure terminal\n")
                time.sleep(1)
                try:
                    connection.send("vsf member 1\n")
                    time.sleep(1)
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
                    renumberCmd="vsf renumber-to " + str(items['vsfmember']) + "\n"
                    connection.send(renumberCmd)
                    time.sleep(4)
                    connection.send('y\n')
                    time.sleep(3)
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
                        ztpstatus="VSF has been deployed to the member switch, rebooting switch"
                        queryStr="update ztpdevices set enableztp=41, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        cursor.execute(queryStr)
                # SWITCH IS MASTER
                else:
                    try:
                        connection.close()
                        client.close()
                    except:
                        pass
                    # We can go into the next stage, which is for the master switch to wait until all members have joined the stack
                    logEntry(items['id'],"Stage 4: VSF has been deployed to the master switch. Waiting for member switches", cursor)
                    ztpstatus="VSF has been deployed. Waiting for member switches"
                    queryStr="update ztpdevices set enableztp=5, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
            except:
                # First, get the VSF topology from the master
                if items['vsfmaster']!=0:
                     queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
                     cursor.execute(queryStr)
                     vsfmasterResult=cursor.fetchall()
                     queryStr="select * from ztpprofiles where id='{}'".format(vsfmasterResult[0]['profile'])
                     cursor.execute(queryStr)
                     masterprofileResult=cursor.fetchall()
                     masterprofileResult[0]['password'] = decryptPassword(globalconf['secret_key'], masterprofileResult[0]['password'])
                     url="system/vsf_members?attributes=id%2Crole%2Cstatus&depth=2"
                     response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                     # Now check if the VSF member exists in the VSF and status is ready
                     memberInfo=next(item for item in response if item["id"] == items['vsfmember'])
                     if memberInfo['id']==items['vsfmember'] and memberInfo['status']=="ready":
                         logEntry(items['id'],"Stage 4: VSF has been deployed to the member switch", cursor)
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
            queryStr="select * from ztpprofiles where id='{}'".format(vsfmasterResult[0]['profile'])
            cursor.execute(queryStr)
            masterprofileResult=cursor.fetchall()
            masterprofileResult[0]['password'] = decryptPassword(globalconf['secret_key'], masterprofileResult[0]['password'])
            url="system/vsf_members?attributes=id%2Crole%2Cstatus&depth=2"
            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if items['vsfrole']=="Secondary":
                # Additional check is to verify whether the secondary switch member id exists in the VSF. If it does, we can assign the secondary role to the member switch
                # We should only push the secondary role to the master switch when the master switch has been completed and the VSF is ready (stage 61)
                if vsfmasterResult[0]['enableztp']==61:
                    # At the moment there is no API call for configuring the secondary role, therefore we have to set this using SSH. And for this we need to login to the master switch
                    try:
                        client=SSHClient()
                        client.set_missing_host_key_policy(AutoAddPolicy)
                        client.connect(vsfmasterResult[0]['ipaddress'],username=masterprofileResult[0]['username'],password=masterprofileResult[0]['password'])
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
                            connection.send('y\n')
                            time.sleep(3)
                            connection.close()
                            client.close()  
                        else:
                            # Secondary is already configured. Now check the VSF status again. If the member is up and running again, we can set the status to completed
                            url="system/vsf_members/"+str(items['vsfmember'])
                            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],masterprofileResult[0]['username'],masterprofileResult[0]['password'],url)
                            if response['status']=="ready":
                                # It is done. The member switch has been provisioned
                                print("STAGE 100: ZTP COMPLETED")
                                ztpstatus="ZTP completed"
                                queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                                logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
                                connection.close()
                                client.close()  
                    except:
                        pass
            else:
                # Switch is a member switch and it has been provisioned
                print("STAGE 100: ZTP COMPLETED")
                ztpstatus="ZTP completed"
                queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
        elif items['enableztp']==42:
            # STAGE 42: SWITCH HAS BEEN CONFIGURED AS SECONDARY. CHECK WHEN SECONDARY IS BACK ONLINE AGAIN
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            masterResult=cursor.fetchall()
            url="system/vsf_members/" + str(items['vsfmember']) + "?depth=1"
            response=getRESTcxIP(masterResult[0]['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response:
                if response['role']=="standby":
                    # The switch has been designated secondary. The switch is ready
                    print("STAGE 100: ZTP COMPLETED")
                    ztpstatus="ZTP completed"
                    queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
            else:
                # System is not ready yet
                ztpstatus="Waiting for secondary switch"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 42: Waiting for secondary member to come online", cursor)

        elif items['enableztp']==5:
            # VSF MASTER TO WAIT WITH CONFIGURATION PUSH UNTIL ALL MEMBERS HAVE JOINED THE STACK
            # We will do two checks. First check is to verify the '100' status for the VSF. If the numbers match the total number of switches configured for the VSF
            # Then the next check is to verify whether the VSF if operational. If that is the case, we can go to stage 6, which is provisioning the master switch configuration
            # Total successfully configured VSF members
            print("STAGE 5: VSF MASTER TO WAIT WITH CONFIGURATION PUSH UNTIL ALL MEMBERS HAVE JOINED THE STACK")
            queryStr="select count(*) as total from ztpdevices where vsfmaster='{}'".format(items['id'])
            cursor.execute(queryStr)
            totalinVSF=cursor.fetchall()
            # Total members in VSF. We will check this with a REST call
            # Check whether the VSF is completely operational
            url="system/vsf_members?depth=1"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
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
                else:
                    ztpstatus="Waiting for VSF ready state"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 5: VSF master has been setup. Waiting for VSF ready state", cursor)

        elif items['enableztp']==6:
            # STAGE 6: PROVISION THE CONFIGURATION
            print("STAGE 6: PROVISION THE CONFIGURATION FOR {}".format(items['ipaddress']))
            logEntry(items['id'],"Stage 6: Push configuration template to {}".format(items['ipaddress']), cursor)
            if items['template']!=0:
                # there is a template. Get the template information
                queryStr="select template from ztptemplates where id='{}'".format(items['template'])
                templateResult=cursor.execute(queryStr)
                templateResult=cursor.fetchall()
                # Create the template
                jinjaTemplate=Template(templateResult[0]['template'])
                # Template is loaded successfully. Now try to push the parameters into the template
                templateOutput=jinjaTemplate.render(json.loads(items['templateparameters']))
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
                url="fullconfigs/running-config?from=tftp%3A%2F%2F" + hostip + "%2F" + items['macaddress'] + "template.cfg&vrf=" + credentialResult[0]['vrf']
                try:
                    response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'') 
                    if response==200:
                        logEntry(items['id'],"Stage 6: The push to the running configuration was successful. Now put the configuration in the startup", cursor)
                        # The push to the running configuration was successful. Now put the configuration in the startup
                        url="fullconfigs/startup-config?from=%2Frest%2Fv1%2Ffullconfigs%2Frunning-config"
                        # url="fullconfigs/startup-config?from=tftp%3A%2F%2F" + hostip + "%2F" + items['macaddress'] + "template.cfg&vrf=" + credentialResult[0]['vrf']
                        # The push to the running configuration was successful. Now repeat the push and store the configuration to the startup-config
                        response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                        if response==200:
                            # The put to the startup config was successful
                            url="system?attributes=platform_name"
                            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                            if response['platform_name']:
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
                                    else:
                                        ztpstatus="ZTP completed"
                                        print("STAGE 100: ZTP COMPLETED")
                                        queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        cursor.execute(queryStr)
                                        logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
                            else:
                                # Seems that the switch is not reachable anymore. Update the status.
                                ztpstatus="Switch is not reachable anymore, retrying.."
                                logEntry(items['id'],"Stage 6: Switch is not reachable anymore, retrying..", cursor)
                                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                        else:
                            # Configuration not pushed to the switch, something went wrong with the push. We need to try again
                            ztpstatus="Could not push the configuration template, retrying.."
                            logEntry(items['id'],"Stage 6: Could not push the configuration template, retrying..", cursor)
                            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                            cursor.execute(queryStr) 
                except:
                    logEntry(items['id'],"Stage 6: Error pushing configuration template to running configuration {}".format(items['ipaddress']), cursor)
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
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
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
                    # The VSF configuration is completed
                    print("STAGE 100: ZTP COMPLETED")
                    ztpstatus="ZTP completed"
                    queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
                else:
                    # System is not ready yet
                    ztpstatus="Waiting for secondary switch"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 61: Waiting for secondary member to come online", cursor)
            else:
                # The VSF configuration is completed
                print("STAGE 100: ZTP COMPLETED")
                ztpstatus="ZTP completed"
                queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                logEntry(items['id'],"Stage 100: ZTP provisioning successful", cursor)
        elif items['enableztp']==8:
            #STAGE 8: THERE IS ALREADY AN INITIAL CONFIGURATION ON THE SWITCH
            print("STAGE 8: INITIAL CONFIGURATION ALREADY EXISTS")
            ztpstatus="Try to access the {} through SSH or HTTPS".format(items['ipaddress'])
            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
            cursor.execute(queryStr)
            logEntry(items['id'],"Stage 8: Try to access the {} through SSH or HTTPS".format(items['ipaddress']), cursor)


    
def getRESTcxIP(ipaddress,username,password,url):
    global sessionid
    baseurl="https://{}/rest/v1/".format(ipaddress)
    credentials={'username': username,'password': password }
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=10)
        response = sessionid.get(baseurl + url, verify=False, timeout=10)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            sessionid.post(baseurl + "logout", verify=False, timeout=5)
            # print("Error obtaining response from get call")
            response={}
        sessionid.post(baseurl + "logout", verify=False, timeout=5)
    except:
        response={}
    return response

def putRESTcxIP(ipaddress,username,password,url,parameters):
    global sessionid
    baseurl="https://{}/rest/v1/".format(ipaddress)
    credentials={'username': username,'password': password }
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=10)
        response = sessionid.put(baseurl + url, data=parameters, verify=False, timeout=20)
        sessionid.post(baseurl + "logout", verify=False, timeout=10)
        return response.status_code
    except:
        sessionid.post(baseurl + "logout", verify=False, timeout=10)
        return 401
    return response


def postRESTcxIP(ipaddress,username,password,url,parameters):
    global sessionid
    baseurl="https://{}/rest/v1/".format(ipaddress)
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

def deleteRESTcxIP(ipaddress,username,password,url):
    global sessionid
    baseurl="https://{}/rest/v1/".format(ipaddress)
    credentials={'username': username,'password': password }
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=10)
        response = sessionid.delete(baseurl + url, verify=False, timeout=20)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            response={}
        sessionid.post(baseurl + "logout", verify=False, timeout=10)
    except:
        return {}
    return response

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
        # There is a log entry. We need to check whether the last three messages are the same message as the current one. If it is not, then update
        logging=json.loads(result[0]['logging'])
        lastEntries=logging[len(logging)-3:]
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