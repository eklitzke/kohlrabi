/* -*- indent-tabs-mode: nil; tab-width: 4; -*- */

var currentQuery = '';
var currentSort = '';

function updateHash () {
    var i;
    var parts = [];
    if (currentQuery) {
        parts.push('q=' + escape(currentQuery));
    }
    if (currentSort) {
        parts.push('s=' + escape(currentSort));
    }
    if (parts.length) {
        location.hash = parts.join('&')
    } else {
        location.hash = '';
    }
}

function info (msg) {
    if (typeof console === 'object' && typeof console.info === 'function') {
        console.info(msg);
    }
}

/* Read the currentQuery and currentSort out of location.hash */
$(document).ready(function () {
    var hash = (location.hash || '').replace(/^(#*)(.*)/, '$2');
    if (hash) {
        var i;
        var parts = hash.split('&');
        for (i = 0; i < parts.length; i++) {
            if (/[a-z]=.+/.test(parts[i])) {
                var k = parts[i][0];
                var v = unescape(parts[i].slice(2)) || '';
                if (k === 'q') {
                    currentQuery = v;
                } else if (k === 's') {
                    currentSort = v;
                }
            }
        }
    }

    var servlet_filter = $('#servlet_filter');
    servlet_filter.val(currentQuery);
    establishInputFilter(servlet_filter, 0);
});

$(document).ready(function () {
    var tbl = document.getElementById('kohlrabi_table');
    var thRow = tbl.getElementsByTagName('tr')[0];
    for (var i = 0; i < thRow.children.length; i++) {
        thRow.children[i].sortType = 'asc';
    }
    var r = tbl.getElementsByTagName('tr');
    var tdRows = [];
    for (var i = 1; i < r.length; i++) {
        tdRows.push(r[i]);
    }
    $('th').click(function (e) {
        var th = null;
        var sort;
        for (var i = 0; i < thRow.children.length; i++) {
            if (thRow.children[i] === this) {
                th = thRow.children[i];
                if ($(th).hasClass('number')) {
                    sort = 'numeric';
                }
                break;
            }
        }
        if (th) {
            /* this looks kind of weird, but the if check is hoisted outside of
             * the sort function for speed */
            if (sort == 'numeric') {
                tdRows.sort(function (a, b) {
                    var aVal = parseFloat(a.children[i].innerHTML);
                    var bVal = parseFloat(b.children[i].innerHTML);
                    return aVal - bVal;
                });
            } else {
                tdRows.sort(function (a, b) {
                    var aVal = a.children[i].innerHTML;
                    var bVal = b.children[i].innerHTML;
                    if (aVal == bVal)
                        return 0;
                    return aVal > bVal ? 1 : -1;
                });
            }
            if (th.sortType == 'desc') {
                th.sortType = 'asc';
            } else {
                tdRows.reverse();
                th.sortType = 'desc';
            }
            while (tbl.children.length > 1) {
                tbl.removeChild(tbl.lastChild);
            }
            for (var i = 0; i < tdRows.length; i++) {
                tbl.appendChild(tdRows[i]);
            }
        } else {
            alert('huh, which TH element is that?');
        }
    });

    var clickedRow = null;
    $('tr').click(function () {
        if (this.children[0].tagName == 'TH') {
            return;
        }
        if (clickedRow) {
            $(clickedRow).removeClass('clicked');
        }
        if (clickedRow !== this) {
            clickedRow = this;
            $(this).addClass('clicked');
        } else {
            clickedRow = null;
        }
    });
});

function establishInputFilter(input, offset, implicitCaret) {
    var filter = function (force) {
        var newVal = input.val();
        if (force || newVal !== currentQuery) {
            currentQuery = newVal;
            updateHash();

            var r;
            if (implicitCaret) {
                r = new RegExp('^' + newVal);
            } else {
                r = new RegExp(newVal);
            }
            $('tr').each(function () {
                var td = this.children[offset];
                if (td.tagName == 'TD') {
                    if (r.test(td.innerHTML)) {
                        this.style.display = 'table-row';
                    } else {
                        this.style.display = 'none';
                    }
                }
            });
        }
    };
    input.change(filter);
    input.keyup(filter);

    if (input.val()) {
        filter(true);
    }
}
