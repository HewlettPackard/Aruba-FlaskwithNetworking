# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Kill Websocket client

import psutil, sys, os, platform, subprocess, socket
from subprocess import Popen, PIPE
import pymysql.cursors

dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)

for proc in psutil.process_iter():
    processname="/var/www/html/bash/wsclient"
    cmdline=proc.cmdline()
    if len(cmdline)>1:
        if processname in cmdline[1]:
            if sys.argv[1]==cmdline[2]:
                proc.kill()
                # Update the database and clear the subscriber information
                queryStr="update devices set subscriber='' where id='{}'".format(sys.argv[1])
                cursor.execute(queryStr)
