// (C) Copyright 2020 Hewlett Packard Enterprise Development LP.


$(document).ready(function () {

    $('.editField input').keyup(function () {
        var fieldisEmpty = false;
        $('.editField input').keyup(function () {
            $('.editField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.editActions input').attr('disabled', 'disabled');
            } else {
                $('.editActions input').attr('disabled', false);
            }
        });
    });

    $('.addField input').keyup(function () {
        var fieldisEmpty = false;
        $('.addField input').keyup(function () {
            $('.addField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.addActions input').attr('disabled', 'disabled');
            } else {
                $('.addActions input').attr('disabled', false);
            }
        });
    });

    $(".editTemplate").click(async function () {
        templateid = $(this).attr('data-templateid');
        document.getElementById("editTemplate").style.display = "block";
        document.getElementById("addTemplate").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        templateInfo = await $.ajax({
            url: "/ztptemplateInfo",
            type: "POST",
            data: { id: templateid},
            success: function () {
                // Obtaining the ZTP template was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error finding ZTP Template information";
            }
        });
        templateInfo = JSON.parse(templateInfo);
        document.getElementById('templateid').value = templateInfo['id'];
        document.getElementById('editName').value = templateInfo['name'];
        document.getElementById('editDescription').value = templateInfo['description'];
        $('#editTemplatecontent').val(templateInfo['template']);
    });
});

function highlighttemplateRow(e) {
    var tr = e.parentNode.parentNode;
    var table = e.parentNode.parentNode.parentNode;
    //set current backgroundColor
    var len = table.childNodes.length;
    for (var i = 0; i < len; i++) {
        if (table.childNodes[i].nodeType == 1) {
            table.childNodes[i].style.backgroundColor = 'transparent';
        }
    }
    tr.style.backgroundColor = 'darkorange';
    var tableTitles = document.getElementsByClassName('tableTitle');
    for (var i = 0; i < tableTitles.length; i++) {
        tableTitles[i].style.backgroundColor = 'grey';
    }
}

function cleartemplateRow(e) {
    var tr = e.parentNode.parentNode;
    var table = e.parentNode.parentNode.parentNode;
    var len = table.childNodes.length;
    for (var i = 0; i < len; i++) {
        if (table.childNodes[i].nodeType == 1) {
            table.childNodes[i].style.backgroundColor = 'transparent';
        }
    }
    var tableTitles = document.getElementsByClassName('tableTitle');
    for (var i = 0; i < tableTitles.length; i++) {
        tableTitles[i].style.backgroundColor = 'grey';
    }
}

$(document).on("click", "#addztpTemplate", function () {
    document.getElementById("addTemplate").style.display = "block";
    document.getElementById("editTemplate").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
});
