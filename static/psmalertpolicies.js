// (C) Copyright 2022 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.alertpolicyStatus').ready(function () {
        var refresh = async function () {          
            $('.alertpolicyInformation').each(function () {
                alertpolicyInfo = $(this).attr('data-info');
                alertDestinations = $('.alertpolicyStatus').attr('data-alertdestinations');
                if (typeof alertpolicyInfo === 'string' || alertpolicyInfo instanceof String) {
                    alertpolicyInfo = alertpolicyInfo.replace(/'/g, '"');
                    alertpolicyInfo = JSON.parse(alertpolicyInfo);
                }
                if (typeof alertDestinations === 'string' || alertDestinations instanceof String) {
                    alertDestinations = alertDestinations.replace(/'/g, '"');
                    alertDestinations = JSON.parse(alertDestinations);
                }
                var uuid = alertpolicyInfo['meta']['uuid'];
                //Construct the destinations from the destinations list
                if (typeof (alertpolicyInfo['spec']['destinations']) === 'object') {
                    for (var i = 0; i < alertpolicyInfo['spec']['destinations'].length; i++) {
                        for (var j = 0; j < alertDestinations['items'].length; j++) {
                            if (alertDestinations['items'][j]['meta']['name'] == alertpolicyInfo['spec']['destinations'][i]) {
                                attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                                attrsetHTML += "<tr>";
                                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Destination information</font></td>";
                                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + alertpolicyInfo['spec']['destinations'][i] + "</font></td>";
                                attrsetHTML += "</tr>";
                                attrsetHTML += "<tr>";
                                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Format</font></td>";
                                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + alertDestinations['items'][j]['spec']['syslog-export']['format'] + "</font></td>";
                                attrsetHTML += "</tr>";
                                for (var k = 0; k < alertDestinations['items'][j]['spec']['syslog-export']['targets'].length; k++) {
                                    attrsetHTML += "<tr>";
                                    attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Target (transport/port)</font></td>";
                                    attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + alertDestinations['items'][j]['spec']['syslog-export']['targets'][k]['destination'] + " (" + alertDestinations['items'][j]['spec']['syslog-export']['targets'][k]['transport'] + ")</font></td>";
                                    attrsetHTML += "</tr>";
                                }
                                attrsetHTML += "</table>";
                                $('#alertdestinations' + uuid).attr('data-info', attrsetHTML);
                            }  
                        }
                    }
                }
                //Fill the requirements tooltip
                if (typeof (alertpolicyInfo['spec']['requirements']) === 'object') {
                    attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                    attrsetHTML += "<tr>";
                    attrsetHTML += "<td class='whiteBG' align='center' nowrap colspan='3'><font class='font10pxgrey'>Requirements</font></td>";
                    attrsetHTML += "</tr>";
                    
                    for (var i = 0; i < alertpolicyInfo['spec']['requirements'].length; i++) {
                        
                        attrsetHTML += "<tr>";
                        attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + alertpolicyInfo['spec']['requirements'][i]['key'] + "</font></td>";
                        attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + alertpolicyInfo['spec']['requirements'][i]['operator'] + "</font></td>";
                        attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>";
                        for (var j = 0; j < alertpolicyInfo['spec']['requirements'][i]['values'].length; j++) {
                            attrsetHTML += alertpolicyInfo['spec']['requirements'][i]['values'][j] + "<br>";
                        }
                        attrsetHTML += "</font ></td >";
                        attrsetHTML += "</tr>";
                    }
                    attrsetHTML += "</table>";
                    $('#alertrequirements' + uuid).attr('data-info', attrsetHTML);

                }
           

            });


            // Refresh the alert policy destinations, obtain the policies from PSM
            response = await $.ajax({
                type: "POST",
                data: {},
                url: "/psmalertDestinations",
                success: function () {

                },
                error: function () {
                }
            });
            $('.alertpolicyStatus').attr('data-alertdestinations', JSON.stringify(response));
            // And also the alert policies. Add them to the alertpolicyStatus div
            response = await $.ajax({
                type: "POST",
                data: {},
                url: "/psmalertPolicies",
                success: function () {

                },
                error: function () {
                }
            });
            $('.alertpolicyStatus').attr('data-alertpolicies', JSON.stringify(response));












        }
        setInterval(refresh, 5000);
        refresh();
    }); 

   



});


