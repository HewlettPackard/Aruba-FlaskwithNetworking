// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.


$(document).ready(function () {
    document.getElementById("liProgress").style.display = "none";
    $('.telemetryOnline').ready(function () {
        var refresh = async function () {
            telemetryOnline = document.getElementsByClassName('telemetryOnline');
            for (var i = 0; i < telemetryOnline.length; i++) {
                deviceid = telemetryOnline.item(i).getAttribute('data-deviceid');
                ostype = telemetryOnline.item(i).getAttribute('data-ostype');
                await $.ajax({
                    type: "POST",
                    data: { 'deviceid': deviceid },
                    url: "/telemetrystatus",
                    success: function (response) {
                        response = JSON.parse(response);
                        subscriptions = JSON.parse(response['subscriptions'])
                        // For some strange reason it could be that the status that is received from the call is not for the same device. If that is the case, we have to skip the update
                        if (response['deviceid'] == deviceid) {
                            //We can show the status
                            if (response['isRunning'] == "Online" && subscriptions['devicestatus'] == "Online") {
                                //The websocket client is running and device is online
                                document.getElementById("liProgress").style.display = "none";
                                document.getElementById('telemetryOnline' + deviceid).innerHTML = "<img src='static/images/status-good.svg' height='12' width='12' class='showtitleTooltip' data-title='Device is online'>";
                                $('#telemetryOnline' + deviceid).attr('data-status', '3');
                                $('#monitor' + deviceid).attr('disabled', false);
                                document.getElementById("subscriber" + deviceid).innerHTML = subscriptions['subscriber'];
                                document.getElementById("activesubscriptions" + deviceid).innerHTML = subscriptions['swsubs'];
                                document.getElementById("subscriptions" + deviceid).innerHTML = subscriptions['totaldbsubs'];
                                document.getElementById("activatedsubscriptions" + deviceid).innerHTML = subscriptions['activedbsubs'];
                                document.getElementById("startws" + deviceid).innerHTML = "";
                            }
                            else if (response['isRunning'] == "Offline" && subscriptions['devicestatus'] == "Online") {
                                //The websocket client is not running but the device is online
                                document.getElementById('telemetryOnline' + deviceid).innerHTML = "<img src='static/images/status-unknown.svg' height='12' width='12'  class='showtitleTooltip' data-title='Device is online, no subscriptions'>";
                                $('#telemetryOnline' + deviceid).attr('data-status', '2');
                                document.getElementById("subscriber" + deviceid).innerHTML = "";
                                document.getElementById("subscriptions" + deviceid).innerHTML = subscriptions['totaldbsubs'];
                                document.getElementById("activatedsubscriptions" + deviceid).innerHTML = subscriptions['activedbsubs'];
                                document.getElementById("activesubscriptions" + deviceid).innerHTML = subscriptions['swsubs'];
                                document.getElementById("startws" + deviceid).innerHTML = "";
                                if (subscriptions['subscriber'] != "Not active") {
                                    startwsHTML = "<button type='button' name='startws' class='transparent-button startwsClient' id='monitor" + deviceid + "' data-deviceid='" + deviceid + "'><img src='static/images/start.svg' width='12' height='12' class='showtitleTooltip' data-title='Start telemetry client'></button>";
                                    document.getElementById("startws" + deviceid).innerHTML = startwsHTML;
                                }
                            }
                            else if (response['isRunning'] == "Online" && subscriptions['devicestatus'] == "Offline") {
                                //The websocket client is not running but the device is online
                                document.getElementById('telemetryOnline' + deviceid).innerHTML = "<img src='static/images/status-critical.svg' height='12' width='12'  class='showtitleTooltip' data-title='Device is offline, telemetry client is active'>";
                                $('#telemetryOnline' + deviceid).attr('data-status', '1');
                                document.getElementById("subscriber" + deviceid).innerHTML = "";
                                document.getElementById("subscriptions" + deviceid).innerHTML = subscriptions['totaldbsubs'];
                                document.getElementById("activatedsubscriptions" + deviceid).innerHTML = subscriptions['activedbsubs'];
                                document.getElementById("activesubscriptions" + deviceid).innerHTML = subscriptions['swsubs'];
                                document.getElementById("startws" + deviceid).innerHTML = "";
                            }
                            else if (response['isRunning'] == "Offline" && subscriptions['devicestatus'] == "Offline") {
                                document.getElementById('telemetryOnline' + deviceid).innerHTML = "<img src='static/images/status-critical.svg' height='12' width='12'  class='showtitleTooltip' data-title='Device is offline, no active subscriptions'>";
                                $('#telemetryOnline' + deviceid).attr('data-status', '0');
                                $('#monitor' + deviceid).attr('disabled', true);
                                document.getElementById("subscriber" + deviceid).innerHTML = "Offline";
                                document.getElementById("activesubscriptions" + deviceid).innerHTML = "0";
                                document.getElementById("subscriptions" + deviceid).innerHTML = subscriptions['totaldbsubs'];
                                document.getElementById("activatedsubscriptions" + deviceid).innerHTML = subscriptions['activedbsubs'];
                                //Need to show the start wsclient button so that user can start the client manually, only if the switch is online
                                if (subscriptions['subscriber'] != "Not active") {
                                    startwsHTML = "<button type='button' name='startws' class='transparent-button startwsClient' id='monitor" + deviceid + "' data-deviceid='" + deviceid + "'><img src='static/images/start.svg' width='12' height='12' class='showtitleTooltip' data-title='Start telemetry client'></button>";
                                    document.getElementById("startws" + deviceid).innerHTML = startwsHTML;
                                }
                            }                         
                        }
                    },
                    error: function (response) {
                        console.log("There is an error obtaining status information");
                    }
                });
            }
        }
        setInterval(refresh, 3000);
        refresh();
    });




    $('#wsClient').ready(function () {

        uri = "ws://" + $('#wsClient').attr('data-hostip') + ":5000";
        const socket = new WebSocket(uri);
        // Connection opened
        socket.addEventListener('open', function (event) {
            socket.send('Connecting from Compass client');
        });

        // Listen for messages
        socket.addEventListener('message', function (event) {
            try { 
                message = (JSON.parse(event.data));
                messagecount = parseInt(document.getElementById("showWS" + message['ipaddress']).getAttribute('data-messagecount'));
                messagecount = messagecount + 1;
                document.getElementById("showWS" + message['ipaddress']).setAttribute('data-messagecount', messagecount);
                document.getElementById("showWS" + message['ipaddress']).innerHTML = messagecount;

                if (document.getElementsByClassName("showNotifications").id=="showNotification"+message['ipaddress']) {
                    //Monitor subscriptions has been clicked. We need to obtain the information from the textarea and append the message
                    //But only if the message is intended for the monitored device
                    //Format the message
                    updateMessage = JSON.stringify(message['message']).replace(/\\\"/g, "'");
                    updateMessage = updateMessage.replace(/(\r\n|\n|\r|\\n)/gm, "") + "\n";
                    notificationInfo = document.getElementById("showNotifications").innerHTML + updateMessage;
                    document.getElementById('showNotifications').innerHTML = notificationInfo;
                    

                }
            } catch (e) {
                message = {};
            }
            //console.log(message);
        });

        // Connection closed
        socket.addEventListener('close', function (event) {
            showmessageBar("Disconnected from the websocket server");
        });
        const sendMsg = () => {
            socket.send("Hello from client...");
        }


    });

    $(document).on("click", "#searchSubscription", function () {
        document.getElementById("monitorsubscription").style.display = "none";
        document.getElementById("managesubscription").style.display = "none";
    });

 
    $(".editSubscription").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("monitorsubscription").style.display = "none";
        document.getElementById("managesubscription").style.display = "none";
    });

    
});

$(document).on("click", ".monitorSubscription", function () {
    id = $(this).data('username');
    document.getElementsByClassName("showNotifications").id = "showNotification" + id;
    document.getElementById('showNotifications').innerHTML = "";
    document.getElementById("monitorsubscription").style.display = "block";
    document.getElementById("managesubscription").style.display = "none";
});

$(document).on("click", ".startwsClient", async function () {
    response = await $.ajax({
        url: "/startwsClient",
        type: "POST",
        data: { id: $(this).data('deviceid') },
        success: function (response) {
            response = JSON.parse(response);  
            console.log(response);
        },
        error: function () {
            console.log("Error starting websocket client");
        }
    });
});


$(document).on("click", ".manageSubscription", async function () {
    document.getElementById("monitorsubscription").style.display = "none";
    document.getElementById("managesubscription").style.display = "block";

    if (document.getElementById("addSubscription")) {
        addSubscription = document.getElementById("addSubscription").value;
    }
    else {
        addSubscription = "";
    }
    if ($(this).attr('value') == "Delete") {
        deleteEntry = deleteConfirm();
        if (deleteEntry == false) {
            var confirmDelete = 0;
        }
        else {
            var confirmDelete = 1;
            }
    }
    response = await $.ajax({
        url: "/subscriptions",
        type: "POST",
        data: { id: $(this).attr('data-deviceid'), action: $(this).attr('value'), subscriber: $(this).attr('data-subscriber'), resource: $(this).attr('data-resource'), addSubscription: addSubscription, confirmDelete:confirmDelete },
        success: function (response) {
            response = JSON.parse(response);
            msHTML = "<table class='tablenoborder'>";
            msHTML += "<tr style='background-color: grey;'><td colspan='3'><font class='font13pxwhite'><center>Subscriptions of " + response['deviceinfo']['ipaddress'] + " (" + response['deviceinfo']['description'] + ")</center></font></td></tr>";
            msHTML += "<tr><td width='50%' nowrap><font class='font13pxgrey'>Resource</font></td>";
            msHTML += "<td width='40%' nowrap><font class='font13pxgrey'>Status</font></td><td nowrap></td></tr>";
            subscriptions = JSON.parse(response['subscriptions']);
            for (var i = 0; i < subscriptions[0].length; i++) {
                msHTML += "<tr><td class='whiteBG'><font class='font11px'>" + subscriptions[0][i]['resource'] + "</font></td>";
                msHTML += "<td class='whiteBG'><font class='font11px'>" + subscriptions[0][i]['message'] + "</font></td>";
                msHTML += "<td class='whiteBG' width='10%' nowrap align='right'>";
                if (subscriptions[0][i]['status'] == "0") {
                    msHTML += "<button type='button' class='transparent-button manageSubscription' value='Subscribe' data-deviceid='" + response['deviceinfo']['id'] + "' data-subscriber='" + response['deviceinfo']['subscriber'] + "' data-resource='" + subscriptions[0][i]['resource'] + "'><img src='static/images/link.svg' width='12' height='12' class='showtitleTooltip' data-title='Subscribe'></button>";
                    msHTML += "<button type='button' class='transparent-button manageSubscription' value='Delete'  data-deviceid='" + response['deviceinfo']['id'] + "' data-subscriber='" + response['deviceinfo']['subscriber'] + "' data-resource='" + subscriptions[0][i]['resource'] + "'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete subscription'></button>";
                }
                else if (subscriptions[0][i]['status'] == "1") {
                    msHTML += "<button type='button' class='transparent-button manageSubscription' value='Unsubscribe' data-deviceid='" + response['deviceinfo']['id'] + "' data-subscriber='" + response['deviceinfo']['subscriber'] + "' data-resource='" + subscriptions[0][i]['resource'] + "'><img src='static/images/unlink.svg' width='12' height='12' class='showtitleTooltip' data-title='Unsubscribe'></button>";
                }
                else if (subscriptions[0][i]['status'] == "2") {
                    msHTML += "Subscription error";
                }
                msHTML += "</td></tr> ";
            }
            msHTML += "<tr><td class='whiteBG'><font class='font11px'><input type='text' name='addSubscription' id='addSubscription' value='' size='100'></font></td><td class='whiteBG'></td>";
            msHTML += "<td class='whiteBG' width='10%' nowrap align='right'>";
            msHTML += "<button type='button' class='transparent-button manageSubscription' value='Add subscription' data-deviceid='" + response['deviceinfo']['id'] + "' data-subscriber='" + response['deviceinfo']['subscriber'] + "'><img src='static/images/add.svg' width='12' height='12' class='showtitleTooltip' data-title='Add subscription'></button></td></tr >";

            msHTML += "</table>";
            document.getElementById('managesubscription').innerHTML = msHTML;

        },
        error: function () {
            console.log("Error obtaining device information");
        }
    });
});


function clearTextArea(element) {
    element.innerHTML = "";
}

function deleteConfirm() {
    return confirm("Delete entry");
}