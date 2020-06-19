# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from datetime import date, datetime, time, timedelta
import time
import json
import pymysql.cursors
import re
import sys
import os
import platform
import requests
import urllib3
from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sessionid = requests.Session()

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def cleanupTrackers():
    # Cleaning up the trackers
    cleanuplog = open('/var/www/html/log/cleanup.log', 'a')
    cleanuplog.write('{}: Running trackers cleanup process. \n'.format(datetime.now()))
    cleanuplog.close()
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    pathname = os.path.dirname(sys.argv[0])
    appPath = os.path.abspath(pathname) + "/globals.json"
    # Purge entries from DHCP, Syslog and SNMP which are older than configured values
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    queryStr="DELETE FROM `snmptracker` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_snmp']))))
    cursor.execute(queryStr)
    queryStr="DELETE FROM `dhcptracker` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_dhcp']))))
    cursor.execute(queryStr)
    queryStr="DELETE FROM `syslog` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_syslog']))))
    cursor.execute(queryStr)
    # Cleaning up the logs
    currentTime=int(time.time())

def cleanupLogging():
    cleanuplog = open('/var/www/html/log/cleanup.log', 'a')
    cleanuplog.write('{}: Running logfile cleanup process. \n'.format(datetime.now()))
    cleanuplog.close()
    #Get the timestamp of minus 24 hours 
    oneday=int((datetime.now() - timedelta(hours=24)).timestamp())
    pathname = os.path.dirname(sys.argv[0])
    appPath = os.path.abspath(pathname) + "/globals.json"
    # Purge entries from DHCP, Syslog and SNMP which are older than configured values
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    # Log files list
    logFiles=["cleanup.log","topology.log","ztp.log","listener.log"]
    for items in logFiles:
        timestampList=[]
        # Go through the logfiles and perform 2 actions:
        # If it is midnight (or past midnight), create a new timestamp line (append)
        # Check the retain values of the log file. Older data needs to be removed from the file
        logFile = globalconf['appPath']+ "/log/" + items
        # First, get all the timestamp from the logfile and then add 86400 to the last item. If the sum is smaller than the timestamp
        # Then a day has past and we need to add a new timestamp to the logfile
        with open(logFile,'r') as checklog:
            datafile = checklog.readlines()
            for line in datafile:
                if "---" in line:
                    # Found a timestamp. Obtain the timestamp value from the line and add it to the list
                    ts=line[:-3]
                    ts = ts.replace("-", "")
                    timestampList.append(int(ts))
        # Close the file
        checklog.close()
        # Now that we have all the timestamps, we need to get the last entry and check if there is more than 24 hours difference
        # But first check if the log has a timestamp entry at all
        if len(timestampList)==0:
            # The logfile is completely empty. We need to add the timestamp
            checklog=open(logFile,'w')
            checklog.write('\n---'+str(int(datetime.now().timestamp()))+'---\n')
            clecklog.close()
        elif oneday>timestampList[len(timestampList)-1]:
            # Another day has gone by. Add the new timestamp
            checklog=open(logFile,'a')
            checklog.write('\n---'+str(int(datetime.now().timestamp()))+'---\n')
            # Close the file
            checklog.close()
        # Next is to verify the retain days for the log and remove the information that should not be retained
        # We only have to do this when the number of timestamp entries in the log is bigger than the retain value
        retain=items.split(".")
        retain="retain_"+retain[0]+"log"
        if len(timestampList)>int(globalconf[retain]):
            splitTimestamp="---"+str(timestampList[len(timestampList)-int(globalconf[retain])-1])+"---"
            # First open the file and split on the splitTimestamp
            checklog=open(logFile,'r')
            logInfo=checklog.read()
            tsData=logInfo.split(splitTimestamp)
            checklog.close()
            # Now Open the file again for write, and only write the last section
            checklog=open(logFile,'w')
            checklog.write(tsData[1])
            checklog.close()








