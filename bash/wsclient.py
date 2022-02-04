# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3

import requests
import json
import pymysql.cursors
import sys
import os
import urllib3
import schedule
from datetime import datetime, time, timedelta
import time
import asyncio
import ssl
import pathlib
import websockets
import socket
import select
import errno

from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)

queryStr="select id,ipaddress,secinfo, subscriptions from devices where id='{}'".format(sys.argv[1])
cursor.execute(queryStr)
result = cursor.fetchall()

async def wsClient(id,ipaddr,uri,cookie_header, subscriptions, cursor):
    wscookie={'telemetryIP': ipaddr}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    telemetryURI = "ws://" + s.getsockname()[0] + ":5000"
    subscriptions=json.loads(subscriptions)
    try:
        async with websockets.connect(uri=uri, extra_headers=json.loads(cookie_header), ssl=ssl_context) as websocket, websockets.connect(uri=telemetryURI, extra_headers=wscookie) as CommPass:
            uri="https://{}/rest/v1/system/notification_subscribers?attributes=name%2Cnotification_subscriptions%2Ctype&depth=3".format(ipaddr)
            response=requests.get(uri,headers=json.loads(cookie_header),verify=False,timeout=10)
            # Subscribe to the active subscriptions (status = 1)
            for items in subscriptions[0]:
                if items['status']=="1":
                    sendMessage={"topics":[{"name":items['resource']}],"type":"subscribe"}
                    await websocket.send(json.dumps(sendMessage))
            while True:
                try:
                    message = await websocket.recv()
                    # We are still good on receiving messages
                    msgjson=json.loads(message)
                    # The message contains a "type" key value pair. type can have different values: success, notification, error
                    # We need to update the message values in the subscriptions, store this in the database
                    if msgjson['type']=="success":
                        for items in msgjson['data']:
                            if "topicname" in items:
                                # found the topic in the response
                                for i in range(len(subscriptions[0])): 
                                    if subscriptions[0][i]['resource']==items['topicname']:
                                        subscriptions[0][i]['message']="Success"  
                                subscriptions[1]=0
                                queryStr="update devices set subscriptions='{}' where id='{}'".format(json.dumps(subscriptions),id)
                                cursor.execute(queryStr)
                    if "subscriber_name" in msgjson:
                        # Update the database with the subscriber information
                        queryStr="update devices set subscriber='{}' where id='{}'".format(msgjson['subscriber_name'],id)
                        cursor.execute(queryStr)
                    message = {'ipaddress':ipaddr,'message': message }
                    await CommPass.send(json.dumps(message))
                except Exception as e:
                    print("Connection Reset Error: {}".format(e))
                    sys.exit()
    except ConnectionRefusedError as e:
        # We need to check which connection has failed, whether it is the connection to the CommPass server or the connection to the switch
        try:
            websocket
        except NameError:
            print("No connection to the switch")
        try:
            CommPass
        except NameError:
            print("No connection to the CommPass server")
        sys.exit()
    except Exception as e:
        print(e)


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(wsClient(result[0]['id'],result[0]['ipaddress'],"wss://{}:443/rest/v1/notification".format(result[0]['ipaddress']),result[0]['secinfo'], result[0]['subscriptions'], cursor))
    loop.run_forever()
except asyncio.CancelledError as e:
    print("Asyncio cancel error occured: {}".format(e))
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()

cursor.close()


