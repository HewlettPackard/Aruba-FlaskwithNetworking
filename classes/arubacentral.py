# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Aruba Central classes
import requests
from requests.auth import HTTPBasicAuth
import classes.classes
import urllib3
import json
from urllib.parse import urlencode, urlparse, urlunparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def centralAuthentication():
    print("Check Authentication")
    globalsconf=classes.classes.globalvars()
    url = globalsconf['centralurl'] + "/oauth2/authorize/central/api/login"
    login_params={"client_id":globalsconf['centralclientid']}
    payload={"username":globalsconf['centralusername'],"password": globalsconf['centraluserpassword']}
    try:
        response=requests.post(url,params=login_params,json=payload)
        if response.json()['status']==True:
            result={"message":"Authentication is successful","status":True}
            # Authentication is successful. We need to obtain the cookie values and store them in the variables file
            globalsconf.update({"arubacentralcsrftoken":response.cookies['csrftoken']})
            globalsconf.update({"arubacentralsession":response.cookies['session']})
            with open('bash/globals.json', 'w') as systemconfig:
                systemconfig.write(json.dumps(globalsconf))
        else:
            result=response.json()
    except Exception as err:
        result={"message":"Invalid parameters","status":False}
    return result


def centralAuthorization():
    print("Check authorization")
    globalsconf=classes.classes.globalvars()
    url = globalsconf['centralurl'] + "/oauth2/authorize/central/api"
    # Building the API call
    ses="session=" + globalsconf['arubacentralsession']
    headers={
        "X-CSRF-TOKEN": globalsconf['arubacentralcsrftoken'],
        "Content-type":"application/json",
        "Cookie":ses,
        }
    payload={"customer_id":globalsconf['centralcustomerid']}
    params={"client_id":globalsconf['centralclientid'],"response_type":"code","scope":"all"}
    try:
        response=requests.post(url,params=params,json=payload,headers=headers)
        if "auth_code" in response.json():
            token_url = globalsconf['centralurl'] + "/oauth2/token"
            token_data={
                "grant_type":"authorization_code",
                "code": response.json()['auth_code']}
            token_response=requests.post(token_url,data=token_data,auth=(globalsconf['centralclientid'],globalsconf['centralclientsecret']))
            if "refresh_token" in token_response.json() and "access_token" in token_response.json():
                # There is a refresh token and access token in the response. We can store this dictionary in the variables file
                globalsconf.update({"arubacentraltokeninfo":token_response.json()})
                with open('bash/globals.json', 'w') as systemconfig:
                    systemconfig.write(json.dumps(globalsconf))
                result={"message":"Authorization successful", "status":True}
            else:
                result=token_result.json()
        else:
            result={"message":"Unable to authorize...", "status":False}
    except Exception as err:
        result={"message":"Invalid parameters","status": False}
    return result


def checkcentralToken(authtype):
    print("Verify Aruba Central token validity")
    globalsconf=classes.classes.globalvars()
    url = globalsconf['centralurl'] + "/monitoring/v1/aps"
    headers={"authorization": f"Bearer {globalsconf['arubacentraltokeninfo']['access_token']}"}
    response=requests.get(url, headers=headers)
    print(response.json())
    print(response.status_code)
    if "error" in response.json():
        if response.json()['error']=="invalid_token" :
            # The access token is not valid anymore, we have to refresh the token
            refreshcentralToken()
            if authtype=="authentication":
                result={"message":"Re-authenticating","status":False}
            else:
                result={"message":"Re-authorizing","status":False}
    elif "message" in response.json():
        if response.json()['message']=="API rate limit exceeded":
            result={"message":"Maximum number of API calls reached","status":False}
    elif response.status_code==200:
        if authtype=="authentication":
            result={"message":"Authentication is successful","status":True}
        elif authtype=="authorization":
            result={"message":"Authorization is successful","status":True}
        else:
            result={"message":"Valid token","status":True}
    else:
        result={"message":"Auth error","status":False}
    return result


def refreshcentralToken():
    globalsconf=classes.classes.globalvars()
    try:
        url=globalsconf['centralurl'] + "/oauth2/token?client_id=" + globalsconf['centralclientid'] + "&client_secret=" + globalsconf['centralclientsecret'] + "&grant_type=refresh_token&refresh_token=" + globalsconf['arubacentraltokeninfo']['refresh_token']
        s = requests.Session()
        req = requests.Request(method="POST", url=url)
        prepped = s.prepare_request(req)
        settings = s.merge_environment_settings(prepped.url, {}, None, None, None)
        response = s.send(prepped, **settings)
        # It could be that there is a problem with the token refresh. If that is the case, we need to authenticate and authorize and store the new auth results
        if "error_description" in response.json():
            response=centralAuthentication()
            if response['status']==True:
                # Authentication is successful, now authorize and refresh the token
                response=centralAuthorization()
                if response['status']==True:
                    result={"message":"Token refresh successful", "status":True}
                else:
                    result=response
            else:
                result=response          
        else:
            # Token is refreshed successfully. We need to store the newly created token information in the settings.
            if "refresh_token" in response.json() and "access_token" in response.json():
                # There is a refresh token and access token in the response. We can store this dictionary in the variables file
                globalsconf.update({"arubacentraltokeninfo":response.json()})
                with open('bash/globals.json', 'w') as systemconfig:
                    systemconfig.write(json.dumps(globalsconf))
                result={"message":"Token refresh successful", "status":True}
            else:
                result=response.json()
    except Exception as err:
        result={"message":err, "status":False}
    return result


