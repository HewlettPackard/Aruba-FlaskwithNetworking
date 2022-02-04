// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {


    $('.afcStatus').ready(function () {
        // Obtain the integration information from AFC, to check whether AFC is online
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
        }
        setInterval(refresh, 5000);
        refresh();
    });


    $('.switchInfo').click(function () {
        // Obtain the switch information from AFC
        $('#afcswitchInfo').attr('data-uuid', $(this).attr("data-uuid"));
        $('#afcswitchInfo').empty().append("<br><center><font class='font12pxgrey'>Obtain switch information...</font></center>");
        $('#afcportInfo').empty().append("<br><center><font class='font12pxgrey'>Obtain port information...</font></center>");
        var refresh = async function () {
            response = await $.ajax({
                type: "POST",
                data: { uuid: $('#afcswitchInfo').attr("data-uuid")},
                url: "/afcswitchInfo",
                success: function () {              
                },
                error: function () {
                }
            });
            if ("info" in response) {
                $("#liProgress").hide();
                var s = new Date(response['info']['boot_time']).toLocaleDateString("en-US");
                var duration = Math.abs((new Date($.now()) - new Date(response['info']['boot_time'])) / 1000);
                var days = Math.floor(duration / (3600 * 24));
                duration -= days * 3600 * 24;
                var hours = Math.floor(duration / 3600);
                duration -= hours * 3600;
                var minutes = Math.floor(duration / 60);
                duration -= minutes * 60;
                switchHTML = "<table class='tablewithborder'>";
                switchHTML += "<tr class='tableTitle'><td align='center' colspan='8'><font class='font10pxwhite'>Switch information</font></td></tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Uptime</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + days + " days, " + hours + " hours, " + minutes + " minutes, " + Math.floor(duration) + " seconds</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Health status</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['health']['status'].charAt(0).toUpperCase() + response['info']['health']['status'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Status</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['status'].charAt(0) + response['info']['status'].slice(1).toLowerCase() + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Hostname</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['name'] + "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>System ID</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['id'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Serial number</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['serial_number'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Switch role</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['role'].charAt(0).toUpperCase() + response['info']['role'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Operational software</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['sw_version'] + "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Model</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['model'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Description</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG' colspan='3'><font class='font9pxgrey'>" + response['info']['description'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Hardware revision</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['hw_revision'] + "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Primary version</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['primary_version'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Secondary version</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['secondary_version'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Booted partition</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['booted_partition'].charAt(0).toUpperCase() + response['info']['booted_partition'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Default partition</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['default_partition'].charAt(0).toUpperCase() + response['info']['default_partition'].slice(1) + "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Staged software version</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                if (response['info']['staged_sw_version'] == null) {
                    switchHTML += "Not staged";
                }
                else {
                    switchHTML += response['info']['staged_sw_version'];
                }
                switchHTML + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Next boot partition</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['next_boot_partition'].charAt(0).toUpperCase() + response['info']['next_boot_partition'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Software state</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                if (response['info']['software_state']) {
                    switchHTML += response['info']['software_state'].charAt(0).toUpperCase() + response['info']['software_state'].slice(1);
                }
                else {
                    switchHTML += "Unknown";
                }

                switchHTML += "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Operational stage</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['operational_stage'].charAt(0) + response['info']['operational_stage'].slice(1).toLowerCase() + "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv4 address/mask</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['ip_address'] + "/" + response['info']['ip_mask'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv6 address/mask</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['ip_address_v6'] + "/" + response['info']['ip_mask_v6'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv4 gateway</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                for (var i in response['info']['ip_gateway']) {
                    switchHTML += response['info']['ip_gateway'][i] + "  ";
                }
                switchHTML = switchHTML.slice(0, -2);
                switchHTML += "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv6 gateway</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                for (var i in response['info']['ip_gateway_v6']) {
                    switchHTML += response['info']['ip_gateway_v6'][i] + "  ";
                }
                switchHTML = switchHTML.slice(0, -2);
                switchHTML += "</font></td>";
                switchHTML += "</tr>";
                switchHTML += "<tr class='tableTitle'>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv4 address mode</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['ip_mode'].charAt(0).toUpperCase() + response['info']['ip_mode'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>IPv6 address mode</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['ip_mode_v6'].charAt(0).toUpperCase() + response['info']['ip_mode_v6'].slice(1) + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'>Interface MAC address</font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['info']['mac_address'] + "</font></td>";
                switchHTML += "<td align='left' nowrap><font class='font10pxwhite'></font></td>";
                switchHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'></font></td>";
                switchHTML += "</tr>";
                switchHTML += "</table>";
                $('#afcswitchInfo').empty().append(switchHTML);
                portHTML = "<table class='tablewithborder'>";
                portHTML += "<tr class='tableTitle'><td align='center' colspan='8'><font class='font10pxwhite'>Port information</font></td></tr>";
                portHTML += "<tr class='tableTitle'>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Interface</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Speed(s) (Mbps)</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Transceiver type</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Formfactor</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Admin state</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Link state</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>Port mode</font></td>";
                portHTML += "<td align='left' nowrap><font class='font10pxwhite'>MTU</font></td>";
                portHTML += "</tr>";
                for (var i = 0; i < response['portInfo'].length; i++) {
                    portHTML += "<tr class='tableTitle'>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['portInfo'][i]['name'] + "</font></td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                    for (var j = 0; j < response['portInfo'][i]['speed']['permitted'].length; j++) {
                        portHTML += response['portInfo'][i]['speed']['permitted'][j] + ", ";
                    }
                    portHTML = portHTML.slice(0, -2);
                    portHTML += "</font></td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['portInfo'][i]['transceiver_bay_type'] + "</font</td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['portInfo'][i]['form_factor'] + "</font</td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['portInfo'][i]['link_state'] + "</font</td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>" + response['portInfo'][i]['admin_state'] + "</font></td>";
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                    if (response['portInfo'][i]['port_mode'] != null) {
                        portHTML += response['portInfo'][i]['port_mode'] + "</font></td>";
                    }
                    else {
                        portHTML += "-</font></td>";
                    }
                    portHTML += "<td align='left' nowrap class='whiteBG'><font class='font9pxgrey'>";
                    if (response['portInfo'][i]['mtu'] != null) {
                        portHTML += response['portInfo'][i]['mtu'] + "</font></td>";
                    }
                    else {
                        portHTML += "-</font></td>";
                    }

                    switchHTML += "</tr>";

                }
                portHTML += "</table>";
                $('#afcportInfo').empty().append(portHTML);
            }
        }
        setInterval(refresh, 10000);
        refresh();
    });

});


