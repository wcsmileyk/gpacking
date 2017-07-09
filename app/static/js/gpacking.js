/**
 * Created by wes.smiley on 6/29/17.
 */


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

$("#toggleAdd").click(function(){
    $(this).toggleClass('glyphicon glyphicon-plus');
    $(this).toggleClass('glyphicon glyphicon-chevron-up');
});

jQuery(function() {
    $('h5 > a > span').click(function() {
        $(this).toggleClass('glyphicon glyphicon-menu-up');
        $(this).toggleClass('glyphicon glyphicon-menu-down');
    })
});

$(document).ready(get_cats);
$("#category").change(get_cats);
