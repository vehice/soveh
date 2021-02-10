function init_step_1() {
  // var url = Urls.entryform();
  // $.ajax({
  //   type: "GET",
  //   url: url,
  // })
  //   .done(function (data) {
  //     initialData(data);
  //     organs = data.organs;
  //     initialConf();
  //     loadData();

  //   })
  //   .fail(function () {
  //     console.log("Fail")
  //   });

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
      $('#unitTTT').append(rows);
    }, 2000)
    return table_template;
    // '<tr>' +
    // '<td>Full name:</td>' +
    // '<td>' + d.name + '</td>' +
    // '</tr>' +
    // '<tr>' +
    // '<td>Extension number:</td>' +
    // '<td>' + d.extn + '</td>' +
    // '</tr>' +
    // '<tr>' +
    // '<td>Extra info:</td>' +
    // '<td>And any further details here (images etc)...</td>' +
    // '</tr>' +
    // '</table>'
    ;
  }

  var table = $('#identifications').DataTable({
    "columnDefs": [
      {
        "targets": [0],
        "className": 'details-control',
        "orderable": false,
        "data": null,
        "defaultContent": ''
      },
    ],
    "info": false,
    "paging": false,
    "searching": false,
    "order": [[1, 'asc']]
  });

  // Add event listener for opening and closing details
  $('#identifications tbody').on('click', 'td.details-control', function () {
    var tr = $(this).closest('tr');
    var row = table.row(tr);

    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();
      tr.removeClass('shown');
    }
    else {
      // Open this row
      row.child(format(row.data())).show();
      tr.addClass('shown');
    }
  });

  $('#addIdent').on('click', function () {
    let index = table.rows()[0].length;
    table.row.add({
      "1": '<input name="eee" class="form-control1">',
      "2": '<input name="eee" class="form-control1">',
      "3": '<input name="eee" class="form-control1">',
      "4": '<input name="eee" class="form-control1">',
      "5": '<input name="eee" class="form-control1">',
      "6": '<input name="eee" class="form-control1">',
      "7": '<input name="eee" class="form-control1">',
      "8": '<input name="eee" class="form-control1">',
      "9": '<input name="eee" class="form-control1" type="number">',
      "10": `<button class="btn btn-danger btn-sm deleteIdent" type="button" data-index="${index}"><i class="fa fa-trash fa-fx"></i></button>`
    }).draw()
  })
  $(document).on('click', '.deleteIdent', function () {
    var row = table.row($(this).parents('tr'));
    row.remove().draw();
  })
}

function addUnitTemplate(data) {
  var unitTemplate = document.getElementById("unit_template").innerHTML;

  var templateFn = _.template(unitTemplate);
  var templateHTML = templateFn(data);
  return templateHTML;
}