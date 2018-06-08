var data_step_3;

function init_step_3() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.cassette_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      data_step_3 = data

      console.log(data_step_3);

      loadBlockTable(data_step_3);
    })
    .fail(function () {
      console.log("Fail")
    })
}

$(document).on('change', '#block_table :checkbox', function (e) {
  if (e.target.checked) {
    $("[name='" + e.target.id + "']").val(moment().format());
  } else {
    $("[name='" + e.target.id + "']").val("");
  }
})

function loadBlockTable(data) {
  if ($.fn.DataTable.isDataTable('#block_table')) {
    // TODO: Fix efecto al destruir la tabla
    $('#block_table').DataTable().clear().destroy();
  }

  populateBlockTable(data);

  var elems = Array.prototype.slice.call(document.querySelectorAll('.switchery'));

  elems.forEach(function (html) {
    new Switchery(html);
  });

  $('[data-toggle="popover"]').popover();

  $('#block_table').DataTable({
    ordering: false,
    paginate: false,
    scrollX: true,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateBlockTable(data) {
  var analyses = data.analyses;

  $.each(data.cassettes, function (i, item) {

    var row = {};
    var slice_index = i + 1;

    row.sample_id = item.sample_id;
    row.cassette_name = item.cassette_name
    row.cassette_pk = item.id
    row.organs = item.organs.join(", ")
    row.no_slice = item.no_slice
    row.block_index = i;
    row.analyses = analyses;
    row.slice_info = "<ol>";

    var cage = row.sample_id.split("-")[1].split("_")[1]

    $.each(data.exams, function (i, item) {
      row.slice_info += "<li><p><strong>Cassette:</strong> " + row.cassette_name + " /<strong> Jaula: </strong>" + cage + " /<strong> Tinci&oacute;n: </strong>" + item.stain + "</p></li>"
    })

    row.slice_info += "</ol>";

    addBlockRow(row)
  });
}

function addBlockRow(data) {
  var blockRowTemplate = document.getElementById("block_dyeing_row").innerHTML;

  var templateFn = _.template(blockRowTemplate);
  var templateHTML = templateFn(data);

  $("#block_table tbody").append(templateHTML)
}
