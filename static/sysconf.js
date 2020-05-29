// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('#secret_key').on('keyup', function () {
        if (this.value.length<= 15)
        {
            $('#submitChanges').attr('disabled', 'disabled');
        } else {
            $('#submitChanges').attr('disabled', false);
        }
    });
});

$('.cleanupProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='cleanupProcess']").load('monitorProcess?name=Cleanup');
    }
    setInterval(refresh, 5000);
    refresh();
});

$('.topologyProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='topologyProcess']").load('monitorProcess?name=Topology');
    }
    setInterval(refresh, 5000);
    refresh();
});

$('.ztpProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='ztpProcess']").load('monitorProcess?name=ZTP');
    }
    setInterval(refresh, 5000);
    refresh();
});

$('.listenerProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='listenerProcess']").load('monitorProcess?name=Listener');
    }
    setInterval(refresh, 5000);
    refresh();
});

$('#systemTime').ready(function () {
    var refresh = function () {
        $.ajax({
            type: "POST",
            headers: { "Content-Type": "application/json" },
            url: "/getsysTime",
            success: function (response) {
                response = JSON.parse(response);
                document.getElementById("systemTime").innerHTML = response['month'] + " " + response['day'] + ", " + response['year'] + ": " + minTwoDigits(response['hour']) + ":" + minTwoDigits(response['minute']) + ":" + minTwoDigits(response['second']);
            }

        });
    }
    setInterval(refresh, 1000);
    refresh();
});

$('#ipamstatus').ready(function () {
    var refresh = async function () {
        if (document.getElementById('ipamsystem')) {
            var e = document.getElementById("ipamsystem");
            var ipamsystem = e.options[e.selectedIndex].value;
            var ipamenabled = document.getElementById("ipamenabled");
            if ((ipamsystem == "Infoblox" || ipamsystem == "PHPIPAM") && ipamenabled.checked == true) {
                if (ipamsystem == "Infoblox") {
                    var ipamuser = document.getElementById('ipamuser').value;
                    var ipampassword = document.getElementById('ipampassword').value;
                    var ipamipaddress = document.getElementById('ipamipaddress').value;
                    var phpipamappid = "";
                    var phpipamauth = "";
                }
                else if (ipamsystem == "PHPIPAM") {
                    var ipamuser = document.getElementById('ipamuser').value;
                    var ipampassword = document.getElementById('ipampassword').value;
                    var ipamipaddress = document.getElementById('ipamipaddress').value;
                    var e = document.getElementById("phpipamauth");
                    var phpipamauth = e.options[e.selectedIndex].value;
                    var phpipamappid = document.getElementById('phpipamappid').value;
                }

                response = await $.ajax({
                    url: "/ipamStatus",
                    type: "POST",
                    data: { ipamsystem: ipamsystem, ipamipaddress: ipamipaddress, ipamuser: ipamuser, ipampassword: ipampassword, phpipamauth: phpipamauth, phpipamappid: phpipamappid },
                    success: function (response) {
                    }
                });
                if (response == "Online") {
                    document.getElementById("ipamStatus").innerHTML = "<font class='font13pxwhite'>IPAM is reachable: </font><img src='static/images/ok.png' height='15' width='15'>";
                }
                else {
                    document.getElementById("ipamStatus").innerHTML = "<font class='font13pxwhite'>IPAM is unreachable: </font><img src='static/images/notok.png' height='15' width='15'>";
                }
            }
            else {
                document.getElementById("ipamStatus").innerHTML = "<font class='font13pxwhite'>IPAM not selected or activated...</font>";
            }
        }
    }
    setInterval(refresh, 5000);
    refresh();
});

$(document).on('click', '.downloadLog', function () {
    response = $.ajax({
        url: "/downloadLog",
        type: "POST",
        data: { processName: $(this).attr("data-processname") },
        success: function (response) {
            response = JSON.parse(response);
            var logInfo = document.createElement('a');
            logFile = response[0] + ".txt";
            logInfo.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(response[1]));
            logInfo.setAttribute("download", logFile);
            if (document.createEvent) {
                var event = document.createEvent('MouseEvents');
                event.initEvent('click', true, true);
                logInfo.dispatchEvent(event);
            }
            else {
                logInfo.click();
            }          
        }
    });
});

$(document).on('click', '.clearLog', function () {
    response = $.ajax({
        url: "/clearprocessLog",
        type: "POST",
        data: { processName: $(this).attr("data-processname") },
        success: function (response) {
        }
    });
});

function minTwoDigits(n) {
    return (n < 10 ? '0' : '') + n;
}

function ipamConf() {
    var e = document.getElementById("ipamsystem");
    var ipamVal = e.options[e.selectedIndex].value;


    if (ipamVal == "Infoblox") {
        $("#ipamtr").show();
        $("#phpipamtr").hide();
    }

    else if (ipamVal == "PHPIPAM") {
        $("#ipamtr").show();
        $("#phpipamtr").show();
    }
    else {
        $("#ipamtr").hide();
        $("#phpipamtr").hide();
    }

   
}