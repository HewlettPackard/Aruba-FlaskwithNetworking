// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.


$(document).on('mouseenter', '.showtitleTooltip', function (event) {
    if ((event.pageX + 45) > self.innerWidth) {
        var left = event.pageX - 45 - $(this).attr('data-title').length;
    }
    else {
        var left = event.pageX - 30;
    }
    var top = event.pageY + 10;
    $("#showdaTooltip").css({
        position: 'absolute',
        zIndex: 20,
        left: left,
        top: top,
        paddingLeft: 5,
        paddingTop: 5,
        paddingRight: 5,
        paddingBottom: 5,
        backgroundColor: 'white',
        width: 70,
        "text-align": "center",
    });
    // Construct the innerHTML
    if ($(this).attr('data-title') != "") {
        $('#showdaTooltip').empty().append($(this).attr('data-title'));
        $('#showdaTooltip').show();
    }
});

$(document).on('mouseleave', '.showtitleTooltip', function (event) {
    $('#showdaTooltip').empty();
    $('#showdaTooltip').hide();
});



function setHidden(buttonValue)
{
    var element = document.getElementById("action");
    element.value = buttonValue;
    return true;
}

function infoBar(info) {
    document.getElementById(infoBar).value = info;
}

function updateCookie(authOK, idle_timeout) {
    document.cookie = "username=" + authOK['username'] + ";max-age=" + idle_timeout;
    document.cookie = "token=" + authOK['token'] + ";max-age=" + idle_timeout;
}

function clearCookies() {
    document.cookie = "username=;max-age=" + -1;
    document.cookie = "token=;max-age=" + -1;
}

function getCookie(name) {
    var re = new RegExp(name + "=([^;]+)");
    var value = re.exec(document.cookie);
    document.getElementById('userInfo').innerHTML = "<a href='/login' class='transparent-button'><img src='/static/images/logout.svg' width='12' height='12' data-title='Logout " + value[1] + " ' class='showtitleTooltip'></a>";
}


function clearRow(e) {
    var tr = e.closest('tr');
    var table = e.closest('tbody');
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


function highlightRow(e) {
    var tr = e.closest('tr');
    var table = e.closest('tbody');
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



function checkPass() {
    //Store the password field objects into variables ...
    var password = document.getElementById('password');
    var confirm = document.getElementById('rpassword');
    //Store the Confirmation Message Object ...
    var message = document.getElementById('confirm-message');
    //Set the colors we will be using ...
    var good_color = "#66cc66";
    var bad_color = "#ff6666";
    if (password.value.length <= 7 || rpassword.value.length<=7) {
        $('#reset').attr('disabled', 'disabled');
    } else {
        $('#reset').attr('disabled', false);
    }
    //Compare the values in the password field and the confirmation field
    if (password.value == confirm.value) {
        //The passwords match. 
        //Set the color to the good color and inform
        //the user that they have entered the correct password 
        confirm.style.backgroundColor = good_color;
        message.style.color = good_color;
        message.innerHTML = 'Passwords match';
    } else {
        //The passwords do not match. Set the color to red, notify the user and disable the submit button
        confirm.style.backgroundColor = bad_color;
        message.style.color = bad_color;
        message.innerHTML = 'Passwords Do Not Match!';
    }
}  


function showmessageBar(message) {
    document.getElementById("liProgress").style.display = "block";
    $('#liProgress').css({
        'position': 'relative',
        'width': '350px',
        'height': '16px',
        'line-height': '16px',
        'background-color': '#4CAF50',
        'text-align': 'center',
        'vertical-align': 'middle',
        'color': 'white',
        'right': '0',
        'left': '0',
        'top': '0px',
        'z-index': '101',
        'text-decoration': 'none',
        'pointer-events' : 'none'
    });
    $('#liProgress').empty().append(message);
}