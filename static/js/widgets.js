betasmartz.widgets = {
    searchTable: function (table, searchField, options) {
        function getColumns() {
            var columnNumber = $table.find(">thead>tr>th").length,
                columns = [];
            for (var i = 0; i < columnNumber; i++) {
                columns.push({
                    orderable: options.noSort.indexOf(i) === -1,
                    searchable: options.noSearch.indexOf(i) === -1
                });
            }
            return columns;
        }

        options = options || {};
        options = {
            noSort: options.noSort || [],  // [2]
            noSearch: options.noSearch || [],  // [2,3]
            defOrder: options.defOrder || undefined, // [[1, "asc"]]
        };
        var $table = $(table),
            $searchField = $(searchField),
            $clearSearch = $(".btn-clear-search", $searchField),
            dataTable, params = {
                paging: false,
                info: false,
                columns: getColumns()
            };
        if (options.defOrder !== undefined) {
            params.order = options.defOrder;
        }
        dataTable = $table.DataTable(params);

        if (!$clearSearch.length) {
            $clearSearch = $('<span class="glyphicon glyphicon-remove-sign ' +
                'form-control-feedback form-control-clear btn-clear-search" ' +
                'style="cursor: pointer; pointer-events: all">');
            $clearSearch.appendTo($searchField.parent());
        }
        $searchField.keyup(function (e) {
            dataTable.search(this.value).draw();
            this.value.length ? $clearSearch.show() : $clearSearch.hide();
        });
        $clearSearch.hide().click(function () {
            $searchField.val('');
            dataTable.search('').draw();
            $clearSearch.hide();
        });
        // hide lib's search box with disabling
        $(".dataTables_filter").hide();
    }
};
