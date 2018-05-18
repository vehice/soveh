var data_step_2;

function init_step_2() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      data_step_2 = data

      loadTable(data_step_2);
    })
    .fail(function () {
      console.log("Fail")
    })
}

$(document).on('change', '#no_cassette', function (e) {
  loadTable(data_step_2);
})

function loadTable(data) {
  var no_cassette = $('#no_cassette').val();

  if ($.fn.DataTable.isDataTable('#cassettes_table')) {
    // TODO: Fix efecto al destruir la tabla
    $('#cassettes_table').DataTable().clear().destroy();
  }

  populateTable(data, no_cassette);

  $('#cassettes_table').DataTable({
    ordering: false,
    paginate: false,
    columnDefs: [
      { "width": "50%", "targets": 2 }
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });

  $('[name*="cassette[organ]"]').select2();
}

function populateTable(data, no_cassette) {
  var organs = data.organs;

  $.each(data.identifications, function (i, item) {
    var no_fish = item.no_fish * no_cassette;

    var array_index = _.range(1, no_fish + 1);
    var id_muestra = 'C_' + data.entryform.id + '-' + 'E_' + item.cage + '-C_';

    $.each(array_index, function (i, item) {
      var row = {};
      var final_id_muestra = id_muestra + item;
      row.sample_id = final_id_muestra;
      row.cassette_id = item;
      row.cassette_organs = organs;
      row.cassette_index = i;

      addCasseteRow(row)
    });
  });
}

function addCasseteRow(data) {
  var cassetteRowTemplate = document.getElementById("cassette_row").innerHTML;

  var templateFn = _.template(cassetteRowTemplate);
  var templateHTML = templateFn(data);

  $("#cassettes_table tbody").append(templateHTML)
}
