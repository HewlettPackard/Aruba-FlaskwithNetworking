// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {


    $('#updateAuditlog').ready(function () {
        var refresh = async function () {
            //Obtain the obvious values
            var e = document.getElementById("entryperpage");
            var entryperpage = e.options[e.selectedIndex].value;
            var p = document.getElementById('pageoffset');
            if (p.options.length > 0) {
                var pageoffset = p.options[p.selectedIndex].value;
            }
            else {
                var pageoffset = 1;
            }
            var srt = document.getElementById('searchRecordtype');
            var searchRecordtype = srt.options[srt.selectedIndex].value;
            var sid = document.getElementById('searchStreamid');
            var searchStreamid = sid.options[sid.selectedIndex].value;
            var ss = document.getElementById('searchSeverity');
            var searchSeverity = ss.options[ss.selectedIndex].value;
            var searchDescription = document.getElementById('searchDescription').value;
            response = await $.ajax({
                type: "POST",
                url: "/updateafcAudit",
                data: { entryperpage: entryperpage, pageoffset: pageoffset, searchRecordtype: searchRecordtype, searchStreamid: searchStreamid, searchSeverity: searchSeverity, searchDescription: searchDescription },
                success: function (response) {
                    listHTML = "";
                    totalpages = response['totalentries'] / entryperpage;
                    for (var i = 0; i < response['result'].length; i++) {

                        listHTML += "<form method='post'>";
                        listHTML += "<input name='currentpageoffset' type='hidden' value='" + pageoffset + "'>";
                        listHTML += "<input name='currenttotalentries' type='hidden' value='" + response['totalentries'] + "'>";
                        listHTML += "<input name='totalpages' type='hidden' value='" + response['totalpages'] + "'>";
                        listHTML += "<input name='entryperpage' type='hidden' value='" + entryperpage + "'>";
                        listHTML += "<input name='currententryperpage' type='hidden' value='" + entryperpage + "'>";
                        listHTML += "<input name='searchRecordtype' type='hidden' value='" + searchRecordtype + "'>";
                        listHTML += "<input name='searchStreamid' type='hidden' value='" + searchStreamid + "'>";
                        listHTML += "<input name='searchDescription' type='hidden' value='" + searchDescription + "'>";
                        listHTML += "<input name='searchSeverity' type='hidden' value='" + searchSeverity + "'>";
                        if ($('#selectedItem').attr('data-id') == response['result'][i]['id']) {
                            listHTML += "<tr style='background-color: darkorange'>";
                        }
                        else {
                            listHTML += "<tr>";
                        }
                        
                        listHTML += "<td><font class='font10px'>" + (i + 1) + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response['result'][i]['record_type'].charAt(0) + response['result'][i]['record_type'].slice(1).toLowerCase() + "</font></td>";
                        listHTML += "<td nowrap><font class='font10px'>" + response['result'][i]['stream_id'] + "</font></td>";
                        listHTML += "<td><font class='font10px'>" + response['result'][i]['description'].slice(0, 200)+ "</font></td>";
                        listHTML += "<td nowrap><font class='font10px'>" + response['result'][i]['severity'].charAt(0) + response['result'][i]['severity'].slice(1).toLowerCase() + "</font></td>";
                        var ts = new Date(response['result'][i]['log_date']);
                        listHTML += "<td nowrap><font class='font10px'>" + ts.toLocaleDateString() + " " + ts.toLocaleTimeString() + "</font></td>";
                        listHTML += "<td nowrap>";
                        listHTML += "<button type='button' class='transparent-button auditItem' data-uuid='" + response['result'][i]['uuid'] + "' data-info='" + response['result'][i]['jsondata'] + "' onclick='highlightRow(this);showauditItem(" + response['result'][i]['id'] + ");$(\"#selectedItem\").attr(\"data-id\"," + response['result'][i]['id'] + ");'>";
                        listHTML += "<img src='static/images/info.svg' class='showtitleTooltip showauditItem' width='12' height='12' data-title='Information'></button></center ></td >";
                        listHTML += "</tr>";
                        listHTML += "</form>";
                    }
                    document.getElementById("auditContent").innerHTML = listHTML;
                    navigation();
                }
            });         
        }
        setInterval(refresh, 2000);
        refresh();
    });

 
});


function showauditItem(id) {
    // Based on the object type we need to build a lot of different HTML
    $("#showauditItem").show(); 
    $('#showauditItem').load('afcauditItem?id=' + id);
}


async function changeSearch() {
    $("#showauditItem").hide(); 
    clearTable();
    await navigation();
}


async function navigation() {
    //Obtain the obvious values
    clearTable();
    var e = document.getElementById("entryperpage");
    var entryperpage = e.options[e.selectedIndex].value;
    var p = document.getElementById('pageoffset');
    if (p.options.length > 0) {
        var pageoffset = p.options[p.selectedIndex].value;
    }
    else {
        var pageoffset = 1;
    }
    var srt = document.getElementById('searchRecordtype');
    var searchRecordtype = srt.options[srt.selectedIndex].value;
    var sid = document.getElementById('searchStreamid');
    var searchStreamid = sid.options[sid.selectedIndex].value;
    var ss = document.getElementById('searchSeverity');
    var searchSeverity = ss.options[ss.selectedIndex].value;
    var searchDescription = document.getElementById('searchDescription').value;
    var queryStr = "select COUNT(*) as totalentries from afcaudit where record_type like '%" + searchRecordtype + "%' AND stream_id like '%" + searchStreamid + "%' AND severity like '%" + searchSeverity + "%' AND description like '%" + searchDescription + "%'";
    response = await $.ajax({
        type: "POST",
        url: "/getafcauditCount",
        data: { queryStr: queryStr },
        success: function (response) {
            totalentries = JSON.parse(response);
            if (totalentries % entryperpage > 0) {
                totalPages = Math.floor(totalentries / entryperpage) + 1;
            }
            else {
                totalPages = Math.floor(totalentries / entryperpage);
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
            // If the currentpageoffset or currententryperpage is different from the pageoffset or entryperpage we need to hide the item detail and update the currententryperpage and currentpageoffset with the new values
            if ($('#currententryperpage').attr('value') != entryperpage || $('#currentpageoffset').attr('value') != pageoffset) {
                $('#currententryperpage').attr('value', entryperpage);
                $('#currentpageoffset').attr('value', pageoffset);
                $("#showauditItem").hide();  
            }
        }
    });
}


