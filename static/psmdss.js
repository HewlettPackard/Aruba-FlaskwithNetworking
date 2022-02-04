// (C) Copyright 2022 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.dssStatus').ready(function () {
        var refresh = async function () {
            $('.dssInformation').each(function () {
                dssInfo = $(this).attr('data-info');
                if (typeof dssInfo === 'string' || dssInfo instanceof String) {
                    dssInfo = dssInfo.replace(/'/g, '"');
                    dssInfo=JSON.parse(dssInfo);
                }

                var uuid = dssInfo['meta']['uuid'];

                // Construct the switch information HTML
                attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Switch hostname</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['dss-info']['host-name'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>IP address</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['ip-config']['ip-address']  + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Switch default gateway</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['ip-config']['default-gw']  + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Switch software version</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['dss-info']['version']  + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "</table>";
                $('#dssswitchinfo' + uuid).attr('data-info', attrsetHTML);

                // Construct the advanced information HTML
                attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Device type</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['kind'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Management mode</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['spec']['mgmt-mode'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>network mode</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['spec']['network-mode'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Firewall log policy (tenant)</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['spec']['fwlog-policy']['name'] + " (" + dssInfo['spec']['fwlog-policy']['tenant'] + ")</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>DSC SKU</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['DSCSku'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>OS type</td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['system-info']['os-info']['type'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "<tr>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>OS kernel release</font></td>";
                attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + dssInfo['status']['system-info']['os-info']['kernel-release'] + "</font></td>";
                attrsetHTML += "</tr>";
                attrsetHTML += "</table>";
                $('#dssinfo' + uuid).attr('data-info', attrsetHTML);
            })
        }
        setInterval(refresh, 5000);
        refresh();
    }); 


});


