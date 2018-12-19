function init_step_2() {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    loadScanTable(data);
    $('.showSummaryBtn').removeClass("hidden");
    fillSummary(data);
  })
  .fail(function () {
    console.log("Fail")
  });

  // Events

  $(document).on('change', '#scan_table :checkbox', function (e) {
    if (e.target.checked) {
      $("[name='" + e.target.id + "']").val(moment().format());
    } else {
      $("[name='" + e.target.id + "']").val("");
    }
  });
}

$(document).on('click', '.start_scan_all', function (e) {
  $("input[type=checkbox][id^='scan[start_scan]']" ).trigger('click');
});

$(document).on('click', '.end_scan_all', function (e) {
  $("input[type=checkbox][id^='scan[end_scan]']" ).trigger('click');
});

$(document).on('click', '.showSummary', function (e) {
  // console.log("ASDASDAS");
  swal({
    title: 'Resúmen del caso',
    type: 'info',
    html:
      'You can use <b>bold text</b>, ' +
      '<a href="//github.com">links</a> ' +
      'and other HTML tags',
    showCloseButton: true,
    showCancelButton: false,
    focusConfirm: false,
  });
});

function loadScanTable(data) {
  if ($.fn.DataTable.isDataTable('#scan_table')) {
    $('#scan_table').DataTable().clear().destroy();
  }

  populateScanTable(data);

  var elems = Array.prototype.slice.call(document.querySelectorAll('.switchery'));

  elems.forEach(function (html) {
    new Switchery(html);
  });

  $('#scan_table').DataTable({
    ordering: false,
    paginate: false,
    columnDefs: [
      { className: "dt-head-center", targets: [0] },
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateScanTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};
    row.slice_id = item.id;
    row.sample_index = item.sample.index;
    row.slice_name = item.slice_name;
    row.scan_index = i;
    row.sample_identification = item.sample.identification.cage + '-' + item.sample.identification.group;
    row.start_scan = item.start_scan;
    row.end_scan = item.end_scan;
    row.slice_store = item.slice_store;

    addScanRow(row)

    if (item.start_scan != null && item.end_scan != null) {
      $("[data-index='" + i + "']").find(".switchery").trigger("click");
    }
  });
}

function addScanRow(data) {
  var blockScanTemplate = document.getElementById("scan_row").innerHTML;

  var templateFn = _.template(blockScanTemplate);
  var templateHTML = templateFn(data);

  $("#scan_table tbody").append(templateHTML)
}
