/**
 * Created by wes.smiley on 6/29/17.
 */

var toggle_add = function() {
    $('#toggleAdd').toggleClass('hidden');
};

var get_cats = function() {
    $.getJSON($SCRIPT_ROOT + '/create_opts', {
        a: $('#category').val()
    }, function (data) {
        $('#type option').remove();
        $.each(data.result, function( key, value ) {
            $('#type').append('<option value=' + value[0] + '>' + value[1] + '</option>')
        })
    });
    return false;
};

$(document).ready(get_cats);
$("#toggleAdd").click(toggle_add);
$("#category").change(get_cats);
