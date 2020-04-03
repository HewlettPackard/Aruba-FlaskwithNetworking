// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

/**
 * Event handler for clicking on button "Connect"
 */

function onConnectClick() {
    var devid = document.getElementById("deviceid");
    var deviceid = devid.options[devid.selectedIndex].value;
    $(function () {
        //This function is calling a Python definition that logs into the CX switch and obtains the cookie information
        $.ajax({
            type: 'POST',
            url: 'getcxcookie',
            data: {deviceid:deviceid},
            success: function (data) {
                data = JSON.parse(data);
                for (i = 0; i < data['cookies'].length; i++) {
                    //Setting the cookie values. deviceip is the IP address of the switch but this cannot be set because of the origin of the script
                    //which is the webserver instead of the switch
                    document.cookie = data['cookies'][i].name + "=" + data['cookies'][i].value + "domain=" + data['deviceip'];
                }
                wss_url = "wss://" + data['deviceip'] + "/rest/v1/notification";
                //Set the cookie value using a broker (Express)
                $.ajax({
                    url: 'http://localhost:3000/setcookie?ipaddress=' + data['deviceip'] + '&cookies=' + JSON.stringify(data['cookies']),
                    withCredentials: true,
                    dataType: "json",
                    success: function (data) {
                        console.log(data);
                        //process the JSON data etc
                    }
                })
                openWSConnection(wss_url);
            }
        });
});
}
/**
 * Event handler for clicking on button "Disconnect"
 */
function onDisconnectClick() {
    webSocket.close();
}
/**
 * Open a new WebSocket connection using the given parameters
 */
function openWSConnection(wss_url) {
    console.log("openWSConnection::Connecting to: " + wss_url);
    var devid = document.getElementById("deviceid");
    var deviceid = devid.options[devid.selectedIndex].value;
    try {
        webSocket = new WebSocket(wss_url, [], {
            rejectUnauthorized: false
        });
        console.log(JSON.stringify(webSocket));
        webSocket.onopen = function (openEvent) {
            console.log("WebSocket OPEN: " + JSON.stringify(openEvent, null, 4));
            document.getElementById("subscribeAction").disabled = false;
            document.getElementById("Connect").disabled = true;
            document.getElementById("Disconnect").disabled = false;
            document.getElementById("wsstatus").style.display = "block";
            document.getElementById("subscribeForm").style.display = "block";
            document.getElementById("wsstatus").innerHTML = "<font class='font13px'>Status: Connected</font>";
        };
        webSocket.onclose = function (closeEvent) {
            console.log(closeEvent);
            console.log("WebSocket CLOSE: " + JSON.stringify(closeEvent, null, 4));
            document.getElementById("subscribeAction").disabled = true;
            document.getElementById("Connect").disabled = false;
            document.getElementById("Disconnect").disabled = true;
            document.getElementById("subscribeForm").style.display = "none";
            document.getElementById("wsstatus").innerHTML = "<font class='font13px'>Status: Disconnected</font>";
        };
        webSocket.onerror = function (errorEvent) {
            console.log("WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4));
            document.getElementById("wsstatus").style.display = "block";
            document.getElementById("wsstatus").innerHTML = "WebSocket ERROR";
        };
        webSocket.onmessage = function (messageEvent) {
            var wsMsg = messageEvent.data;
            msgJSON = JSON.parse(wsMsg);
            if (msgJSON['subscriber_name']) {
                subscriber_name = msgJSON['subscriber_name'];
                document.getElementById('subscriber_name').value = subscriber_name;
            }
            else {
                subscriber_name = document.getElementById('subscriber_name').value;
            }
            document.getElementById("subscriptionList").style.display = "none";
            $.ajax({
                type: 'POST',
                url: 'getSubs',
                data: { subscriber_name:subscriber_name, deviceid: deviceid},
                success: function (subscriberdata) {
                    subJSON = jQuery.parseJSON(subscriberdata);
                    subscriberHTML = "<table class='tablenoborder'><tr><td><font class='font13px'>Subject</font></td><td><font class='font13px'>Attributes</font></td><td><font class='font13px'>Depth</font></td><td><font class='font13px'>Action</font></td></tr>";
                    for (items in subJSON) {
                        for (items2 in subJSON[items]) {
                            //Break up the items in Subject, Attributes and Depth
                            wsSubject = subJSON[items][items2][0].split("?");
                            wsAttributes = wsSubject[1].split("&");
                            wsDepth = wsAttributes[1].split("=");
                            subscriberHTML += "<tr><td><font class='font12px'>" + wsSubject[0].substring('/rest/v1/system/'.length) + "</font></td> <td><font class='font12px'>" + wsAttributes[0].substring('attributes='.length) + "</font></td> <td><font class='font12px'>" + wsDepth[1] + "</font></td>";
                            subscriberHTML += "<td><button class='button' value='" + subJSON[items][items2][0] + "' onclick='unsubscribeClick(this)'>Unsubscribe</button></td></tr>";
                        }
                    }
                    subscriberHTML += "</table>";
                    if (subJSON.length==0) {
                        document.getElementById("subscriptionList").style.display = "none";
                    }
                    else {
                        document.getElementById("subscriptionList").style.display = "block";
                        document.getElementById('subscriptionList').innerHTML = subscriberHTML;
                        document.getElementById("attributes").value = "";
                        document.getElementById("subject").value = "";
                    }
                }
            });
            //console.log("WebSocket MESSAGE: " + wsMsg);
            if (wsMsg.indexOf("error") > 0) {
                errorMessage = JSON.parse(wsMsg);
                document.getElementById("incomingMsgOutput").value += "Error: " + errorMessage['message'] + "\r\n";
            } else {
                document.getElementById("incomingMsgOutput").value += "Message: " + wsMsg + "\r\n";
             }
        };
    } catch (exception) {
         console.error(exception);
    }
}
/**
 * Send a message to the WebSocket server (subscribe or unsubscribe)
 */
function subscribeClick() {
    if (webSocket.readyState != WebSocket.OPEN) {
        console.error("webSocket is not open: " + webSocket.readyState);
        return;
    }

    var subj = document.getElementById("subject");
    var subject = subj.options[subj.selectedIndex].value;
    var dpth = document.getElementById("depth");
    var depth = dpth.options[dpth.selectedIndex].value;     
    msg = "{ \"topics\": [{ \"name\": \"/rest/v1/system/" + subject + "?attributes=" + document.getElementById("attributes").value + "&depth=" + depth + "\"}], \"type\": \"subscribe\" }";
    if (subject != "") {
        webSocket.send(msg);
    }
}

function unsubscribeClick(message) {
    if (webSocket.readyState != WebSocket.OPEN) {
        console.error("webSocket is not open: " + webSocket.readyState);
        return;
    }
    msg = "{ \"topics\": [{ \"name\": \"" + message.value + "\" }], \"type\": \"unsubscribe\" }";
    webSocket.send(msg);

}

function clearText() {
    document.getElementById("incomingMsgOutput").value = "";
}