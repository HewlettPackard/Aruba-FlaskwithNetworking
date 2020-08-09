# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#!/usr/bin/python3


import psutil, sys, os, platform, subprocess
from subprocess import Popen, PIPE
import psutil, sys, os, platform, websockets, ssl, asyncio, pathlib, requests, json, pymysql.cursors
import urllib3
from datetime import datetime, timedelta
import paramiko
import time
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)


pathname = os.path.dirname(sys.argv[0])
appPath = os.path.abspath(pathname) + "/globals.json"
with open(appPath, 'r') as myfile:
    data=myfile.read()
globalconf=json.loads(data)


dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
cursor=dbconnection.cursor(pymysql.cursors.DictCursor)


# When launching the telemetry service, we also need to run the telemetryclasses.py script. Before we do, this we need to check whether this is already running
# If it is running, kill the process


connected=set()


async def server (websocket,path):
    # Before adding 
    if not websocket in connected:
        connected.add(websocket)
    try:
        async for message in websocket:
            for conn in connected:
                # The IP address of the "multicast" group can be found in the cookie section
                # If it is a connection from a browser, the cookie attribute is telemetryIP
                # If it is a connection coming from the Python websocket client
                if "Cookie" in conn.request_headers:
                    # This comes from a browser. We need to split the cookie based on ; and find the telemetryIP entry
                    # Then we need to check whether the client connection is for the right switch. If it is, forward the notification from the switch
                    wsBrowser = conn.request_headers['Cookie'].split(";")
                    await conn.send(message)
                    # This notification comes from the switch. We need to go through the connection list again and only forward this message to the clients that are
                    # registered with the IP address of the switch                                   
    finally:
        connected.remove(websocket)


async def checkCookie(cursor, globalconf):
    while True:
        await asyncio.sleep(2)
        websocketlog = open('/var/www/html/log/telemetry.log', 'a')
        # First step is to get all the devices from the database that have telemetry (websocketconnect) enabled
        queryStr="select id, ipaddress,username, description,password,secinfo, switchstatus from devices where telemetryenable='1' and ostype='arubaos-cx'"
        cursor.execute(queryStr)
        result = cursor.fetchall()
        for items in result:
            try:
                password=await decryptPassword(globalconf['secret_key'], items['password']) 
                # For each switch we need to check if the cookie is still valid. If not, we have to login and store the cookie value in the database
                baseurl="https://{}/rest/v1/".format(items['ipaddress']) 
                if items['secinfo'] is None:
                    # There is no cookie in the secinfo field, we HAVE to login
                    credentials={'username': items['username'],'password': decryptPassword(globalsconf['secret_key'], items['password']) }
                    try:
                        # Login to the switch. The cookie value is stored in the session cookie jar
                        response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                        if "set-cookie" in response.headers:
                            # There is a cookie, so the login was successful. We need to update the database
                            cookie_header = {'Cookie': response.headers['set-cookie']}
                        elif "session limit reached" in response.text:
                            cs=await clearSessions(items['ipaddress'], items['username'],decryptPassword(globalsconf['secret_key'], items['password']))
                            if cs=="ok":
                                response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                                if "set-cookie" in response.headers:
                                    cookie_header = {'Cookie': response.headers['set-cookie']}
                                else:
                                    cookie_header=""
                        else:
                            queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,items['id'])
                            cursor.execute(queryStr)
                        queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,items['id'])
                        cursor.execute(queryStr)
                    except:
                        # Something went wrong with the login
                        queryStr="update devices set switchstatus=100 where id='{}'".format(items['id'])
                        cursor.execute(queryStr)
                else:
                    try:
                        if type(items['secinfo']) is dict:
                            header=items['secinfo']
                        else:
                            header=json.loads(items['secinfo'])
                        try:
                            response=requests.get(baseurl+"system?attributes=software_info&depth=2",headers=header,verify=False,timeout=5)
                            if response.status_code==200:
                                # The cookie is still valid, return the cookie that is stored in the database
                                if items['switchstatus']!=200:
                                    queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,items['id'])
                                    cursor.execute(queryStr)
                            else:
                                # There is something wrong with the cookie, might be expired or the switch may be out of sessions
                                # If the latter is the case, we need to SSH into the switch and reset the sessions, then try to login again and get the cookie
                                # There could also be an authentication failure, if that is the case, we should return that result code
                                if "Authorization Required" in response.text:
                                    # Need to login and store the cookie
                                    credentials={'username': items['username'],'password': decryptPassword(globalsconf['secret_key'], items['password']) }
                                    response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                                    if "set-cookie" in response.headers:
                                        cookie_header = {'Cookie': response.headers['set-cookie']}
                                        queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),items['id'])
                                        cursor.execute(queryStr)  
                                    else:
                                        queryStr="update devices set secinfo='', switchstatus={} where id='{}'".format(response.status_code,items['id'])
                                        cursor.execute(queryStr)                      
                                elif "session limit reached" in response.text:
                                    websocketlog.write('{}: Maximum number of HTTPS sessions reached for {} ({}). Clearing sessions\n'.format(datetime.now(),items['ipaddress'],items['description']))
                                    cs=clearSessions(items['ipaddress'], items['username'],decryptPassword(globalsconf['secret_key'], items['password']))
                                    if cs=="ok":
                                        response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                                        if "set-cookie" in response.headers:
                                            cookie_header = {'Cookie': response.headers['set-cookie']}
                                            queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),items['id'])
                                            cursor.execute(queryStr)
                                        else:
                                            queryStr="update devices set secinfo='', switchstatus={} where id='{}'".format(response.status_code,items['id'])
                                            cursor.execute(queryStr)                     
                                else:
                                    queryStr="update devices set switchstatus=120 where id='{}'".format(items['id'])
                                    cursor.execute(queryStr)
                        except:
                            if items['switchstatus']>100 and items['switchstatus']<103:
                                switchstatus=items['switchstatus']-1
                            else:
                                switchstatus=100
                            websocketlog.write('{}: Something went wrong with the authentication verification\n'.format(datetime.now()))
                            queryStr="update devices set switchstatus={} where id='{}'".format(switchstatus,items['id'])
                            cursor.execute(queryStr)
                    except:
                        pass
            except:
                pass
        websocketlog.close()

async def checkWS(cursor,globalconf):
    while True:
        await asyncio.sleep(2)
        try:
            queryStr="select id, ipaddress,secinfo,switchstatus,subscriber, subscriptions from devices where telemetryenable='1' and switchstatus=200 and ostype='arubaos-cx' and CHAR_LENGTH(subscriptions) > 8"
            cursor.execute(queryStr)
            result = cursor.fetchall()
            # Check if there are any active subscriptions
            for items in result:
                subscriptions=json.loads(items['subscriptions'])
                activeSubscription=0
                for subitems in subscriptions[0]:
                    if subitems['status']=="1":
                        activeSubscription=1;
                # if there are no active subscriptions, do nothing
                if activeSubscription==1 and subscriptions[1]==0:
                    # Now we need to check if the wsclient is already running. If it is running, do nothing. If it is not running, start the wsclient
                    # Check is done by checking the subscriber ID with the switch
                    uri="https://{}/rest/v1/system/notification_subscribers?attributes=name&filter=name:{}&depth=2".format(items['ipaddress'],items['subscriber'])
                    try:
                        response=requests.get(uri,headers=json.loads(items['secinfo']),verify=False,timeout=5)
                        response=json.loads(response.text)
                        # If the response is not empty, we are good with the subscriber. If it is not empty, we need to obtain a new subscriber. This means restarting the wsclient
                        # When the wsclient restarts, the client updates the subscriber information in the database
                        if len(response)==0:
                            # Response is empty, this means that the subscriber is not valid anymore and we have to restart the wsclient.
                            # We only have to restart if the wsclient is running
                            if await checkRunningws(items['id'])=="ok":
                                # wsclient is already running, stop it
                                await stopwsClient(items['id'])
                            await startwsClient(items['id'])
                            await asyncio.sleep(2)
                    except:
                        # There is something wrong with the verification. It could be that the subscriber does not exist. We will force a restart of the client
                        await stopwsClient(items['id'])
                        await startwsClient(items['id'])
                        pass

                # Also, we need to check if one of the subscriptions has changed. If that is the case, we need to restart the wsclient
                elif subscriptions[1]==1:
                    try:
                        # Another check, if there are no active subscriptions for this device anymore, there is no need to start the wsclient
                        if await checkRunningws(items['id'])=="ok":
                            # wsclient is already running, stop it
                            await stopwsClient(items['id'])
                        activeSubscription=0
                        for subitems in subscriptions[0]:
                            if subitems['status']=="1":
                                activeSubscription=1;
                        if activeSubscription==1:
                            await startwsClient(items['id'])
                        await asyncio.sleep(2)
                    except:
                        pass
        except:
            pass


async def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()


async def clearSessions(ipaddr, username,password):
    try:
        remoteclient=paramiko.SSHClient()
        remoteclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remoteclient.connect(ipaddr,username=username,password=password, timeout=5)
        # Logging in could take some time. Pause a bit
        sleep(5)
        connection=remoteclient.invoke_shell()
        connection.send("\n")
        sleep(3)
        connection.send("https session close all\n")
        sleep(3)
        connection.close()
        remoteclient.close()
        return "ok"
    except:
        return "nok"


async def stopwsClient(deviceid):
    for proc in psutil.process_iter():
        if "python" in proc.name().lower():
            procinfo=psutil.Process(proc.pid)
            if len(procinfo.cmdline())>1:
                if procinfo.cmdline()[1]=="/var/www/html/bash/wsclient.py":
                    # If there is a wsclient process, the device id is also attached
                    if procinfo.cmdline()[2]==str(deviceid):
                        proc.kill()
                        await asyncio.sleep(2)


async def startwsClient(deviceid):
    scriptName="/var/www/html/bash/wsclient.py"
    args=["python3",scriptName,str(deviceid)]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    await asyncio.sleep(2)


async def checkRunningws(deviceid):
    for proc in psutil.process_iter():
        # Need to check whether the listener process or the scheduler process is queried
            if "python" in proc.name().lower():
                procinfo=psutil.Process(proc.pid)
                if len(procinfo.cmdline())>1:
                    if procinfo.cmdline()[1]=="/var/www/html/bash/wsclient.py":
                        # If there is a wsclient process, the device id is also attached
                        if procinfo.cmdline()[2]==str(deviceid):
                            return "ok"
    return "nok"


async def checkSocketserver():
    while True:
        await asyncio.sleep(10)
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


start_server = websockets.serve(server,"0.0.0.0",5000)               
loop = asyncio.get_event_loop()


try:
    asyncio.ensure_future(start_server)
    asyncio.ensure_future(checkCookie(cursor,globalconf))
    asyncio.ensure_future(checkWS(cursor,globalconf))
    asyncio.ensure_future(checkSocketserver())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()







