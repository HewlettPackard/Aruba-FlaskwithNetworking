// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.




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

    $(".editdeviceImage").click(async function () {
        imageid = $(this).attr('data-imageid');
        document.getElementById("editImage").style.display = "block";
        document.getElementById("addImage").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        tableRow = $(this).closest('tr').index();
        imageInfo = await $.ajax({
            url: "/imageInfo",
            type: "POST",
            data: { id: imageid },
            success: function () {
                // Obtaining the device image information was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error finding software image information";
            }
        });
        imageInfo = JSON.parse(imageInfo);
        document.getElementById('imageid').value = imageInfo['id'];
        document.getElementById('editFilename').value = imageInfo['filename'];
        document.getElementById('editName').value = imageInfo['name'];
        document.getElementById('editDevicefamily').value = imageInfo['devicefamily'];
        document.getElementById('editVersion').value = imageInfo['version'];
        document.getElementById('editImagename').innerHTML = "<font class='font12px'>" + imageInfo['filename'] + "</font>";
    });
});


$(document).on("click", "#searchImage", function () {
    document.getElementById("editImage").style.display = "none";
    document.getElementById("addImage").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    if (document.getElementById("pageoffset")) {
        var e = document.getElementById("pageoffset");
        var pageoffset = e.options[e.selectedIndex].value;
    }
    else {
        pageoffset = 0;
    }
    $("div[data-imagemgr='imagemgr']").load('deviceimages?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
    });


function entryperPage() {
    document.getElementById("editImage").style.display = "none";
    document.getElementById("addImage").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    var pageoffset = 0;
    $("div[data-imagemgr='imagemgr']").load('deviceimages?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
}

function pageNumber() {
    document.getElementById("editImage").style.display = "none";
    document.getElementById("addImage").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    if (document.getElementById("pageoffset")) {
        var e = document.getElementById("pageoffset");
        var pageoffset = e.options[e.selectedIndex].value;
    }
    else {
        pageoffset = 0;
    }
    $("div[data-imagemgr='imagemgr']").load('deviceimages?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
}

$(document).on("click", "#adddeviceImage", function () {
    document.getElementById("addImage").style.display = "block";
    document.getElementById("editImage").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
});



