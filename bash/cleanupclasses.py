# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from datetime import datetime, time, timedelta
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

def cleanup():
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    pathname = os.path.dirname(sys.argv[0])
    if platform.system()=="Windows":
        appPath = os.path.abspath(pathname) + "\\globals.json"      
    else:
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
