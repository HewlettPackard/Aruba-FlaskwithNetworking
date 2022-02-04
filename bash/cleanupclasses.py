# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from datetime import date, datetime, time, timedelta
import time
import json
import pymysql.cursors
import re
import requests
import urllib3
from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import psutil, sys, os, platform, subprocess, socket
from subprocess import Popen, PIPE

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
    globalconf=obtainGlobalconf(cursor)
    # Purge entries from DHCP, Syslog and SNMP which are older than configured values
    queryStr="DELETE FROM `snmptracker` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_snmp']))))
    cursor.execute(queryStr)
    queryStr="DELETE FROM `dhcptracker` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_dhcp']))))
    cursor.execute(queryStr)
    queryStr="DELETE FROM `syslog` WHERE `utctime` < {}".format(datetime.timestamp(datetime.now() - timedelta(days=int(globalconf['retain_syslog']))))
    cursor.execute(queryStr)


def cleanupafcAudit():
    # Cleaning up the AFC audit log
    cleanuplog = open('/var/www/html/log/cleanup.log', 'a')
    cleanuplog.write('{}: Running AFC auditlog cleanup process. \n'.format(datetime.now()))
    cleanuplog.close()
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    globalconf=obtainGlobalconf(cursor)
    afcconf=obtainafcconf(cursor)
    # Purge entries from AFC audit log database
    queryStr="DELETE FROM afcaudit WHERE log_date < {}".format(int(datetime.timestamp(datetime.now() - timedelta(days=int(afcconf['auditpurge']))))*1000)
    cursor.execute(queryStr)


def cleanupLogging():
    cleanuplog = open('/var/www/html/log/cleanup.log', 'a')
    cleanuplog.write('{}: Running logfile cleanup process. \n'.format(datetime.now()))
    cleanuplog.close()
    #Get the timestamp of minus 24 hours 
    oneday=int((datetime.now() - timedelta(hours=24)).timestamp())
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    globalconf=obtainGlobalconf(cursor)
    # Purge entries from DHCP, Syslog and SNMP which are older than configured values
    # Log files list
    logFiles=["cleanup.log","topology.log","ztp.log","listener.log", "telemetry.log"]
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
            checklog.close()
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


def checkSocketserver():
    status=""
    # Check if the websocket server is running. If it is not running, we need to stop all the ws clients.
    # Once the websocket server is running again, the checkws definition should restart the sessions as well
    for proc in psutil.process_iter():
        # Need to check whether the listener process or the scheduler process is queried
            if "python" in proc.name().lower():
                procinfo=psutil.Process(proc.pid)
                if len(procinfo.cmdline())>1:
                    if "telemetry.py" in procinfo.cmdline()[1]:
                        # We are ok
                        status = "ok"
    # If the for next loop has returned nok, we have to kill all the websocket sessions because the socket server has stopped for some reason
    if status=="":
        for proc in psutil.process_iter():
            if "python" in proc.name().lower():
                procinfo=psutil.Process(proc.pid)
                if len(procinfo.cmdline())>1:
                    if procinfo.cmdline()[1]=="/var/www/html/bash/wsclient.py":
                        proc.kill()
        cleanuplog = open('/var/www/html/log/cleanup.log', 'a')
        cleanuplog.write('{}: Web Socket server is stopped. All websocket clients have been stopped. \n'.format(datetime.now()))
        cleanuplog.close()


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


def obtainafcconf(cursor):
    queryStr="select datacontent from systemconfig where configtype='sysafc'"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    afcconf=result[0]
    if isinstance(afcconf,str):
        afcconf=json.loads(afcconf)
    afcconf=afcconf['datacontent']
    if isinstance(afcconf,str):
        afcconf=json.loads(afcconf)
    return afcconf








