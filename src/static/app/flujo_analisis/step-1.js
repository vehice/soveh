
function init_step_1(active = true) {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    $('.showSummaryBtn').removeClass("hidden");
    fillSummary(data);
    loadStainTable(data, active)
  })
  .fail(function () {
    console.log("Fail")
  });

  // Events

  $(document).on('change', '#stain_table :checkbox', function (e) {
    if (e.target.checked) {
      $("[name='" + e.target.id + "']").val(moment().format("DD/MM/YYYY HH:mm:ss"));
    } else {
      $("[name='" + e.target.id + "']").val("");
    }
  });
}

$(document).on('click', '.start_stain_all', function (e) {
  $("input[type=checkbox][id^='stain_start_stain']" ).trigger('click');
});

$(document).on('click', '.end_stain_all', function (e) {
  $("input[type=checkbox][id^='stain_end_stain']" ).trigger('click');
});

$(document).on('click', '#saveTimingStep1', function (e) {
  lockScreen(1);
  var form_data = $('#stain_table_wrapper :input').serialize();
  var url = Urls.save_stain_timing();
  $.ajax({
    type: "POST",
    url: url,
    data: form_data,
    async: false,
  })
  .done(function (data) {
    lockScreen(0);
    if (data.ok) {
      toastr.success('', 'Guardado.');
    } else {
      toastr.error('', 'No ha sido posible guardar. Contacte un administrador.');
    }    
    response = data;
  })
  .fail(function (data) {
    lockScreen(0);
    toastr.error('', 'No ha sido posible guardar. Contacte un administrador.');
  })
});

function loadStainTable(data, active = true) {
  if ($.fn.DataTable.isDataTable('#stain_table')) {
    $('#stain_table').DataTable().clear().destroy();
  }

  populateStainTable(data, active);

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

function populateStainTable(data, active = true) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.id;
    row.sample_index = item.sample.index;
    row.slice_name = item.slice_name;
    row.stain_index = i;
    row.sample_identification = item.sample.identification.cage + '-' + item.sample.identification.group;
    row.start_stain = item.start_stain;
    row.end_stain = item.end_stain;

    addStainRow(row)
    console.log(active)
    if (item.start_stain != null) {
      $("#stain_start_stain_" + i).trigger("click");
    }
    if(!active)
      $("#stain_start_stain_" + i).attr("disabled", true);
    if (item.end_stain != null) {
      $("#stain_end_stain_" + i).trigger("click");
    }
    if(!active)
      $("#stain_end_stain_" + i).attr("disabled", true);
    
  });
}

function addStainRow(data) {
  var blockStainTemplate = document.getElementById("stain_row").innerHTML;

  var templateFn = _.template(blockStainTemplate);
  var templateHTML = templateFn(data);

  $("#stain_table tbody").append(templateHTML)
}
