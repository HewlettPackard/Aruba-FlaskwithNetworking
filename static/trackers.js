// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.


$('#updateTracker').ready(function () {
    var refresh = async function () {
        //Obtain the obvious values
        var tt = document.getElementById('updateTracker');
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
        var p = document.getElementById('pageoffset');
        if (p.options.length > 0) {
            var pageoffset = p.options[p.selectedIndex].value;
        }
        else {
            var pageoffset = 1;
        }
        if (tt.getAttribute('data-type') == "dhcp") {
            var st = document.getElementById('searchType');
            var searchType = st.options[st.selectedIndex].value;
            var searchInfo = document.getElementById('searchInfo').value;
            //Obtain the relevant information from the database
            response = await $.ajax({
                type: "POST",
                url: "/updateDHCPtracker",
                data: { entryperpage: entryperpage, pageoffset: pageoffset, searchType: searchType, searchInfo: searchInfo },
                success: function (response) {
                    result = JSON.parse(response);
                    response = result['result'];
                    //Render the table
                    listHTML = "";
                    for (var i = 0; i < response.length; i++) {
                        listHTML += "<form method='post'><input type='hidden' name='id' value='" + response[i]['id'] + "' /><tr>";
                        var ts = new Date(response[i]['utctime']*1000);
                        listHTML += "<td><font class='font10px'>" + ts.toLocaleDateString() + " " + ts.toLocaleTimeString()  + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['dhcptype'] + "</font></td>";
                        listHTML += "<td width='60%' nowrap><font class='font10px'>" + response[i]['information'] + "</font></td>";
                        if (result['accessright'] == true) {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' class='selectEntry' id='selectEntry" + response[i]['id'] + "' data-id='" + response[i]['id'] + "'";
                            if ($('#selectEntry' + response[i]['id']).is(":checked")) {
                                listHTML += " checked ";
                            }
                            listHTML += "></td>";
                            listHTML += "<td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' onclick=\"if (confirm('Are you sure?')) deleteEntry(" + response[i]['id'] + ",'dhcptracker');\"><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr ></form > ";
                        }
                        else {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' data-id='" + response[i]['id'] + "' class='selectEntry' disabled></td><td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' style='opacity:0.2;pointer-events:none;'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr></form>";
                        }
                    }
                    document.getElementById("logList").innerHTML = listHTML;
                    navigation();
                }
            });
        }
        else if (tt.getAttribute('data-type') == "snmp") {
            var searchSource = document.getElementById('searchSource').value;
            var sv = document.getElementById('searchVersion');
            var searchVersion = sv.options[sv.selectedIndex].value;
            var sc = document.getElementById('searchCommunity');
            var searchCommunity = sc.options[sc.selectedIndex].value;
            var searchInfo = document.getElementById('searchInfo').value;
            response = await $.ajax({
                type: "POST",
                url: "/updateSNMPtracker",
                data: { entryperpage: entryperpage, pageoffset: pageoffset, searchSource:searchSource, searchVersion: searchVersion, searchCommunity: searchCommunity, searchInfo: searchInfo },
                success: function (response) {
                    result = JSON.parse(response);
                    response = result['result'];
                    listHTML = "";
                    for (var i = 0; i < response.length; i++) {
                        listHTML += "<form method='post'><input type='hidden' name='id' value='" + response[i]['id'] + "' /><tr>";
                        var ts = new Date(response[i]['utctime'] * 1000);
                        listHTML += "<td><font class='font10px'>" + ts.toLocaleDateString() + " " + ts.toLocaleTimeString() + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['source'] + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['version'] + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['community'] + "</font></td>";
                        listHTML += "<td width='60%' nowrap><font class='font10px'>" + response[i]['information'] + "</font></td>";
                        if (result['accessright'] == true) {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' class='selectEntry' id='selectEntry" + response[i]['id'] + "' data-id='" + response[i]['id'] + "'";
                            if ($('#selectEntry' + response[i]['id']).is(":checked")) {
                                listHTML += " checked ";
                            }
                            listHTML += "></td>";
                            listHTML += "<td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' onclick=\"if (confirm('Are you sure?')) deleteEntry(" + response[i]['id'] + ",'snmptracker');\"><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr ></form > ";
                        }
                        else {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' data-id='" + response[i]['id'] + "' class='selectEntry' disabled></td><td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' style='opacity:0.2;pointer-events:none;'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr></form>";
                        }
                    }
                    document.getElementById("logList").innerHTML = listHTML;
                    navigation();
                }
            });
        }
        else if (tt.getAttribute('data-type') == "syslog") {
            var searchSource = document.getElementById('searchSource').value;
            var sf = document.getElementById('searchFacility');
            var searchFacility = sf.options[sf.selectedIndex].value;
            var ss = document.getElementById('searchSeverity');
            var searchSeverity = ss.options[ss.selectedIndex].value;
            var searchInfo = document.getElementById('searchInfo').value;
            response = await $.ajax({
                type: "POST",
                url: "/updateSyslogtracker",
                data: { entryperpage: entryperpage, pageoffset: pageoffset, searchSource: searchSource, searchFacility: searchFacility, searchSeverity: searchSeverity, searchInfo: searchInfo },
                success: function (response) {
                    result = JSON.parse(response);
                    response = result['result'];
                    listHTML = "";
                    for (var i = 0; i < response.length; i++) {
                        listHTML += "<form method='post'><input type='hidden' name='id' value='" + response[i]['id'] + "' /><tr>";
                        var ts = new Date(response[i]['utctime'] * 1000);
                        listHTML += "<td><font class='font10px'>" + ts.toLocaleDateString() + " " + ts.toLocaleTimeString() + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['source'] + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['facility'] + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response[i]['severity'] + "</font></td>";
                        listHTML += "<td width='60%' nowrap><font class='font10px'>" + response[i]['information'].slice(0, 250) + "</font></td>";
                        if (result['accessright'] == true) {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' class='selectEntry' id='selectEntry" + response[i]['id'] + "' data-id='" + response[i]['id'] + "'";
                            if ($('#selectEntry' + response[i]['id']).is(":checked")) {
                                listHTML += " checked ";
                            }
                            listHTML += "></td>";
                            listHTML += "<td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' onclick=\"if (confirm('Are you sure?')) deleteEntry(" + response[i]['id'] + ",'syslog');\"><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr ></form > ";
                        }
                        else {
                            listHTML += "<td align='right' style='vertical-align:bottom;' width='1%'><input type='checkbox' data-id='" + response[i]['id'] + "' class='selectEntry' disabled></td><td align='right' width='1%'><button name='action' value='Delete' class='transparent-button' style='opacity:0.2;pointer-events:none;'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete'></button></td></tr></form>";
                        }
                    }
                    document.getElementById("logList").innerHTML = listHTML;
                    navigation();
                }
            });
        }
    }
    setInterval(refresh, 2000);
    refresh();
});

async function navigation() {
    //Obtain the obvious values
    var tt = document.getElementById('updateTracker');
    var e = document.getElementById("entryperpage");
    var entryperpage = e.options[e.selectedIndex].value;
    var p = document.getElementById('pageoffset');
    if (p.options.length > 0) {
        var pageoffset = p.options[p.selectedIndex].value;
    }
    else {
        var pageoffset = 1;
    }
    if (tt.getAttribute('data-type') == "dhcp") {
        var st = document.getElementById('searchType');
        var searchType = st.options[st.selectedIndex].value;
        var queryStr = "select count(*) as totalentries from dhcptracker where dhcptype like '%" + searchType + "%' AND information like '%" + document.getElementById('searchInfo').value + "%'";
    }
    else if (tt.getAttribute('data-type') == "snmp") {
        var sv = document.getElementById('searchVersion');
        var searchVersion = sv.options[sv.selectedIndex].value;
        var sc = document.getElementById('searchCommunity');
        var searchCommunity = sc.options[sc.selectedIndex].value;
        var queryStr = "select count(*) as totalentries from snmptracker where source like '%" + document.getElementById('searchSource').value + "%' AND version like '%" + searchVersion + "%' AND community like '%" + searchCommunity + "%' AND information like '%" + document.getElementById('searchInfo').value + "%'";
    }
    else if (tt.getAttribute('data-type') == "syslog") {
        var sf = document.getElementById('searchFacility');
        var searchFacility = sf.options[sf.selectedIndex].value;
        var ss = document.getElementById('searchSeverity');
        var searchSeverity = ss.options[ss.selectedIndex].value;
        var queryStr = "select count(*) as totalentries from syslog where source like '%" + document.getElementById('searchSource').value + "%' AND facility like '%" + searchFacility + "%' AND severity like '%" + searchSeverity + "%' AND information like '%" + document.getElementById('searchInfo').value + "%'";

    }
    response = await $.ajax({
        type: "POST",
        url: "/getTrackercount",
        data: { queryStr: queryStr },
        success: function (response) {
            totalentries = JSON.parse(response);
            $("#pageoffset").empty();
            if (totalentries % entryperpage > 0) {
                totalPages=Math.floor(totalentries/entryperpage)+1;
            }
            else {
                 totalPages=Math.floor(totalentries / entryperpage);
            }
            document.getElementById("totalpagesph").innerHTML = totalPages;
            $("#pageoffset").empty();
            for (pageNumber = 1; pageNumber < (totalPages + 1); pageNumber++) {

                $('#pageoffset').append($('<option>', {
                    value: pageNumber,
                    text: pageNumber
                }));
            }
            if (totalPages < pageoffset) {
                pageoffset = 1;
            }
            $('#pageoffset').val(pageoffset);

        }
    });
}


async function deleteEntry(id, dbtable) {
    response = await $.ajax({
        type: "POST",
        url: "/deleteTrackerentry",
        data: { dbtable: dbtable, id: id  },
        success: function (response) {
        }
    });
}

function selectAll(dbtable) {
    $('.selectEntry').each(function () {
        $(this).attr('checked', !$(this).attr('checked'));
    });
}

async function deleteSelection(dbtable) {
    var selection = [];
    // Obtain all the id's from the checkboxes, but only the ones that are selected
    $('.selectEntry').each(function () {
        if ($(this).attr('checked')) {
            selection.push($(this).attr('data-id'));
        }
    });
    response = await $.ajax({
        type: "POST",
        url: "/deleteTrackerselection",
        data: { dbtable: dbtable, selection: selection.toString() },
        success: function (response) {
        }
    });
}