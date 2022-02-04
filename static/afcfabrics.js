// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.fabricStatus').ready(function () {
        // Obtain the fabric information from AFC
        var refresh = async function () {
            response = await $.ajax({
                type: "POST",
                data: {},
                url: "/afcfabricStatus",
                success: function () {
                },
                error: function () {
                }
            });
            if ("result" in response) {
                // There is a fabric so we can check if the fabric is added/removed/etc
                if (response['result'] != "Authentication token header required") {
                    $("#liProgress").hide();
                    fabriclistHTML = JSON.parse($('#afcfabrics').attr('data-afcfabricuuid').replace(/'/g, '"'));
                    //Construct the fabric UUID's in an array
                    fabricList = [];
                    for (var i = 0; i < response['result'].length; i++) {
                        fabricList.push(response['result'][i]['uuid']);
                    }
                    // First check is if a fabric has been added, we need to add a row to the table
                    addedFabric = $(fabricList).not(fabriclistHTML).get();

                    if (response['result'].length > 0) {


                        for (var i = 0; i < addedFabric.length; i++) {
                            for (var j = 0; j < response['result'].length; j++) {
                                if (addedFabric[i] == response['result'][j]['uuid']) {
                                    // Need to add a row containing this fabric information
                                    //Construct the HTML
                                    fabricHTML = "";
                                    fabricHTML += "";
                                    fabricHTML += "<tr id='tr" + response['result'][j]['uuid'] + "' class='trfabric' data-fabric=" + response['result'][j]['uuid'] + "'>";
                                    fabricHTML += "<td><font class='font10px'><div class='afcfabricindex' id='afcfabricindex" + fabricList.length.toString() + "' data-id='" + fabricList.length.toString() + "'>" + fabricList.length.toString() + "</div></font></td>";
                                    fabricHTML += "<td><font class='font10px'><div id='afcname'" + response['result'][j]['uuid'] + "'>" + response['result'][j]['name'] + "</div></font></td>";
                                    fabricHTML += "<td nowrap><font class='font10px'><div id='afcdescription'" + response['result'][j]['uuid'] + "'>" + response['result'][j]['description'] + "</div></font></td>";
                                    fabricHTML += "<td nowrap><font class='font10px'><div id='afcfabricclass'" + response['result'][j]['uuid'] + "'>" + response['result'][j]['fabric_class'] + "</div></font></td>";
                                    fabricHTML += "<td nowrap><font class='font10px'><center><img src='static/images/tag.svg' class='showattributeTooltip' width='12' height='12' data-info='' id='switchinfo" + response['result'][j]['uuid'] + "'></font></center></td>";
                                    fabricHTML += "<td nowrap><font class='font10px'>";
                                    if (response['result'][j]['is_stable'] == true) {
                                        fabricHTML += "Stable";
                                    }
                                    else {
                                        fabricHTML += "Unstable";
                                    }
                                    fabricHTML += "</font></td>";
                                    fabricHTML += "</tr>";
                                    $('#afcfabrics tr:last').after(fabricHTML);
                                    $('#afcfabrics').attr('data-afcfabricuuid', JSON.stringify(fabricList));
                                }
                            }
                        }
                    }
                    removedFabric = $(fabriclistHTML).not(fabricList).get();
                    for (var i = 0; i < removedFabric.length; i++) {
                        $('#tr' + removedFabric[i]).remove();
                        $('#afcfabrics').attr('data-afcfabricuuid', JSON.stringify(fabricList));
                        // Renumber the indices on the page
                        var indexList = $('.afcfabricindex').map(function () {
                            return $(this).data('id');
                        }).get();
                        for (var j = 0; j < indexList.length; j++) {
                            $('#afcfabricindex' + indexList[j].toString()).empty().append((j + 1).toString());
                            $('#afcfabricindex' + indexList[j].toString()).attr('data-id', (j + 1).toString());
                            $('#afcfabricindex' + indexList[j].toString()).attr('id', 'afcfabricindex' + (j + 1).toString());
                        }
                    }
                    // Once high level updates are done, now update the refreshed page with all the new information
                    for (var i = 0; i < response['result'].length; i++) {
                        $('#afcname' + response['result'][i]['uuid']).empty().append(response['result'][i]['name']);
                        $('#afcdescription' + response['result'][i]['uuid']).empty().append(response['result'][i]['description']);
                        $('#afcfabricclass' + response['result'][i]['uuid']).empty().append(response['result'][i]['fabric_class']);
                        if (response['result'][i]['is_stable'] == true) {
                            $('#afcisstable' + response['result'][i]['uuid']).empty().append('Stable');
                        }
                        else {
                            $('#afcisstable' + response['result'][i]['uuid']).empty().append('Unstable');
                        }
                        //Construct the switch info table
                        attrsetHTML = "<table class='tablewithborder' style='max-width: 500px;margin: 1px 3px 1px;padding: 2px 3px 2px;'>";
                        attrsetHTML += "<tr class='tableTitle'>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>Name</font></td>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>IP address</font></td>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>Serial number</font></td>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>Model</font></td>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>Software version</font></td>";
                        attrsetHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>Status</font></td>";
                        attrsetHTML += "</tr>";
                        for (var j in response['result'][i]['switches']) {
                            attrsetHTML += "<tr><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['name'] + "</font></td>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['ip_address'] + "</font></td>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['serial_number'] + "</font></td>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['model'] + "</font></td>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['sw_version'] + "</font></td>";
                            attrsetHTML += "<td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + response['result'][i]['switches'][j]['status'] + "</font></td>";
                            attrsetHTML += "</tr>";
                        }
                        attrsetHTML += "</table>";
                        $('#switchinfo' + response['result'][i]['uuid']).attr('data-info', attrsetHTML);
                    }
                }
            }
            else {
                showmessageBar(response['message']);
            }
        }
        setInterval(refresh, 10000);
        refresh();
    });

});


