# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#/usr/bin/python3

import json
import pymysql.cursors

dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)

# Change the ztpprofile column to text instead of integer and rename to vrf
queryStr="show columns from ztpdevices"
cursor.execute(queryStr)
ztpdeviceColumns=cursor.fetchall()
adminuser=0
adminpassword=0
ztpdhcp=0
ztpvlan=0
for items in ztpdeviceColumns:
    if items['Field']=="profile":
        queryStr="ALTER TABLE `ztpdevices` CHANGE `profile` `vrf` TEXT NOT NULL"
        cursor.execute(queryStr)
    if "ztpdhcp" in items['Field']:
        ztpdhcp=1
    if "adminuser" in items['Field']:
        adminuser=1
    if "adminpassword" in items['Field']:
        adminpassword=1
    if "ztpvlan" in items['Field']:
        ztpvlan=1
if ztpdhcp==0:
    queryStr="ALTER TABLE `ztpdevices` ADD `ztpdhcp` INT NOT NULL AFTER `ztpstatus`"
    cursor.execute(queryStr)
if adminuser==0:
    queryStr="ALTER TABLE `ztpdevices` ADD `adminuser` TEXT NOT NULL AFTER `ztpdhcp`"
    cursor.execute(queryStr)
if adminpassword==0:
    queryStr="ALTER TABLE `ztpdevices` ADD `adminpassword` TEXT NOT NULL AFTER `adminuser`"
    cursor.execute(queryStr)
if ztpvlan==0:
    queryStr="ALTER TABLE `ztpdevices` ADD `ztpvlan` TEXT NULL AFTER `adminpassword`"
    cursor.execute(queryStr)
# Rename the websocketconnect column name in devices to telemetryenable
queryStr="show columns from devices"
cursor.execute(queryStr)
deviceColumns=cursor.fetchall()
for items in deviceColumns:
    if items['Field']=="websocketconnect":
        queryStr="ALTER TABLE `devices` CHANGE `websocketconnect` `telemetryenable` INT UNSIGNED NULL DEFAULT NULL"
        cursor.execute(queryStr)
# Add three columns for the telemetry features
if not any(d['Field'] == 'switchstatus' for d in deviceColumns):
    queryStr="ALTER TABLE `devices` ADD `switchstatus` INT UNSIGNED NULL DEFAULT NULL AFTER `telemetryenable`"
    cursor.execute(queryStr)
if not any(d['Field'] == 'subscriptions' for d in deviceColumns):
    queryStr="ALTER TABLE `devices` ADD `subscriptions` TEXT NULL AFTER `switchstatus`"
    cursor.execute(queryStr)
if not any(d['Field'] == 'subscriber' for d in deviceColumns):
    queryStr="ALTER TABLE `devices` ADD `subscriber` TEXT NULL AFTER `subscriptions`"
    cursor.execute(queryStr)

# Update the vrf information in ztpdevice. For all devices where DHCP is used for ZTP, the VRF column can be empty
queryStr="update ztpdevices set vrf='0' where ztpdhcp='1'"
cursor.execute(queryStr)
# For all the ztp devices that have a ztp profile assigned, we need to change the information in the VRF column to reflect the ztpprofile information
queryStr="select id, vrf from ztpdevices where ztpdhcp='0'"
cursor.execute(queryStr)
vrfResult=cursor.fetchall()
queryStr="SELECT count(*) as ztpprofile FROM information_schema.TABLES WHERE (TABLE_SCHEMA = 'aruba') AND (TABLE_NAME = 'ztpprofiles')"
cursor.execute(queryStr)
ztpprofileExist=cursor.fetchall()
if ztpprofileExist[0]['ztpprofile']==1:
    try:
        for items in vrfResult:
            try:
                queryStr="select vrf from ztpprofiles where id='{}'".format(int(items['vrf']))
                cursor.execute(queryStr)
                vrf=cursor.fetchall()
                # Update the ztpdevice table
                queryStr="update ztpdevices set vrf='{}' where id='{}'".format(vrf[0]['vrf'],items['id'])
                cursor.execute(queryStr)
            except:
                pass
        # Once the column information is migrated, drop the ztpprofiles table
        try:
            queryStr="drop table if EXISTS ztpprofiles"
            cursor.execute(queryStr)
        except:
            pass
    except:
        print("Error migrating the database")
try:
    queryStr="drop table if EXISTS sysrole"
    cursor.execute(queryStr)
    queryStr="CREATE TABLE `sysrole` (`id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,`name` text NOT NULL,`accessrights` text NOT NULL,`status` int NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"
    cursor.execute(queryStr)
    # Create the role
    queryStr="INSERT INTO `sysrole` (`name`, `accessrights`, `status`) VALUES ('Administrator', '{\"devices\": \"on\", \"switchaccess\": \"2\", \"mobilityaccess\": \"2\", \"clearpassaccess\": \"2\", \"ztp\": \"on\", \"ztpimageaccess\": \"2\", \"ztptemplateaccess\": \"2\", \"ztpdeviceaccess\": \"2\", \"topology\": \"on\", \"telemetry\": \"on\", \"telemetrymonitoraccess\": \"2\", \"telemetrysubscriptionaccess\": \"2\", \"ubt\": \"on\", \"ubtprofileaccess\": \"2\", \"ubtserviceaccess\": \"2\", \"trackers\": \"on\", \"dhcptrackeraccess\": \"2\", \"snmptrackeraccess\": \"2\", \"syslogtrackeraccess\": \"2\", \"tools\": \"on\", \"anycliaccess\": \"2\", \"administration\": \"on\", \"sysuseraccess\": \"2\", \"sysroleaccess\": \"2\", \"sysadminaccess\": \"2\", \"servicesstatusaccess\": \"2\"}', 1);"
    cursor.execute(queryStr)
    # Update the administrator account, assign the right role to the account
    queryStr="update sysuser set role='1' where username='admin'"
    cursor.execute(queryStr)
except:
    print("There is a problem creating the user role table")

sysvars = open("/var/www/html/bash/globals.json", "r")
data = json.load(sysvars) 
sysvars.close()
data["softwareRelease"] = "2.1"
data["landingpage"]="/"
data['ztppassword']="ztpinit"
data['retain_ztplog']="5"
data['retain_cleanuplog']="5"
data['retain_listenerlog']="5"
data['retain_topologylog']="5"
data['retain_telemetrylog']="5"
data['authsource']="local"
sysvars = open("/var/www/html/bash/globals.json", "w+")
sysvars.write(json.dumps(data))
sysvars.close()
cursor.close()