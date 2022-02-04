// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {


    $('.showrestCX').mouseover(async function (event) {
        url = $('#' + this.id).attr('data-url');
        deviceid = $('#' + this.id).attr('data-deviceid');
        htmlid = this.id;
        // First show waiting popup
        $('#showcxTooltip').empty().append(waitingHTML());
        $('#showcxTooltip').show();

        console.log(deviceid);
        console.log(htmlid);
        console.log(url);

        response = await $.ajax({
            type: "POST",
            url: "/showrestCX",
            data: { deviceid: deviceid, url: url, htmlid: htmlid},
            success: function (response) {
                result = JSON.parse(response);
                //Render the table    
                tooltipHTML = "";
                if (htmlid.includes("showrestCXipv6")) {
                    tooltipHTML = generateIPv6(result);
                }
                else if (htmlid.includes("showrestCXlldp")) {
                    tooltipHTML = generatelldp(result);
                }
                else if (htmlid.includes("showrestCXvsfpart")) {
                    tooltipHTML = generatevsfpartnumber(result);
                }
                // Based on the URL we need to construct the HTML
                $('#' + htmlid).attr('data-info', tooltipHTML);


        if ((event.pageX + 350) > self.innerWidth) {
            var left = event.pageX - 300;
        }
        else {
            var left = event.pageX + 10;
        }
        if (typeof ($('#' + htmlid).attr('data-url')) !== 'undefined') {
            tooltipHeight = ($('#' + htmlid).attr('data-info').match(/<tr/g) || []).length * 10;
            if (self.innerHeight < (tooltipHeight + event.pageY)) {
                var top = Math.abs(event.pageY - Math.abs(Math.abs(tooltipHeight) / 3) * 4);
            }
            else {
                var top = event.pageY - 280;
            }
        }
        else {
            var top = event.pageY - 280;
        }
        $("#showcxTooltip").css({
            position: 'absolute',
            zIndex: 5000,
            left: left,
            top: top,
            backgroundColor: 'transparent',
            width: '400px',
        });
                                                          

                $('#showcxTooltip').empty().append($('#' + htmlid).attr('data-info'));
                $('#showcxTooltip').show();

            }
        });

        function generateIPv6(result) {
            tooltipHTML = "<table class='tablewithborder' style='max-width: 500px;margin: 1px 3px 1px;padding: 2px 3px 2px;'>";
            tooltipHTML += "<tr class='tableTitle'>";
            tooltipHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font12pxwhite'>IPv6 address(es)</font></td>";
            for (var j in result) {
                tooltipHTML += "<tr><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + j + "</font></td></tr>";
            }
            tooltipHTML += "</table>";
            return tooltipHTML;
        }


        function generatelldp(result) {
            tooltipHTML = "<table class='tablewithborder' style='max-width: 500px;margin: 1px 3px 1px;padding: 2px 3px 2px;'>";
            tooltipHTML += "<tr class='tableTitle'>";
            tooltipHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;' colspan='2'><font class='font12pxwhite'>LLDP information</font></td></tr>";
            for (var j in result) {
                tooltipHTML += "<tr><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>Chassis description</font></td><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + result[j]['neighbor_info']['chassis_description'] + "</font></td></tr>";
                tooltipHTML += "<tr><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>Chassis name</font></td><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + result[j]['neighbor_info']['chassis_name'] + "</font></td></tr>";
                tooltipHTML += "<tr><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>Port description</font></td><td class='whiteBG' align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;'><font class='font10pxgrey'>" + result[j]['neighbor_info']['port_description'] + "</font></td></tr>";
            }
            tooltipHTML += "</table>";
            return tooltipHTML;
        }


        function generatevsfpartnumber(result) {
            console.log(result);
            tooltipHTML = "<table class='tablewithborder' style='max-width: 500px;margin: 1px 3px 1px;padding: 2px 3px 2px;'>";
            tooltipHTML += "<tr class='tableTitle'>";
            tooltipHTML += "<td align='left' nowrap style='margin: 1px 3px 1px;padding: 2px 3px 2px;' colspan='2'><font class='font12pxwhite'>Part number information</font></td></tr>";
            tooltipHTML += "</table>";
            return tooltipHTML;
        }


        function waitingHTML() {
            tooltipHTML = "<table class='tablenoborder' style='max-width: 150px;margin: 1px 3px 1px;padding: 2px 3px 2px;'>";
            tooltipHTML += "<tr class='tableTitle'>";
            tooltipHTML += "<td class='whiteBG'><center><font class='font12pxgrey'>Obtaining information...</font></center></td>";
            tooltipHTML += "</table>";
            return tooltipHTML;
        }

    });

    $('.showrestCX').mouseout(function () {
        $('#showcxTooltip').hide();
    });


    async function sysInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxsysinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table           
            }
        });
    }


    async function portInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxportinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table 
                console.log(result);
            }
        });
    }

    
    async function vsxInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxvsxinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table 
                console.log(result);          
            }
        });
    }


    async function vsfInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxvsfinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table 
                console.log(result);       
            }
        });
    }


    async function interfaceInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxinterfaceinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table 
                console.log(result);          
            }
        });
    }


    async function resourceInfo(deviceid) {
        response = await $.ajax({
            type: "POST",
            url: "/cxresourceinfo",
            data: { deviceid: deviceid },
            success: function (response) {
                result = JSON.parse(response);
                //Render the table 
                console.log(result);          
            }
        });
    }
    
});


