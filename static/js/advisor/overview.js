(function ($) {
    "use strict";

    $(document).ready(function () {
        var $accounts = $('#accounts'),
            $search = $("#search"),
            $clearSearch = $("#btn-clear-search"),
            table = $accounts.DataTable({
            paging: false,
            info: false,
            order: [[1, "asc"]],
            columns: [
                {
                    searchable: true,
                    orderable: false
                },
                {
                    searchable: true,
                    orderable: true
                },
                {
                    searchable: true,
                    orderable: true
                },
                {
                    searchable: true,
                    orderable: true
                }
            ]
        });
        $search.keyup(function (e) {
            table.search(this.value).draw();
            this.value.length ? $clearSearch.show() : $clearSearch.hide();
        });
        $clearSearch.hide().click(function () {
            $search.val('');
            table.search('').draw();
            $clearSearch.hide();
        });
        // hide lib's search box with disabling
        $(".dataTables_filter").hide();
    });
}(jQuery));
