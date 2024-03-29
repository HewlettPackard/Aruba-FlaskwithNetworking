// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $(".showendpoints").click(function () {
        selectId = $(this).closest(".showendpoints").attr("data-id");
        var refresh = async function () {
            //document.getElementById("showEndpoints").style.display = "block";
            //document.getElementById("showTopology").style.display = "none";

            endpointInfo = await $.ajax({
                url: "/endpointInfo",
                type: "POST",
                data: { id: selectId },
                success: function () {
                },
                error: function () {
                }
            });
            endpointHTML = endpointInfo;
            endpointInfo = JSON.parse(endpointInfo);
            if (endpointInfo.length > 0) {
                endpointHTML = "<table class='tablenoborder'><tr style='background-color: grey;'>";
                endpointHTML += "<td colspan='5'><font class='font13pxwhite'><center>Connections of " + endpointInfo[0]['hostname'] + ": " + endpointInfo[0]['switchip'] + " (" + endpointInfo[0]['systemmac'] + ")</center></font></td></tr>";
                endpointHTML += "<tr><td><font class='font13pxgrey'>Local interface</font></td><td><font class='font13pxgrey'>Remote hostname</font></td><td><font class='font13pxgrey'>Remote interface</font></td><td><font class='font13pxgrey'>Remote IP address</font></td><td><font class='font13pxgrey'>Remote System MAC address</font></td></tr>";
                for (var i = 0; i < endpointInfo.length; i++) {
                    endpointHTML += "<tr><td><font class='font11px'>" + endpointInfo[i]['interface'] + "</font></td><td><font class='font11px'>" + endpointInfo[i]['remotehostname'] + "</font></td><td><font class='font11px'>" + endpointInfo[i]['remoteinterface'] + "</font></td><td><font class='font11px'>" + endpointInfo[i]['remoteswitchip'] + "</font></td><td><font class='font11px'>" + endpointInfo[i]['remotesystemmac'] + "</font></td></tr>";
                }
                endpointHTML += "</table>";
                document.getElementById("showEndpoints").innerHTML = endpointHTML;
            }
        }
        setInterval(refresh, 10000);
        refresh();
        });
    
    
    $(".showendpoints").click(async function () {
        selectId = $(this).closest(".showendpoints").attr("data-id");
        topoInfo = await $.ajax({
            url: "/topoInfo",
            type: "POST",
            data: { id: selectId },
            success: function () {
                // Obtaining the topology information was successful
                document.getElementById("liProgress").style.display = "none";

            },
            error: function () {
                showmessageBar("Error finding topology information");
            }
        });
        topoInfo = JSON.parse(topoInfo);
            var baseNodes = topoInfo['nodes'];
            var baseLinks = topoInfo['links'];

            var canvas = d3.select("#showTopo"),
                width = canvas.attr("width"),
                height = canvas.attr("height"),
                r = 10,
                ctx = canvas.node().getContext("2d"),
                simulation = d3.forceSimulation()
                    .force("x", d3.forceX(width / 2))
                    .force("y", d3.forceY(height / 2))
                    .force("collide", d3.forceCollide(r))
                    .force("charge", d3.forceManyBody()
                        .strength(-500))
                    .force("link", d3.forceLink()
                        .id(function (d) { return d.name }))
                    .on("tick", update);

            simulation
                .nodes(baseNodes)
                .force("link")
                .links(baseLinks);

            canvas
                .call(d3.drag()
                    .container(canvas.node())
                    .subject(dragsubject)
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            function update() {
                ctx.clearRect(0, 0, width, height);
                ctx.beginPath();
                ctx.globalAlpha = 0.3;
                baseLinks.forEach(drawLink);
                ctx.stroke();
                ctx.beginPath();
                ctx.globalAlpha = 1.0;
                baseNodes.forEach(drawNode);
                ctx.fill();
            }

            function drawNode(d) {
                ctx.moveTo(d.x, d.y);
                ctx.fillStyle = '#69b3a2';
                ctx.fillRect(d.x, d.y, 180, 30);
                ctx.font = "10px Arial";
                ctx.fillStyle = "black";
                ctx.textAlign = "center";
                ctx.fillText(d.label + " (" + d.name + ")", d.x + 90, d.y + 20);
            }

            function drawLink(l) {
                ctx.moveTo(l.source.x + 70, l.source.y + 15);
                ctx.lineTo(l.target.x + 70, l.target.y + 15);
            }

            function dragsubject() {
                return simulation.find(d3.event.x, d3.event.y);
            }

            function dragstarted() {
                if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                d3.event.subject.fx = d3.event.subject.x;
                d3.event.subject.fy = d3.event.subject.y;
            }

            function dragged() {
                d3.event.subject.fx = d3.event.x;
                d3.event.subject.fy = d3.event.y;
            }

            function dragended() {
                if (!d3.event.active) simulation.alphaTarget(0);
                d3.event.subject.fx = d3.event.subject.x;
                d3.event.subject.fy = d3.event.subject.y;
            }
            update();
    });



    $('.deviceStatus').ready(function () {
        var refresh = async function () {
            deviceStatus = document.getElementsByClassName('deviceStatus');
            for (var i = 0; i < deviceStatus.length; i++) {
                deviceid = deviceStatus.item(i).getAttribute('data-deviceid');
                await $.ajax({
                    type: "POST",
                    data: { 'deviceid': deviceid },
                    url: "/topodeviceStatus",
                    success: function (response) {
                        if (response == "Online") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/status-good.svg' height='12' width='12' class='showtitleTooltip' data-title='Device is online'>";
                        }
                        else {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/status-critical.svg' height='12' width='12'  class='showtitleTooltip' data-title='Device is offline'>";
                        }
                    }
                });
            }
        }
        setInterval(refresh, 10000);
        refresh();
    });
 
});