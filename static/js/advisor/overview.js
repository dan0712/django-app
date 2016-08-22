(function ($) {
    "use strict";

    $(document).ready(function () {
        var $accounts = $('#accounts'),
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
        $("#search").keyup(function (e) {
            table.search(this.value).draw();
        });
        // hide lib's search box with disabling
        $(".dataTables_filter").hide();
    });
}(jQuery));
