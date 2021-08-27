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
                showmessageBar("Error finding ZTP Template information");
            }
        });
        templateInfo = JSON.parse(templateInfo);
        document.getElementById('templateid').value = templateInfo['id'];
        document.getElementById('editName').value = templateInfo['name'];
        document.getElementById('editDescription').value = templateInfo['description'];
        $('#editTemplatecontent').val(templateInfo['template']);
    });
});


$(document).on("click", "#addztpTemplate", function () {
    document.getElementById("addTemplate").style.display = "block";
    document.getElementById("editTemplate").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
});
