function init_step_3() {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      $('.showSummaryBtn').removeClass("hidden");
      loadStoreTable(data);
      
    })
    .fail(function () {
      console.log("Fail")
    })
}

function loadStoreTable(data) {
  if ($.fn.DataTable.isDataTable('#store_table')) {
    $('#store_table').DataTable().clear().destroy();
  }

  populateStoreTable(data);

  $('#store_table').DataTable({
    ordering: false,
    paginate: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateStoreTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.id;
    row.slice_name = item.slice_name;
    row.store_index = i;
    row.box_id = item.box_id
    var samples_index_comm_sep = '';
    $.each(item.samples, function(j, sample){
      if (j == 0){
        samples_index_comm_sep += sample.index;
      } else {
        samples_index_comm_sep += ', '+sample.index;
      }
    });
    row.samples = samples_index_comm_sep;
    addStoreRow(row)
  });
}

function addStoreRow(data) {
  var blockStoreTemplate = document.getElementById("store_row").innerHTML;

  var templateFn = _.template(blockStoreTemplate);
  var templateHTML = templateFn(data);

  $("#store_table tbody").append(templateHTML)
}
