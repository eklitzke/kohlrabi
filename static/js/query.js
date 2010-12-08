$(document).ready(function () {
    var runLocation = window.location.pathname + '/run';
    var schemaLocation = window.location.pathname + '/schema';

    $('.bold').click(function (e) {
        e.preventDefault();
        var tableName = $(this).html();
        $.get(schemaLocation + '/' + tableName, {}, function (data) {
            $('#schema').html(data.sql);
        });
    });

    $('#query_button').click(function (e) {
        e.preventDefault();
        $.post(runLocation, {'query': $('#query_input').val()}, function (data) {
            var children = $('#query_results').children();
            for (var i = 0; i < children.length; i++) {
                $(children[i]).remove();
            }
            if (data.error) {
                var pre = document.createElement('pre');
                $(pre).html(data.error);
                $('#query_results').append(pre);
                return;
            }
            if (data.results) {
                var tbl = $('<table></table>');
                for (var i = 0; i < data.results.length; i++) {
                    var tr = $('<tr></tr>');
                    for (var j = 0; j < data.results[i].length; j++) {
                        var td = $('<td></td>');
                        td.text(data.results[i][j]);
                        tr.append(td);
                    }
                    tbl.append(tr);
                }
                $('#query_results').append(tbl);
            }
            if (data.previous_queries) {
                document.getElementById('query_log_container').style.display = 'block';
                var list = $('#query_log_list');
                while (list.children().length) {
                    $(list.children()[0]).remove();
                }
                for (var i = 0; i < data.previous_queries.length; i++) {
                    $('<li>' + data.previous_queries[i] + '</li>').appendTo(list);
                }
            }
        });
    });

});
