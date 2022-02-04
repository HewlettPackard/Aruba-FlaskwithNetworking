# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Pensando Services Manager classes
import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict

import classes.classes
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtainpsmToken(psmipaddress,psmusername,psmpassword):
    response={}
    try:
        url="https://" + psmipaddress + "/v1/login"
        credentials = {"username": psmusername, "password": psmpassword, "tenant": "default" }
        headers = CaseInsensitiveDict() 
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, data=json.dumps(credentials), verify=False, timeout=5)
        return response.headers
    except ConnectionError:
        response.update({"message":"Connection error, no response from PSM"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to PSM"})
        return response


def checkpsmToken(psmipaddress, psmtoken):
    psmvars=classes.classes.obtainVars('syspsm')
    if isinstance(psmvars,str):
        psmvars=json.loads(psmvars)
    response={}
    try:
        url="https://" + psmipaddress + "/configs/network/v1/tenant/default/networks"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        #headers["Authorization"] = psmtoken
        headers["Cookie"] = psmtoken
        result = requests.get(url, headers=headers, verify=False)
        if result.status_code==401:
            # the cookie has expired, obtain and store new cookie
            response=obtainpsmToken(psmvars['psmipaddress'],psmvars['psmusername'],psmvars['psmpassword'])
            if "Set-Cookie" in response:
                # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                # Result is the afctoken. We need to update the afcvars
                psmtoken=response['Set-Cookie'] + "; Domain: " + psmipaddress
                psmvars.update({'psmtoken': psmtoken })
                queryStr="update systemconfig set datacontent='{}' where configtype='syspsm'".format(json.dumps(psmvars))
                classes.classes.sqlQuery(queryStr,"update")
                try:
                    headers = CaseInsensitiveDict()
                    headers["Content-Type"] = "application/json"
                    headers['accept'] = "application/json; version=1.0"
                    #headers["Authorization"] = psmvars['psmtoken']
                    headers["Cookie"] = psmvars['psmtoken']
                    result = requests.get(url, headers=headers, verify=False)
                    response.update({"message":"Connection to PSM is successful","response": result})
                    return response
                except:
                    response.update({"message":"Cannot establish a connection with PSM","status_code": result.status_code})
                    return response
            else:
                response.update({"message":"Cannot establish a connection with PSM","status_code": result.status_code})
                return response
        else:
            response.update({"status_code": result.status_code})
            return response
    except ConnectionError:
        response.update({"message":"Connection error, no response from PSM"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to PSM"})
        return response


def getRestpsm(url):
    psmvars=classes.classes.obtainVars('syspsm')
    response={}
    if isinstance(psmvars,str):
        psmvars=json.loads(psmvars)
    if len(psmvars)>0:
        if not "psmtoken" in psmvars:
            response= obtainpsmToken(psmvars['psmipaddress'],psmvars['psmusername'], psmvars['psmpassword'])
            if isinstance(response,str):
                response=json.loads(response)
            psmvars.update({"psmtoken":response['result']})
            queryStr="update systemconfig set datacontent='{}' where configtype='syspsm'".format(json.dumps(psmvars))
            classes.classes.sqlQuery(queryStr,"update")
        url="https://" + psmvars['psmipaddress'] + "/" + url
        result={}
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["Cookie"] = psmvars['psmtoken']
        response=checkpsmToken(psmvars['psmipaddress'],psmvars['psmtoken'])
        if "status_code" in response:
            if response['status_code']==204 or response['status_code']==200:
                # Token seems to be valid, we can issue the query
                response = requests.get(url, headers=headers, verify=False)
                response = response.json()
                if "result" in response:
                    if response['result']=="Authentication credential is not valid; please log in again":
                        # Authorization token is still not valid. We need to refresh
                        response= obtainpsmToken(psmvars['psmipaddress'], psmvars['psmusername'], psmvars['psmpassword'])
                        if isinstance(response,str):
                            response = json.loads(response)
                        if "count" in response:
                            # Result is the psmtoken. We need to update the psmvars
                            psmvars.update({"psmtoken":response['result']})
                            queryStr="update systemconfig set datacontent='{}' where configtype='syspsm'".format(json.dumps(psmvars))
                            classes.classes.sqlQuery(queryStr,"update")
                        # And issue the get request again
                        headers["Cookie"] = psmvars['psmtoken']
                        response = requests.get(url, headers=headers, verify=False)
                    else:
                        response.update({"message":"Unable to obtain information, verify PSM credentials"})
            else:
                # Statuscode is not 204, try to refresh the token
                response= obtainpsmToken(psmvars['psmipaddress'], psmvars['psmusername'], psmvars['psmpassword'])
                if isinstance(response,str):
                    response = json.loads(response)
                if "count" in response:
                    # Result is the psmtoken. We need to update the psmvars
                    psmvars.update({"psmtoken":response['result']})
                    queryStr="update systemconfig set datacontent='{}' where configtype='syspsm'".format(json.dumps(psmvars))
                    classes.classes.sqlQuery(queryStr,"update")
                    # And issue the get request again
                    headers["Cookie"] = psmvars['psmtoken']
                    response = requests.get(url, headers=headers, verify=False)
                    response = response.json()
                else:
                    # There is something wrong with the connectivity, return an error
                    response.update({"message":"Unable to obtain information, verify PSM credentials"})
    else:
        response.update({"message":"PSM credentials do not exist"})
    return response