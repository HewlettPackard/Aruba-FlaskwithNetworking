// (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {
    $('.field input').keyup(function () {
        var fieldisEmpty = false;
        $('.field input').keyup(function () {
            $('.field input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });        
            if (fieldisEmpty) {
                $('.actions input').attr('disabled', 'disabled');
            } else {
                $('.actions input').attr('disabled', false);
            }
        });
    });
});

$(document).on("click", "#addUser", function () {
    document.getElementById("adduser").style.display = "block";
    document.getElementById("edituser").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    $('#submituser').attr('disabled', false);
});

$(document).on("click", ".editUser", function () {
    userid = $(this).attr('data-userid');
    response = $.ajax({
        url: "/getuserinfo",
        type: "POST",
        data: { userid: userid},
        success: function (response) {
            response = JSON.parse(response);
            if (response['username'] == "admin") {
                $('#editusername').attr('disabled', 'disabled');
                $('#editrole').attr('disabled', 'disabled');
            }
            else {
                $('#editusername').attr('disabled', false);
                $('#editrole').attr('disabled', false);
            }
            console.log(response);
            document.getElementById('edituserid').value = response['id'];
            document.getElementById('editusername').value = response['username'];
            document.getElementById('editpassword').value = response['password'];
            document.getElementById('editemail').value = response['email'];
            document.getElementById('editorgrole').value = response['role'];
            document.getElementById('editrole').value = response['role'];
            $('#submitchanges').attr('disabled', false);
        }
    });
    document.getElementById("adduser").style.display = "none";
    document.getElementById("edituser").style.display = "block";
    document.getElementById("liProgress").style.display = "none";
});


function highlightuserRow(e) {
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

function clearuserRow(e) {
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