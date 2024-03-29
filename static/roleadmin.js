// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).on("click", "#addRole", function () {
    document.getElementById("Rolediv").style.display = "block";
    var menuitems = ["devices", "ztp", "deviceupdates", "topology", "telemetry", "tools", "psm", "afc", "administration"];
    var accessitems = ["switch", "mobility", "clearpass", "ztptemplate", "ztpdevice", "image", "upgradescheduler", "upgradeprofiles", "telemetrymonitor", "telemetrysubscription", "dhcptracker", "snmptracker", "syslogtracker", "anycli", "afcfabrics", "afcswitches", "afcintegrations", "afcauditlog", "afcvmwareinventory","psmdss","psmnetworks","psmsecuritypolicies","psmalertpolicies", "sysuser", "sysrole", "integrations","deviceattributes", "sysadmin", "servicesstatus"];
    document.getElementById("name").value = "";
    for (i = 0; i < menuitems.length; i++) {
        document.getElementById(menuitems[i]).checked = false;
    }
    for (i = 0; i < accessitems.length; i++) {
        document.getElementById(accessitems[i] + "access").value = 0;
    }
    document.getElementById("addoredit").innerHTML = "Add";
    document.getElementById("submitorchange").innerHTML = "<input type='submit' name='action' value='Submit role' class='button' />";
});


$(document).on("click", ".editRole", async function () {
    document.getElementById("Rolediv").style.display = "block";
    document.getElementById("addoredit").innerHTML = "Edit";
    document.getElementById("submitorchange").innerHTML = "<input type='submit' name='action' value='Submit changes' class='button' />";
    document.getElementById("roleid").value = $(this).attr('data-roleid');
    response = await $.ajax({
        url: "/editrole",
        type: "POST",
        data: { id: $(this).attr('data-roleid')},
        success: function (response) {
            response = JSON.parse(response);
            document.getElementById("name").value=response["name"];
            var menuitems = ["devices", "ztp", "deviceupdates", "topology", "telemetry", "tools", "psm", "afc", "administration"];
            var accessitems = ["switch", "mobility", "clearpass", "ztptemplate", "ztpdevice", "image", "upgradescheduler", "upgradeprofiles", "telemetrymonitor", "telemetrysubscription", "dhcptracker", "snmptracker", "syslogtracker", "anycli", "afcfabrics", "afcswitches", "afcintegrations", "afcauditlog", "afcvmwareinventory","psmdss","psmnetworks","psmsecuritypolicies","psmalertpolicies", "sysuser","sysrole","integrations","deviceattributes", "sysadmin","servicesstatus"];
            accessrights = JSON.parse(response['accessrights']);
            for (i = 0; i < menuitems.length; i++) {
                if (menuitems[i] in accessrights) {
                    document.getElementById(menuitems[i]).checked = true;
                }
            } 
            for (i = 0; i < accessitems.length; i++) {
                document.getElementById(accessitems[i] + "access").value = accessrights[accessitems[i] + "access"];
            }
        },
        error: function () {
            console.log("Error obtaining role information");
        }
    });
});