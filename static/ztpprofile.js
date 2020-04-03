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

    $(".editProfile").click(async function () {
        profileid = $(this).attr('data-profileid');
        document.getElementById("editProfile").style.display = "block";
        document.getElementById("addProfile").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        profileInfo = await $.ajax({
            url: "/ztpprofileInfo",
            type: "POST",
            data: { id: profileid },
            success: function () {
                // Obtaining the ZTP profile was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error finding ZTP Profile information";
            }
        });
        profileInfo = JSON.parse(profileInfo);
        document.getElementById('profileid').value = profileInfo['id'];
        document.getElementById('editName').value = profileInfo['name'];
        document.getElementById('editUsername').value = profileInfo['username'];
        document.getElementById('editPassword').value = profileInfo['password'];
        document.getElementById('editDNS').value = profileInfo['dns'];
        document.getElementById('editVRF').value = profileInfo['vrf'];
    });



$(".deleteProfile").click(async function (element) {
    profileid = $(this).attr('data-profileid');
    var removeSuccess = "0";
    document.getElementById("editProfile").style.display = "none";
    document.getElementById("addProfile").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    profileInfo = await $.ajax({
        url: "/checkztpProfile",
        type: "POST",
        data: { profileid: profileid },
        success: function () {
            // Check if ZTP profile exists is successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error checking ZTP profile";
        }
    });
    // If result is 1, there are profiles assigned to devices so we cannot delete
    if (profileInfo == "1") {
        document.getElementById("liProgress").style.display = "block";
        document.getElementById("progresstooltip").style.display = "none";
        progressInfo.innerHTML = "Profile assigned to device(s), cannot delete";
    }
    else {
        isok = confirm("Delete profile");
        if (isok == true) {
            profileInfo = await $.ajax({
                url: "/deleteztpProfile",
                type: "POST",
                data: { profileid: profileid },
                success: function () {
                    // Profile deleted
                    removeSuccess = "1";
                    document.getElementById("liProgress").style.display = "block";
                    document.getElementById("progresstooltip").style.display = "none";
                    progressInfo.innerHTML = "ZTP profile deleted";
 
                },
                error: function () {
                    document.getElementById("liProgress").style.display = "block";
                    document.getElementById("progresstooltip").style.display = "none";
                    progressInfo.innerHTML = "Error deleting ZTP profile";
                }
            });
        }
    }
    if (removeSuccess == "1") {
    $(this).closest('tr').remove();
    }

});



});

function highlightprofileRow(e) {
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

function clearprofileRow(e) {
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

$(document).on("click", "#searchProfile", function () {
    document.getElementById("editProfile").style.display = "none";
    document.getElementById("addProfile").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    });

function changeVRF(searchVRF) {
    document.getElementById("editProfile").style.display = "none";
    document.getElementById("addProfile").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
 }


$(document).on("click", "#addztpProfile", function () {
    document.getElementById("addProfile").style.display = "block";
    document.getElementById("editProfile").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
});
