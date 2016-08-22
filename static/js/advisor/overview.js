(function ($) {
    "use strict";

    $(document).ready(function () {
        var $accounts = $('#accounts'),
            table = $accounts.DataTable({
            paging: false,
            info: false,
            order: [[2, "asc"]],
            columns: [
                {
                    searchable: true,
                    orderable: false
                },
                {
                    searchable: false,
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
        $accounts.find("tbody>tr").each(function () {
            var url = this.dataset.url;
            $(this).click(function () {
                window.location = url;
            }).css("cursor", "pointer");
        });
        $("#search").keyup(function (e) {
            console.log(this.value);
            table.search(this.value).draw();
        });
        // hide lib's search box with disabling
        $(".dataTables_filter").hide();
    });
}(jQuery));
