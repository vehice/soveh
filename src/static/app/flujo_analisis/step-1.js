$(function () {
  init_step_1();
});

function init_step_1() {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    $('.showSummaryBtn').removeClass("hidden");
    fillSummary(data);
    loadStainTable(data)
  })
  .fail(function () {
    console.log("Fail")
  });

  // Events

  $(document).on('change', '#stain_table :checkbox', function (e) {
    if (e.target.checked) {
      $("[name='" + e.target.id + "']").val(moment().format());
    } else {
      $("[name='" + e.target.id + "']").val("");
    }
  });
}

$(document).on('click', '.start_stain_all', function (e) {
  $("input[type=checkbox][id^='stain[start_stain]']" ).trigger('click');
});

$(document).on('click', '.end_stain_all', function (e) {
  $("input[type=checkbox][id^='stain[end_stain]']" ).trigger('click');
});


function loadStainTable(data) {
  if ($.fn.DataTable.isDataTable('#stain_table')) {
    $('#stain_table').DataTable().clear().destroy();
  }

  populateStainTable(data);

  var elems = Array.prototype.slice.call(document.querySelectorAll('.switchery'));

  elems.forEach(function (html) {
    new Switchery(html);
  });

  $('#stain_table').DataTable({
    ordering: false,
    paginate: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateStainTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.id;
    row.sample_index = item.sample.index;
    row.slice_name = item.slice_name;
    row.stain_index = i;
    row.sample_identification = item.sample.identification.cage + '-' + item.sample.identification.group;
    // row.identification_cage = 'E-' + item.identification_cage;
    row.start_stain = item.start_stain;
    row.end_stain = item.end_stain;

    addStainRow(row)

    if (item.start_stain != null && item.end_stain != null) {
      $("[data-index='" + i + "']").find(".switchery").trigger("click");
    }
  });
}

function addStainRow(data) {
  var blockStainTemplate = document.getElementById("stain_row").innerHTML;

  var templateFn = _.template(blockStainTemplate);
  var templateHTML = templateFn(data);

  $("#stain_table tbody").append(templateHTML)
}
