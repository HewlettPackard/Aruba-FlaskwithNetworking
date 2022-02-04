// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.networkStatus').ready(function () {
        var refresh = async function () {
            $('.networkInformation').each(function () {
                networkInfo = $(this).attr('data-info');
                if (typeof networkInfo === 'string' || networkInfo instanceof String) {
                    networkInfo=networkInfo.replace(/'/g, '"');
                    networkInfo=JSON.parse(networkInfo);
                }
                var uuid = networkInfo['meta']['uuid'];
                if (networkInfo['status']['propagation-status']['pending'] > 0) {
                    if (networkInfo['status']['propagation-status']['pending-DSCS'].constructor == Object) {
                        attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                        attrsetHTML += "<tr>";
                        attrsetHTML += "<td class='whiteBG' align='center' nowrap><font class='font10pxgrey'>Pending DSS/DSC</font></td>";
                        attrsetHTML += "</tr>";
                        for (var i = 0; i < networkInfo['status']['propagation-status']['pending-DSCS'].length; i++) {
                            attrsetHTML += "<tr>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + networkInfo['status']['propagation-status']['pending-DSCS'][i] + "</font></td>";
                            attrsetHTML += "</tr>";
                        }
                        attrsetHTML += "</table>";
                    }
                }
                else {
                    // Construct the switch information HTML
                    attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                    attrsetHTML += "<tr>";
                    attrsetHTML += "<td class='whiteBG' align='center' nowrap><font class='font10pxgrey'>None</font></td>";                  
                    attrsetHTML += "</tr>";
                    attrsetHTML += "</table>";
                }
                $('#networkinfo' + uuid).attr('data-info', attrsetHTML);
            })
        }
        setInterval(refresh, 5000);
        refresh();
    }); 


});


