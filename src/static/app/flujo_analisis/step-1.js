$(function () {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      loadSliceTable(data)
    })
    .fail(function () {
      console.log("Fail")
    })

  // Events

  $(document).on('change', '#slice_table :checkbox', function (e) {
    if (e.target.checked) {
      $("[name='" + e.target.id + "']").val(moment().format());
    } else {
      $("[name='" + e.target.id + "']").val("");
    }
  });
});


function loadSliceTable(data) {
  if ($.fn.DataTable.isDataTable('#slice_table')) {
    // TODO: Fix efecto al destruir la tabla
    $('#slice_table').DataTable().clear().destroy();
  }

  populateSliceTable(data);

  var elems = Array.prototype.slice.call(document.querySelectorAll('.switchery'));

  elems.forEach(function (html) {
    new Switchery(html);
  });

  $('[data-toggle="popover"]').popover();

  $('#slice_table').DataTable({
    ordering: false,
    paginate: false,
    scrollX: true,
    columnDefs: [
      { "width": "20%", "targets": 0 },
      { "width": "20%", "targets": 1 },
      { "width": "40%", "targets": 4 },
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateSliceTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.slice_id;
    row.slice_name = item.slice_name;
    row.slice_index = i;
    row.identification_cage = 'E-' + item.identification_cage;

    addBlockRow(row)
  });
}

function addBlockRow(data) {
  var blockRowTemplate = document.getElementById("slice_row").innerHTML;

  var templateFn = _.template(blockRowTemplate);
  var templateHTML = templateFn(data);

  $("#slice_table tbody").append(templateHTML)
}
