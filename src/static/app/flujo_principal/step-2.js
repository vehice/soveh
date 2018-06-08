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

      loadCassetteTable(data_step_2);
    })
    .fail(function () {
      console.log("Fail")
    })

  $('#datetime_processor_texture_at').datetimepicker({
    locale: 'es',
  });

  $('#datetime_processor_texture_at').on("dp.change", function (e) {
    if (e.date) {
      $("#processor_texture_at_submit").val(e.date.format());
    }
  });
}

$(document).on('change', '#no_cassette', function (e) {
  loadCassetteTable(data_step_2);
})

function loadCassetteTable(data) {
  var no_cassette = $('#no_cassette').val();

  if ($.fn.DataTable.isDataTable('#cassettes_table')) {
    // TODO: Fix efecto al destruir la tabla
    $('#cassettes_table').DataTable().clear().destroy();
  }

  populateCassetteTable(data, no_cassette);

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
  $('[name*="cassette[organ]"] > option').prop('selected', 'selected');
  $('[name*="cassette[organ]"]').trigger('change');
}

function populateCassetteTable(data, no_cassette) {
  var organs = data.organs;
  var cassette_index = 0;
  console.log(data);
  $.each(data.identifications, function (i, item) {

    var no_fish = item.no_fish * no_cassette;
    var identification_id = item.id;

    var array_index = _.range(1, no_fish + 1);
    var id_muestra = data.entryform.id + '-E_' + item.cage + '-G_' + item.group;

    $.each(array_index, function (i, item) {
      var row = {};

      row.identification_id = identification_id;
      row.sample_id = id_muestra;
      row.cassette_name = data.entryform.id + '-C' + item;
      row.cassette_organs = organs;
      row.cassette_index = cassette_index;

      cassette_index += 1;

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
