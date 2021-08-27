# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#/usr/bin/python3

import json
import pymysql.cursors

dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)

queryStr="show columns from deviceupdate"
cursor.execute(queryStr)
deviceupgradeColumns=cursor.fetchall()
if not any(d['Field'] == 'upgradeprofile' for d in deviceColumns):
    queryStr="ALTER TABLE `softwareupdate` ADD `upgradeprofile` BIGINT UNSIGNED NULL AFTER `endtime`;`"
    cursor.execute(queryStr)

try:
    queryStr="drop table if EXISTS upgradeprofiles"
    cursor.execute(queryStr)
    queryStr="CREATE TABLE `upgradeprofiles` (`id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,`name` text NOT NULL,`devicelist` text NOT NULL,`schedule` datetime DEFAULT NULL ,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"
    cursor.execute(queryStr)
    
except:
    print("There is a problem creating the device upgrade profiles table")


cursor.close()