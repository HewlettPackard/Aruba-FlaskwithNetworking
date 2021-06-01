// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).on("click", "#adddeviceAttribute", function () {
    document.getElementById("deviceattributeDiv").style.display = "block";
    document.getElementById("addoredit").innerHTML = "Add";
    document.getElementById("submitorchange").innerHTML = "<input type='submit' name='action' value='Submit device attribute' class='button' />";
});


$(document).on("click", ".editdeviceAttribute", async function () {
    document.getElementById("deviceattributeDiv").style.display = "block";
    document.getElementById("addoredit").innerHTML = "Edit";
    document.getElementById("submitorchange").innerHTML = "<input type='submit' name='action' value='Submit changes' class='button' />";
    document.getElementById("attributeid").value = $(this).attr('data-attributeid');
    response = await $.ajax({
        url: "/editdeviceattribute",
        type: "POST",
        data: { id: $(this).attr('data-attributeid')},
        success: function (response) {
            response = JSON.parse(response);
            $("#name").val(response['name']);
            $("#attributetype").val(response['type']).change();
            $("#attributeList").val(response['attributelist'].toString().replace(/['"]+/g, '').slice(1, -1));
        },
        error: function () {
            console.log("Error obtaining device attribute information");
        }
    });
});




function showattributeType() {
    $('.attributetype').html("<font class='font12pxwhite'>" + $("#attributetype option:selected").text() + "</font>");
    if ($("#attributetype").val() == "value") {
        document.getElementById("attributelist").style.display = "none";
    }
    else if ($("#attributetype").val() == "list") {
        document.getElementById("attributelist").style.display = "inline";
    }

    else if ($("#attributetype").val() == "" || $("#attributetype").val() == "boolean"  ) {
        document.getElementById("attributelist").style.display = "none";
    }

}