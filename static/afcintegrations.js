// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.integrationStatus').ready(function () {
        // Obtain the integration information from AFC
        var refresh = async function () {
            response = await $.ajax({
                type: "POST",
                data: {},
                url: "/afcintegrationStatus",
                success: function (response) {
                },
                error: function () {
                }
            });
            integrationInfo = JSON.parse(response);
            if ("message" in integrationInfo) {
                showmessageBar(integrationInfo['message']);
            }
            else {
                $("#liProgress").hide();
                // Update the integration status fields (features, configuration and status)
                integrationStatus = document.getElementsByClassName('integrationStatus');
                configurationItems = ['auto_discovery', 'connection_state', 'description', 'enabled', 'host', 'name', 'vlan_provisioning', 'vlan_range'];
                for (var i = 0; i < integrationInfo.length; i++) {
                    if ("configurations" in integrationInfo[i]) {
                        //There is configuration, need to check whether the integration is enabled. And update the configurations label information
                        if (integrationInfo[i]['configurations'][0]['enabled'] == true) {
                            // Integration is enabled. Update the status field
                            $('#integrationStatus' + integrationInfo[i]['name']).empty().append("Enabled");
                        }
                        else {
                            $('#integrationStatus' + integrationInfo[i]['name']).empty().append("Disabled");
                        }

                        //Construct and update the configuration information in the html
                        attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                        attrsetHTML += "<tr class='tableTitle'>";
                        attrsetHTML += "<td width='50%' align='left' nowrap><font class='font10pxwhite'>Parameter</font></td>";
                        attrsetHTML += "<td width='50%' align='left' nowrap><font class='font10pxwhite'>Value</font></td>";
                        attrsetHTML += "</tr>";
                        for (var ii = 0; ii < integrationInfo[i]['configurations'].length; ii++) {
                            for (var j in integrationInfo[i]['configurations'][ii]) {
                                if (configurationItems.includes(j) == true) {
                                    attrsetHTML += "<tr><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + j + "</font></td>";
                                    attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + integrationInfo[i]['configurations'][ii][j] + "</font></td>";
                                    attrsetHTML += "</tr>";
                                }
                            }
                            attrsetHTML += "<tr colspan='2' style='height:3px;'><td></td></tr>";
                        }
                        attrsetHTML += "</table>";
                        $('#' + integrationInfo[i]['name'] + 'Configurations').attr('data-info', attrsetHTML);
                    }
                    else {
                        $('#integrationStatus' + integrationInfo[i]['name']).empty().append("Disabled");
                        attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                        attrsetHTML += "<tr class='tableTitle'>";
                        attrsetHTML += "<td align='left' align='center' nowrap><center><font class='font10pxwhite'>Not configured</font></center></td>";
                        attrsetHTML += "</tr>";
                        attrsetHTML += "</table>";
                        $('#' + integrationInfo[i]['name'] + 'Configurations').attr('data-info', attrsetHTML);
                    }
                    // Update the features information in the html
                    attrsetHTML = "<table class='tablewithborder' style='max-width: 200px;'>";
                    attrsetHTML += "<tr class='tableTitle'>";
                    attrsetHTML += "<td align='left' nowrap><font class='font10pxwhite'>Feature list</font></td>";
                    attrsetHTML += "</tr>";
                    for (var j in integrationInfo[i]['features']) {
                        //Construct and update the features information in the html
                        attrsetHTML += "<tr><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + integrationInfo[i]['features'][j] + "</font></td>";
                        attrsetHTML += "</tr>";
                    }
                    attrsetHTML += "</table>";
                    $('#' + integrationInfo[i]['name'] + 'Features').attr('data-info', attrsetHTML);
                }
            }
        }
        setInterval(refresh, 5000);
        refresh();
    });
});


