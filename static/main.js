// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

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
    document.getElementById('userInfo').innerHTML = "<a href='/login' class='nohover'><img src='/static/images/logout.png' width='20' height='20' title='Logout " + value[1] + " ' />";
}


function clearRow(e) {
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


function highlightRow(e) {
    console.log("Highlight");
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
