# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from datetime import datetime, time, timedelta
import time
import socket
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
    1 = enabled for initial ztp
    2 = initial ZTP configuration has been downloaded successfully and stored to the startup configuration. Check whether VSF is enabled and switch is not master. Check software version
    21 = Upgrade VSF member software so that it is the same as the master 
    22 = Reboot the member switch
    23 = Provision the VSF member
    3 = VSF has been provisioned to a member switch, check if the switch is back online again. If it is verify the VSF status
    4 = Check whether the switch requires a software update
    5 = Downloading optional software image to the switch
    6 = Successfully downloaded the software image, preparing to reboot
    7 = Switch reboots
    8 = Switch has been rebooted with the right image and is accessible again, pushing the configuration template
    10 = Configure the master VSF ports
    11 = Successfully pushed the configuration template
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
            # logEntry(items['id'],"Stage 1 for {}".format(items['name']),cursor)
            # print("Stage 1 for ", items['name'])
            try:
                url="system?attributes=ztp"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                if response['ztp']['state']=="success":
                    ztpstatus=response['ztp']['configuration_file'] + " successful download from " + response['ztp']['tftp_server']
                    queryStr="update ztpdevices set enableztp=2, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    logEntry(items['id'],"Stage 1: Initial template downloaded successful", cursor)
                    # print("Stage 1: Initial template downloaded successful")
                elif response['ztp']['failure_reason']=="non_default_startup_config" and  response['ztp']['state']=="aborted":
                    ztpstatus="Initial configuration is present"
                    queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
            except:
                logEntry(items['id'],"Stage 1: Cannot obtain ZTP information from {}".format(items['ipaddress']), cursor)
                #print("Stage 1: Cannot obtain ZTP information from",items['ipaddress'])
                pass
        # The initial configuration file has been successfully downloaded and saved to the startup-configuration. We now need to check whether VSF is enabled for this device
        # If VSF is enabled, if the switch role is member or secondary, we should only push the member id and the VSF ports.
        # If the member role is primary, we should just go through the process and at the end of the ztp process, configure the VSF ports (stage 9)
        elif items['enableztp']==2:
            if items['vsfenabled']==1 and items['vsfmaster']!=0:
                logEntry(items['id'],"Stage 2: VSF is enabled, need to provision secondary/member configuration", cursor)
                # print("Stage 2: VSF is enabled and we need to provision secondary/member configuration")
                ztpstatus="Provisioning VSF member"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
                # First thing to do is to check whether the member switch requires a software upgrade. For this we need to check whether the software image is selected on the master switch
                queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
                cursor.execute(queryStr)
                vsfmasterResult=cursor.fetchall()
                # Obtain the firmware version from the member switch
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                # Obtain the image file name from the master switch
                queryStr="select filename from ztpimages where id='{}'".format(vsfmasterResult[0]['softwareimage'])
                cursor.execute(queryStr)
                imageResult=cursor.fetchall()
                # Formating the image name so that we can compare with the information from the rest call
                imagename="FL."+imageResult[0]['filename'].split('_',2)[2].rsplit('.',1)[0].replace("_",".")
                if imagename==response['current_version']:
                    # There is no need to upgrade the switch. Switch is already running on the right software
                    logEntry(items['id'],"Stage 2: {} is already on the right software".format(items['ipaddress']), cursor)
                    ztpstatus="Switch running on " + imagename + ". Configure VSF"
                    queryStr="update ztpdevices set enableztp=24, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                else:
                    # Switch is not running on the right software, we need to upgrade.
                    logEntry(items['id'],"Stage 2: Upgrade {} with software {}".format(items['ipaddress'],imagename), cursor)
                    url="firmware?image=primary&from=http://" + hostip + "/images/" + imageResult[0]['filename'] + "&vrf=" + credentialResult[0]['vrf']
                    response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                    ztpstatus="Upgrade switch to " + imagename
                    queryStr="update ztpdevices set enableztp=21, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
            else:
                # VSF is not activated on this switch, go to the next stage
                queryStr="update ztpdevices set enableztp=4 where id='{}'".format(items['id'])
                cursor.execute(queryStr)
                # Next step is to verify whether there is a software image assigned to the non VSF or master device. If this is the case, we need to check whether the switch is already running this code
                # If this is the case, go to the next step, which is the configuration template provisioning, which is step 8

        elif items['enableztp']==21:
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response['status']=="success":
                # upgrade is successful to the primary image. We now have to reboot the switch on the primary image
                url="boot?image=primary"
                response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                ztpstatus="Upgrade successful, preparing for reboot"
                queryStr="update ztpdevices set enableztp=22, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            elif response['status']=="in_progress":
                ztpstatus="Upgrade in progress"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==22:
            logEntry(items['id'],"Stage 2c: Waiting for {} to reboot".format(items['ipaddress']), cursor)
            # The switch does not reboot straight away. We have to wait until the switch reboots and then go to the next stage
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if not bool(response):
                ztpstatus="Rebooting switch"
                queryStr="update ztpdevices set enableztp=23, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==23:
            logEntry(items['id'],"Stage 2d: Switch is rebooting, check when {} is back online again".format(items['ipaddress']), cursor)
            # print ("Stage 2d: Switch is rebooting, check when ",items['ipaddress']," is back online again")
            # Switch is rebooting. We need to perform rest calls to check whether the switch is back online
            url="firmware"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response:
                ztpstatus="Upgrade member switch successful. Configure VSF"
                queryStr="update ztpdevices set enableztp=24, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==24:
            ztpstatus="Configure VSF"
            queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
            cursor.execute(queryStr)
            # VSF is enabled and the switch is not a master
            # We have to push the ID and VSF port information to the switch. At the moment this can only be done through SSH.
            try:
                client=SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy)
                client.connect(items['ipaddress'],username=credentialResult[0]['username'],password=credentialResult[0]['password'])
                connection=client.invoke_shell()
                connection.send("\n")
                time.sleep(1)
                connection.send("configure terminal\n")
                time.sleep(1)
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
                renumberCmd="vsf renumber-to " + str(items['vsfmember']) + "\n"
                connection.send(renumberCmd)
                time.sleep(4)
                connection.send('y\n')
                time.sleep(3)
                output = connection.recv(65532).decode(encoding='utf-8')
                print(output)
                try:
                    connection.close()
                    client.close()
                except:
                    pass
                # If the output contains 'transaction success', VSF is provisioned and the switch is rebooting
                # Setting the ZTP status to 3, this is a substage, waiting until the switch comes back. When the switch is back online, we need to verify the VSF status
                if "transaction success" in output:
                    logEntry(items['id'],"VSF has been deployed to the member switch, rebooting switch", cursor)
                    ztpstatus=""
                    queryStr="update ztpdevices set enableztp=3, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
            except:
                logEntry(items['id'],"There is an issue configuring VSF on the member switch", cursor)
                # print("There is an issue configuring VSF on the member switch")
                ztpstatus="Error provisioning VSF to the member switch"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)

        elif items['enableztp']==3:
            # First we need to check whether the master is online and whether the VSF has been formed. We need to get the master switch IP address and profile (for the credentials...)
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            vsfmasterResult=cursor.fetchall()
            # And the ZTP profile for the credentials
            queryStr="select * from ztpprofiles where id='{}'".format(vsfmasterResult[0]['profile'])
            cursor.execute(queryStr)
            masterprofileResult=cursor.fetchall()
            masterprofileResult[0]['password'] = decryptPassword(globalconf['secret_key'], masterprofileResult[0]['password'])
            # Now that we have all the information, get the VSF status from the master
            url="system/vsf_members/"+str(items['vsfmember'])
            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],masterprofileResult[0]['username'],masterprofileResult[0]['password'],url)
            if "status" in response:
                if response['status']=="ready":
                    logEntry(items['id'],"Stage 3: The VSF member switch has joined the VSF stack", cursor)
                    # We also have to check whether the role of the member switch is secondary, if that is the case we have to configure this on the master
                    ztpstatus="Member switch has joined the VSF"
                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                    if items['vsfrole']=="Secondary":
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
                                connection.send('y\n')
                                time.sleep(3)
                                ztpstatus="Member is designated secondary switch"
                                queryStr="update ztpdevices set enableztp=31, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr)
                            else:
                                # Secondary is already configured. Now check the VSF status again. If the member is up and running again, we can set the status to completed
                                url="system/vsf_members/"+str(items['vsfmember'])
                                response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],masterprofileResult[0]['username'],masterprofileResult[0]['password'],url)
                                if response['status']=="ready":
                                    # It is done. The member switch has been provisioned
                                    ztpstatus="ZTP completed"
                                    queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                    logEntry(items['id'],"ZTP provisioning successful", cursor)
                                    cursor.execute(queryStr)
                            connection.close()
                            client.close()  
                        except:
                            logEntry(items['id'],"There is an issue configuring the secondary member of the VSF", cursor)
                            # print("There is an issue configuring the secondary member of the VSF")
                    else:
                        ztpstatus="ZTP completed"
                        queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        logEntry(items['id'],"ZTP provisioning successful", cursor)
                        # print("ZTP provisioning successful")
                        cursor.execute(queryStr)
        elif items['enableztp']==31:
            # This is when the VSF secondary member has been configured. This action reboots the secondary switch so we need to check when the secondary switch is back online again
            # Then check the VSF status, whether the member switch has joined. Once it has joined, the ZTP process was successful
            logEntry(items['id'],"Stage 3a: Check secondary member status", cursor)
            # print("Stage 3a: Check secondary member status")
            queryStr="select * from ztpdevices where id='{}'".format(items['vsfmaster'])
            cursor.execute(queryStr)
            vsfmasterResult=cursor.fetchall()
            # And the ZTP profile for the credentials
            queryStr="select * from ztpprofiles where id='{}'".format(vsfmasterResult[0]['profile'])
            cursor.execute(queryStr)
            masterprofileResult=cursor.fetchall()
            masterprofileResult[0]['password'] = decryptPassword(globalconf['secret_key'], masterprofileResult[0]['password'])
            # Now that we have all the information, get the VSF status from the master
            url="system/vsf_members/"+str(items['vsfmember'])
            response=getRESTcxIP(vsfmasterResult[0]['ipaddress'],masterprofileResult[0]['username'],masterprofileResult[0]['password'],url)
            if "status" in response:
                if response['status']=="ready":
                    # ZTP for the VSF secondary switch has completed. We now have to save the running config on the master switch
                    url="fullconfigs/startup-config?from=%2Frest%2Fv1%2Ffullconfigs%2Frunning-config"
                    response=putRESTcxIP(vsfmasterResult[0]['ipaddress'],masterprofileResult[0]['username'],masterprofileResult[0]['password'],url,'')
                    if response==200:
                        ztpstatus="ZTP completed"
                        queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                        logEntry(items['id'],"ZTP provisioning successful", cursor)
                        print("ZTP provisioning successful")
                        cursor.execute(queryStr)

        elif items['enableztp']==4:
            logEntry(items['id'],"Stage 4: Checking whether the switch requires a software image", cursor)
            # print("Stage 4: Checking whether there is a software image")
            if items['softwareimage']:
                logEntry(items['id'],"Stage 4: There is a software image configured for this device", cursor)
                # print("Stage 4: There is a software image attached")
                # There is an image attached. First check whether it is required to upgrade the switch or whether the switch is already running the right code
                url="firmware"
                response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
                # Obtain the image file name
                queryStr="select filename from ztpimages where id='{}'".format(items['softwareimage'])
                cursor.execute(queryStr)
                imageResult=cursor.fetchall()
                # Formating the image name so that we can compare with the information from the rest call
                imagename="FL."+imageResult[0]['filename'].split('_',2)[2].rsplit('.',1)[0].replace("_",".")
                if imagename==response['current_version']:
                    # There is no need to upgrade the switch. Switch is already running on the right software
                    logEntry(items['id'],"Stage 4: {} already on the right software".format(items['ipaddress']), cursor)
                    # print("Stage 4: ",items['ipaddress'], " already on the right software")
                    ztpstatus="Switch running on " + imagename + ". Provisioning configuration template"
                    queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
                else:
                    # Switch is not running on the right software, we need to upgrade.
                    url="firmware?image=primary&from=http://" + hostip + "/images/" + imageResult[0]['filename'] + "&vrf=" + credentialResult[0]['vrf']
                    response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                    ztpstatus="Upgrade switch to " + imagename
                    queryStr="update ztpdevices set enableztp=5, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                    cursor.execute(queryStr)
            else:
                # There is no image attached to the device. No need to upgrade
                logEntry (items['id'],"Stage 4: There is no software image attached, going to stage 8", cursor)
                # print ("Stage 4: There is no software image attached, going to stage 8")
                ztpstatus="Provisioning configuration template"
                queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==5:
            # Switch is upgrading. Need to check the status
            logEntry(items['id'],"Stage 5: {} is upgrading, checking the status".format(items['ipaddress']), cursor)
            # print("Stage 5: ",items['ipaddress']," is upgrading, checking the status")
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response['status']=="success":
                # upgrade is successful to the primary image. We now have to reboot the switch on the primary image
                url="boot?image=primary"
                response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                ztpstatus="Upgrade successful, preparing for reboot"
                queryStr="update ztpdevices set enableztp=6, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
            elif response['status']=="in_progress":
                ztpstatus="Upgrade in progress"
                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==6:
            logEntry(items['id'],"Stage 6: Waiting for {} to reboot".format(items['ipaddress']), cursor)
            # print("Stage 6: Waiting for ",items['ipaddress']," to reboot")
            # The switch does not reboot straight away. We have to wait until the switch reboots and then go to the next stage
            url="firmware/status"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if not bool(response):
                ztpstatus="Rebooting switch"
                queryStr="update ztpdevices set enableztp=7, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==7:
            logEntry (items['id'],"Stage 7: Switch is rebooting, check when {} is back online again".format(items['ipaddress']), cursor)
            # print ("Stage 7: Switch is rebooting, check when ",items['ipaddress']," is back online again")
            # Switch is rebooting. We need to perform rest calls to check whether the switch is back online
            url="firmware"
            response=getRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url)
            if response:
                ztpstatus="Upgrade successful. Provisioning template."
                queryStr="update ztpdevices set enableztp=8, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                cursor.execute(queryStr)
        elif items['enableztp']==8:
            # The switch is back online. We need to check whether there is a template with parameters, if there is construct the template and then push it to the switch
            # This is an important stage. We first need to check whether VSF is enabled for this switch. If it is enabled, we need to check whether it is the master, secondary or member switch
            # If it is the master, we need to provision, just like a standalone switch, but after configuration push we need to assign the VSF ports
            # If it is a member or secondary switch, we only push the member id and VSF ports, then the switch should reboot and eventually join the stack
            if (items['vsfenabled']==1 and items['vsfmaster']!=0):
                logEntry(items['id'],"VSF is enabled and this is a member or secondary switch", cursor)
                # print("VSF is enabled and this is a member or secondary switch")
                # VSF Member or Secondary. We only push the member id, VSF ports and optionally the secondary role
            else:
                logEntry(items['id'],"Stage 8: Push configuration template to {}".format(items['ipaddress']), cursor)
                # print("Stage 8: Push configuration template to ", items['ipaddress'])
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
                            logEntry(items['id'],"The push to the running configuration was successful. Now put the configuration in the startup", cursor)
                            # print("The push to the running configuration was successful. Now put the configuration in the startup")
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
                                    # ZTP was successful. Final check is to see whether this switch has VSF enabled and is master switch. If it is, we need to push the VSF ports
                                    if items['vsfenabled']==1 and items['vsfmaster']==0:
                                        # This is a VSF master
                                        logEntry(items['id'],"Switch is VSF master. Provision the VSF ports", cursor)
                                        # print("Switch is VSF master. Provision the VSF ports")
                                        ztpstatus="Configure VSF Master"
                                        queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        cursor.execute(queryStr)
                                        # First, delete the links if they exist
                                        response=deleteRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],"system/vsf_members/1/links/1")
                                        response=deleteRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],"system/vsf_members/1/links/2")
                                        # Now put the links, we need to generate the JSON
                                        link1=json.loads(items['link1'])
                                        link2=json.loads(items['link2']) 
                                        if len(link1)>0:
                                            link1Json="{\"id\": 1,\"interfaces\": ["
                                            for l1Items in link1:
                                                link1Json+="\"/rest/v1/system/interfaces/" + l1Items +"\","
                                            link1Json=link1Json[:-1]+"]}"
                                            logEntry(items['id'],"Stage 8: Store into running configuration", cursor)
                                            # print("Stage 8: Store into running configuration")
                                            response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],"system/vsf_members/1/links",link1Json)
                                        if len(link2)>0:
                                            link2Json="{\"id\": 2,\"interfaces\": ["
                                            for l2Items in link2:
                                                link2Json+="\"/rest/v1/system/interfaces/" + l2Items + "\","
                                            link2Json=link2Json[:-1]+"]}"
                                            response=postRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],"system/vsf_members/2/links",link2Json)
                                        logEntry(items['id'],"Stage 8: Store the VSF Master configuration in the startup config", cursor)
                                        # print("Stage 8: Store the VSF Master configuration in the startup config")
                                        url="fullconfigs/startup-config?from=%2Frest%2Fv1%2Ffullconfigs%2Frunning-config"
                                        response=putRESTcxIP(items['ipaddress'],credentialResult[0]['username'],credentialResult[0]['password'],url,'')
                                        if response==200:
                                            ztpstatus="ZTP completed"
                                            queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                            logEntry(items['id'],"ZTP provisioning successful", cursor)
                                            # print("ZTP provisioning successful")
                                            cursor.execute(queryStr)
                                    else:
                                        ztpstatus="ZTP completed"
                                        queryStr="update ztpdevices set enableztp=100, ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                        logEntry(items['id'],"ZTP provisioning successful", cursor)
                                        # print("ZTP provisioning successful")
                                        cursor.execute(queryStr)
                                else:
                                    # Seems that the switch is not reachable anymore. Update the status.
                                    ztpstatus="Switch is not reachable anymore, retrying.."
                                    logEntry(items['id'],"Switch is not reachable anymore, retrying..", cursor)
                                    queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                    cursor.execute(queryStr)
                            else:
                                # Configuration not pushed to the switch, something went wrong with the push. We need to try again
                                ztpstatus="Could not push the configuration template, retrying.."
                                logEntry(items['id'],"Could not push the configuration template, retrying..", cursor)
                                queryStr="update ztpdevices set ztpstatus='{}' where id='{}'".format(ztpstatus,items['id'])
                                cursor.execute(queryStr) 
                    except:
                        logEntry(items['id'],"Stage 8: Error pushing configuration template to running configuration {}".format(items['ipaddress']), cursor)
    
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
            print("Error obtaining response from get call")
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
        # There is a log entry. We need to check whether the last message is the same message as the current one. If it is not, then update
        logging=json.loads(result[0]['logging'])
        lastEntry=logging[len(logging)-1]['logEntry']
        if logging[len(logging)-1]['logEntry']!=message:
            # The last entry is not the same, we can update
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            logEntry={"datetime": timestamp ,"logEntry": message}
            logging.append(logEntry)
            queryStr="update ztplog set logging='{}' where ztpdevice='{}'".format(json.dumps(logging),ztpdevice)
            cursor.execute(queryStr)

        
