// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.securitypolicyStatus').ready(function () {
        var refresh = async function () {
            $('.securitypolicyInformation').each(function () {
                securitypolicyInfo = $(this).attr('data-info');
                if (typeof securitypolicyInfo === 'string' || securitypolicyInfo instanceof String) {
                    securitypolicyInfo = securitypolicyInfo.replace(/'/g, '"');
                    securitypolicyInfo = JSON.parse(securitypolicyInfo);
                }
                var uuid = securitypolicyInfo['meta']['uuid'];
                //Construct the pending DSS status

                if (securitypolicyInfo['status']['propagation-status']['pending'] > 0) {
                     attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
                     attrsetHTML += "<tr>";
                     attrsetHTML += "<td class='whiteBG' align='center' nowrap><font class='font10pxgrey'>Pending DSS/DSC</font></td>";
                     attrsetHTML += "</tr>";
                     for (var i = 0; i < securitypolicyInfo['status']['propagation-status']['pending-dscs'].length; i++) {
                       attrsetHTML += "<tr>";
                       attrsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + securitypolicyInfo['status']['propagation-status']['pending-dscs'][i] + "</font></td>";
                       attrsetHTML += "</tr>";
                     }
                     attrsetHTML += "</table>";
                }
                else {
                    // Construct the switch information HTML
                    attrsetHTML = "<table class='tablenoborder' style='max-width: 350px;'>";
                    attrsetHTML += "<tr>";
                    attrsetHTML += "<td class='whiteBG' align='right' nowrap><font class='font10pxgrey'>None</font></td>";
                    attrsetHTML += "</tr>";
                    attrsetHTML += "</table>";
                }
                $('#pendingdssinfo' + uuid).attr('data-info', attrsetHTML);
            });        
        }
        setInterval(refresh, 5000);
        refresh();
    }); 



    $('.ruleInfo').click(function () {
        uuid = $(this).data('uuid');
        $('#securitypolicyRuleset').attr('data-uuid', $(this).data('uuid'));
        var refresh = async function () {
            uuid = $('#securitypolicyRuleset').attr('data-uuid');
            // Obtain the ruleset information from the selected entry
            securitypolicyInfo = $('#tr' + uuid).data('info');
            if (typeof securitypolicyInfo === 'string' || securitypolicyInfo instanceof String) {
                securitypolicyInfo = securitypolicyInfo.replace(/'/g, '"');
                securitypolicyInfo = JSON.parse(securitypolicyInfo);
            }

            rulesetHTML = "<table class='tablewithborder'>";
            rulesetHTML += "<tr class='tableTitle'><td colspan='8' align='center'><font class='font12pxwhite'>Ruleset for " + securitypolicyInfo['meta']['name'] + "</font></td></tr>";
            for (var i = 0; i < securitypolicyInfo['spec']['rules'].length; i++) {
                rulesetHTML += "<tr class='tableTitle'>";

                rulesetHTML += "<td><font class='font12pxwhite'>Action</font></td>";
                rulesetHTML += "<td class='whiteBG'><font class='font11pxgrey'>" + securitypolicyInfo['spec']['rules'][i]['action'] + "</font></td>";
                rulesetHTML += "<td><font class='font12pxwhite'>App</font></td>";
                rulesetHTML += "<td class='whiteBG'><font class='font11pxgrey'>";
                if (typeof(securitypolicyInfo['spec']['rules'][i]['apps']) != "undefined") {
                    rulesetHTML += securitypolicyInfo['spec']['rules'][i]['apps'];
                }
                else {
                    rulesetHTML += " - ";
                }
                rulesetHTML += "</font></td>";
                rulesetHTML += "<td><font class='font12pxwhite'>From</font></td>";
                rulesetHTML += "<td class='whiteBG'><font class='font11pxgrey'>";
                for (var ii = 0; ii < securitypolicyInfo['spec']['rules'][i]['from-ip-addresses'].length; ii++) {
                    rulesetHTML += securitypolicyInfo['spec']['rules'][i]['from-ip-addresses'][ii] + "<br>";
                }

                rulesetHTML += "</font></td>";
                rulesetHTML += "<td><font class='font12pxwhite'>To</font></td>";
                rulesetHTML += "<td class='whiteBG'><font class='font11pxgrey'>";
                for (var ii = 0; ii < securitypolicyInfo['spec']['rules'][i]['to-ip-addresses'].length; ii++) {
                    rulesetHTML += securitypolicyInfo['spec']['rules'][i]['to-ip-addresses'][ii] + "<br>";
                }
                rulesetHTML += "</font></td>";

                rulesetHTML += "</tr>";

            }
            rulesetHTML += "</table>";
            $('#securitypolicyRuleset').empty().append(rulesetHTML);
        }
        setInterval(refresh, 5000);
        refresh(uuid);
    });



});


