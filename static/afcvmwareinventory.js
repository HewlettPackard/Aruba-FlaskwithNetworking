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
            if ("message" in integrationInfo) {
                showmessageBar(integrationInfo['message']);
            }
            else {
                $("#liProgress").hide();
            }
        }
        setInterval(refresh, 5000);
        refresh();
    });




    $('.virtualTopo').click(function () {
        $('#virtualTopo').attr('data-uuid', $(this).attr('data-uuid'));
        var refresh = async function () {  
            $('#virtualTopo').empty();
            var width = $("#virtualTopo").parent().width();
            var height = $("#virtualTopo").parent().height();
            $(".tooltip").hide();          
            vmConstruct = JSON.parse($('#topo-' + $('#virtualTopo').attr('data-uuid')).attr('data-vmConstruct'));
            data = {};
            data['name'] = vmConstruct['name'];
            data['power_state'] = vmConstruct['power_state'];
            data['uuid'] = vmConstruct['uuid'];
            data['itemtype'] = vmConstruct['itemtype'];
            data['children'] = [];
            data['children'].push(vmConstruct['children'][0]);
            var svg = d3.select("#virtualTopo")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("align", "center")      
                .append("g")
                .attr("transform", "translate(40,-150)");  // bit of margin on the left = 40

            var div = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            var img = d3.select("body").append("img")
                .attr("class", "itemtype")
                .style("opacity", 1)
                .style("background", "white");


            // Create the cluster layout:
            var cluster = d3.cluster()
                .size([width, height]); 
            // Give the data to this cluster layout:
            var root = d3.hierarchy(data, function (d) {
                for (var items in d.children) {
                    return d.children;
                }               
            });
            cluster(root);
            // Add the links between nodes:
            svg.selectAll('path')
                .data(root.descendants().slice(1))
                .enter()
                .append('path')
                .attr("d", function (d) {
                    return "M" + d.y  + "," + d.x
                        + "C" + (d.parent.y + 15) + "," + d.x
                        + " " + (d.parent.y + 100) + "," + d.parent.x 
                        + " " + d.parent.y + "," + d.parent.x;
                })
                .style("fill", 'none')
                .attr("stroke", '#ccc')


            // Add an image for each node.
            svg.selectAll("g")
                .data(root.descendants())
                .enter()
                .append("g")
                .attr("transform", function (d) {
                    return "translate(" + d.y + "," + (d.x-15) + ")"
                })
                .append("svg:image")
                .attr("xlink:href", function (d) {
                    if (d['data']['itemtype'] == "host") {
                        return "static/images/afchostnt.png";
                    }
                    else if (d['data']['itemtype'] == "vswitch") {
                        return "static/images/afcvswitchnt.png";
                    }
                    else if (d['data']['itemtype'] == "switch") {
                        return "static/images/afcswitchnt.png";
                    }
                    else if (d['data']['itemtype'] == "portgroup") {
                        return "static/images/afcportgroupnt.png";
                    }
                    else if (d['data']['itemtype'] == "vnic") {
                        return "static/images/afcvmnicnt.png";
                    }
                    else {
                        return "static/images/afcvmnicnt.png";
                    }
                })
                .on("mouseover", function (d) {
                    //Obtain the name of the node
                    if (typeof d.data != "undefined") {
                        div.transition()
                            .style("opacity", .9)
                            .style("display", "block");


                        if (d['data']['itemtype'] == "host") {
                            div.html(d['data']['name'] + "<br>Power state: " + d['data']['power_state'] + "<br>")
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else if (d['data']['itemtype'] == "nic") {
                            div.html(d['data']['name'] + "<br>MAC address: " + d['data']['mac_address'] + "<br>IP address: " + d['data']['ip_address'] + "<br>")
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else if (d['data']['itemtype'] == "portgroup") {
                            div.html(d['data']['name'] + "<br>Portgroup type: " + d['data']['type'])
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else if (d['data']['itemtype'] == "vswitch") {
                            div.html(d['data']['name'] + "<br>vSwitch type: " + d['data']['type'])
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else if (d['data']['itemtype'] == "vnic") {
                            htmlInfo = d['data']['name'] + "<br>";
                            htmlInfo += "MAC address: " + d['data']['mac_address'] + "<br>";
                            htmlInfo += "Connection status: " + d['data']['connection_status'] + "<br>";
                            htmlInfo += "Link speed: " + d['data']['link_speed'] + "<br>";
                            div.html(htmlInfo)
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else if (d['data']['itemtype'] == "switch") {
                            htmlInfo = d['data']['name'] + "<br>";
                            htmlInfo += "Description: " + d['data']['description'] + "<br>";
                            htmlInfo += "Fabric: " + d['data']['fabric'] + "<br>";
                            htmlInfo += "Fabric class: " + d['data']['fabric_class'] + " <br>";
                            htmlInfo += "IP address: " + d['data']['ip_address'] + "<br>";
                            htmlInfo += "MAC address: " + d['data']['mac_address'] + "<br>";
                            htmlInfo += "Role: " + d['data']['role'] + "<br>";
                            htmlInfo += "Serial number: " + d['data']['serial_number'] + "<br>";
                            htmlInfo += "Switch port:" + d['data']['switch_port_id'];
                            div.html(htmlInfo)
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }
                        else {
                            div.html(d['data']['name'] + "<br>")
                                .style("left", (d3.event.pageX) + "px")
                                .style("top", (d3.event.pageY - 28) + "px");
                        }


                    }
                })
                .on("mousemove", function (d) { return div.style("top", (d3.event.pageY - 10) + "px").style("left", (d3.event.pageX + 10) + "px"); })
                .on("mouseout", function (d) {
                    div.transition()
                        .style("opacity", 0)
                        .style("display", "none");
                });
        }
        setInterval(refresh, 10000);
        refresh();        
    });


    $('.expandcollapseTable').click(async function () {
        if ($(this).attr('data-collapse') == "1") {
            // Collapse (hide) the table and set arrow down
            $(this).attr('data-collapse', '0');
            $('#expandcollapse-' + $(this).attr('data-uuid')).attr('src', 'static/images/caret-down.svg');
            $('#expandcollapse-' + $(this).attr('data-uuid')).attr('data-title', 'Expand');
            $(".tr-" + $(this).attr('data-uuid') ).hide();
        }
        else {
            //expand (show) the table and set arrow up
            $('#' + $(this).attr('data-uuid')).show();
            $(this).attr('data-collapse', '1');
            $('#expandcollapse-' + $(this).attr('data-uuid')).attr('src', 'static/images/caret-up.svg');
            $('#expandcollapse-' + $(this).attr('data-uuid')).attr('data-title', 'Collapse');
            $(".tr-" + $(this).attr('data-uuid')).show();
        }
    });
       

    $('.afcvmwareinventoryStatus').ready(function () {
        // Obtain the integration information from AFC
        var refresh = async function () {
            response = await $.ajax({
                type: "POST",
                data: {},
                url: "/afcvmwareinventoryStatus",
                success: function () {
                },
                error: function () {
                }
            });
            vmInfo = JSON.parse(response);
            defaultsetHTML = "<table class='tablenoborder' style='max-width: 400px;'>";
            defaultsetHTML += "<tr class='border tableTitle'>";
            defaultsetHTML += "<td width='50%' align='left' nowrap><font class='font12pxwhite'>Parameter</font></td>";
            defaultsetHTML += "<td width='50%' align='left' nowrap><font class='font12pxwhite'>Value</font></td>";
            defaultsetHTML += "</tr>";

            for (var i in vmInfo) {
            swsetHTML = defaultsetHTML;
            vmsetHTML = defaultsetHTML;
            pgsetHTML = defaultsetHTML;
            nicsetHTML = defaultsetHTML;
                vssetHTML = defaultsetHTML;
                // This is the host information
                vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>VM power state</font></td>";
                vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['power_state'].charAt(0).toUpperCase() + vmInfo[i]['power_state'].slice(1) + "</font></td>";
                vmsetHTML += "</tr>";
                for (var k = 0; k < vmInfo[i]['children'].length; k++) {
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Virtual NIC</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['name'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>IP address</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['ip_address'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>MAC address</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['mac_address'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>VLAN</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['vlan'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>VNI</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['vni'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    vmsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>VTEP</font></td>";
                    vmsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['vtep'] + "</font></td>";
                    vmsetHTML += "</tr>";
                    if (k < (vmInfo[i]['children'].length - 1)) {
                        vmsetHTML += "<tr><td colspan='2' class='whiteBG'></td></tr>";
                    }
                    if ("children" in vmInfo[i]['children'][k]) {
                        //The port group information
                        for (var l = 0; l < vmInfo[i]['children'][k]['children'].length; l++) {
                            pgsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Name</font></td>";
                            pgsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['name'] + "</font></td>";
                            pgsetHTML += "</tr>";
                            pgsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Port group type</font></td>";
                            pgsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['type'] + "</font></td>";
                            pgsetHTML += "</tr>";
                            // Obtain the vswitch information within the portgroups
                            
                            if ("children" in vmInfo[i]['children'][k]['children'][l]) {
                                vssetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Name</font></td>";
                                vssetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['name'] + "</font></td>";
                                vssetHTML += "</tr>";
                                vssetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>vSwitch type</font></td>";
                                vssetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['type'] + "</font></td>";
                                vssetHTML += "</tr>";
                            }
                            // Obtain the physical NIC information
                            for (var m = 0; m < vmInfo[i]['children'][k]['children'][l]['children'][0]['children'].length; m++) {
                                nicsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Name</font></td>";
                                nicsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['name'] + "</font></td>";
                                nicsetHTML += "</tr>";
                                nicsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>MAC address</font></td>";
                                nicsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['mac_address'] + "</font></td>";
                                nicsetHTML += "</tr>";
                                if (m <  (vmInfo[i]['children'][k]['children'][l]['children'][0]['children'].length - 1) ) {
                                    nicsetHTML += "<tr><td colspan='2' class='whiteBG'></td></tr>";
                                }
                                for (var n = 0; n < vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'].length; n++) { 
                                    if (vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['switch_port_id'] != "") {
                                        if (vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'].length > 0) {
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Name</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['name'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>MAC address</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['mac_address'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>IP address</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['ip_address'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Serial number</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['serial_number'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Fabric</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['fabric'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Fabric class</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['fabric_class'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Switch role</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['role'].charAt(0).toUpperCase() + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][0]['role'].slice(1) + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Description</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['description'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Interface</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['children'][n]['switch_port_id'] + "</font></td>";
                                            swsetHTML += "</tr>";
                                            swsetHTML += "<tr class='border'><td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>Link speed</font></td>";
                                            swsetHTML += "<td class='whiteBG' align='left' nowrap><font class='font10pxgrey'>" + vmInfo[i]['children'][k]['children'][l]['children'][0]['children'][m]['link_speed'] + "</font></td>";
                                        }
                                        if (m < (vmInfo[i]['children'][k]['children'][l]['children'][0]['children'].length - 1 )) {
                                            swsetHTML += "<tr><td colspan='2' class='whiteBG'></td></tr>";
                                        }
                                    }
                                    else {
                                        swsetHTML = "<table class='tablenoborder' style='max-width: 200px;'><tr><td colspan='2' class='whiteBG' align='center' nowrap><font class='font10pxgrey'>Not connected</font></td>";
                                    }
                                }                
                            }
                    

                        }
                        $('#topo-' + vmInfo[i]['uuid']).attr('data-vmConstruct', JSON.stringify(vmInfo[i]));
                        vmsetHTML += "</table>";
                        pgsetHTML += "</tr></table>";
                        vssetHTML += "</tr></table>";
                        nicsetHTML += "</tr></table>";
                        swsetHTML += "</tr></table>";
                        $('#vmInfo-' + vmInfo[i]['uuid']).attr('data-info', vmsetHTML);
                        $('#portgroupInfo-' + vmInfo[i]['uuid']).attr('data-info', pgsetHTML);
                        $('#vswitchInfo-' + vmInfo[i]['uuid']).attr('data-info', vssetHTML);
                        $('#vnicInfo-' + vmInfo[i]['uuid']).attr('data-info', nicsetHTML);
                        $('#arubaswitchInfo-' + vmInfo[i]['uuid']).attr('data-info', swsetHTML);


                    }
                }

            }

        }
        setInterval(refresh, 10000);
        refresh();
    });
});


