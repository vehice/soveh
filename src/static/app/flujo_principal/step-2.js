function init_step_2() {
  var entryform_id = $('#entryform_id').val();

  var table = $('#identifications').DataTable({
    "columnDefs": [
      {
        "targets": 0,
        "className": 'details-control',
        "orderable": false,
        "data": null,
        "render": function (data, type, row, meta) {
          return `<i class="fa fa-chevron-right fa-fx" ></i>`;
        }
      },
      {
        "targets": 1, "orderable": false, "data": "cage",
        "render": function (data, type, row, meta) {
          return `<input name="" class="form-control-table" value="${data}" >`;
        }
      },
      {
        "targets": 2, "orderable": false, "data": "group",
        "render": function (data, type, row, meta) {
          return `<input name="" class="form-control-table" value="${data}" >`;
        }
      },
      {
        "targets": 3, "orderable": false, "data": "group",
        "render": function (data, type, row, meta) {
          return `<input name="" class="form-control-table" value="${data}" >`;
        }
      },
      {
        "targets": 4, "orderable": false, "data": "weight",
        "render": function (data, type, row, meta) {
          return `<input name="" class="form-control-table" type="number" step="0.1" min="0" value="${data}" >`;
        }
      },
      {
        "targets": 5, "orderable": false, "data": "extra_features_detail",
        "render": function (data, type, row, meta) {
          return `<textarea name="" class="form-control-table" rows="3" > ${data} </textarea>`;
        }
      },
      {
        "targets": 6, "orderable": false, "data": "is_optimum",
        "render": function (data, type, row, meta) {
          return `
          <select name="" class="form-control-table">
            <option value="1"> Sí </option>
            <option value="0" ${(data != null && !data) ? 'selected' : ''}> No </option>
          </select>
          `;
        }
      },
      {
        "targets": 7, "orderable": false, "data": "observation",
        "render": function (data, type, row, meta) {
          return `<textarea name="" class="form-control-table" rows="3"> ${data} </textarea>`;
        }
      },
      {
        "targets": 8, "orderable": false, "data": "no_container",
        "render": function (data, type, row, meta) {
          return `<input name="" class="form-control-table amount" type="number" value="${data}" min="${data}">`;
        }
      },
      {
        "targets": 9, "orderable": false, "data": null,
        "render": function (data, type, row, meta) {
          return `<button class="btn btn-danger btn-sm deleteIdent" type="button" data-ident="${row.id}"><i class="fa fa-trash fa-fx"></i></button>`
        }
      },
    ],
    "info": false,
    "paging": false,
    "searching": false,
    "order": [[1, 'asc']]
  });

  var url = Urls.list_identification(entryform_id);
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      // initialData(data);
      // organs = data.organs;
      // initialConf();
      // loadData();
      data.data.forEach(element => {
        addRow(element);
      });
    })
    .fail(function () {
      console.log("Fail")
    });

  function format(d) {
    // color: #ffffff; background-color: #63d0ba; border: none
    let table_id = "unitTTT" // hay que linkearlo a la funcion ajax
    let table_template = `
    <table class='table w-100 table-unit'>
    <thead> 
    <th>#</th> 
    <th>Tipo</th> 
    <th>Organos</th> 
    <th>Eliminar</th> 
    </thead>
    <tbody id="${table_id}">
    </tbody>
    </table>
    `
    let table = $(table_template);
    setTimeout(function () { //sustituir por una funcion ajax
      let rows = addUnitTemplate({})
      $(`#${table_id}`).append(rows);
    }, 2000)
    return table_template;
  }

  function addRow(data) {
    let index = table.rows()[0].length;
    table.row.add(data

    ).draw()
  }

  // Add event listener for opening and closing details
  $('#identifications tbody').on('click', 'td.details-control', function () {
    var tr = $(this).closest('tr');
    var icon = $(this, 'i');
    var row = table.row(tr);

    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();
      icon.removeClass('fa-chevron-down');
      icon.addClass('fa-chevron-right');
      tr.removeClass('shown');
    }
    else {
      // Open this row
      row.child(format(row.data())).show();
      icon.removeClass('fa-chevron-right');
      icon.addClass('fa-chevron-down');
      tr.addClass('shown');
    }
  });

  $('#addIdent').on('click', function () {
    var url = Urls.new_identification(entryform_id);
    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        addRow(data.obj);
      })
      .fail(function () {
        console.log("Fail")
      });
  });

  $(document).on('click', '.deleteIdent', function () {

    var row = table.row($(this).parents('tr'));
    var url = Urls.remove_identification($(this).data('ident'));
    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        row.remove().draw();
      })
      .fail(function () {
        console.log("Fail")
      });
  });

  $(document).on('blur', '.form-control-table.amount', function () {
    this.min = this.value;
  });
}

function addUnitTemplate(data) {
  var unitTemplate = document.getElementById("unit_template").innerHTML;

  var templateFn = _.template(unitTemplate);
  var templateHTML = templateFn(data);
  return templateHTML;
}