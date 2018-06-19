var new_pathology_data;

function init_step_4() {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.slice_analysis_id(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      loadDiagnosticTable(data);
    })
    .fail(function () {
      console.log("Fail")
    })


  $(document).on('click', '#new_pathology_link', function (e) {
    var slice_id = $(this).data("slice-id");
    var url = Urls.organs_by_slice(slice_id);

    $(this).closest('tr').addClass("select");

    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        new_pathology_data = data.organs;
        $("#slice_id").val(slice_id);

        $("#organ_select").children('option:not(:first)').remove();

        $.each(data.organs, function (i, item) {
          var array_index = i;
          $("#organ_select").append(
            $('<option />').val(item.id).text(item.name).attr('data-organ-index', array_index)
          );
        });

        $("#new_pathology").modal("show");
      })
      .fail(function () {
        console.log("Fail")
      })
  });

  $(document).on('show.bs.modal', '#new_pathology', function () {
    initializeSelect2NewPathologyModal();
  });

  $(document).on('hidden.bs.modal', '#new_pathology', function () {
    var modal_closed = true;

    $("#pathology_table .select").removeClass("select");
    clearSelectNewPathologyModal(modal_closed);
  });

  $(document).on('change', '#organ_select', function (e) {
    var organ_index = $('#organ_select').find(':selected').data('organ-index')
    var modal_closed = false;

    clearSelectNewPathologyModal(modal_closed)
    loadSelectNewPathologyModal(organ_index);
  });

  $(document).on('click', '#new_pathology_save', function (e) {
    var url = Urls.report();
    var form_data = $("#new_pathology :input").serialize();
    var pathology = $('#pathology_select').find(':selected').text();
    $.ajax({
      type: "POST",
      url: url,
      data: form_data,
    })
      .done(function (data) {
        if (data.ok) {
          var pathology_cell = $("#pathology_table .select #pathology");
          $(pathology_cell).append(pathology + " ");

          $('#new_pathology').modal('hide');
        } else {

        }
      })
      .fail(function () {
        console.log("Fail")
      })
  });

  $(document).on('click', '#show_pathology_link', function (e) {
    var slice_id = $(this).data("slice-id");
    var url = Urls.report_by_slice(slice_id);

    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        loadPathologyTable(data)

        $("#show_pathologies").modal("show");
      })
      .fail(function () {
        console.log("Fail")
      })
  });

  $(document).on('click', '#remove_pathology', function (e) {
    var report_id = $(this).data("report-id");
    var url = Urls.report(report_id);

    $.ajax({
      type: "DELETE",
      url: url,
    })
      .done(function (data) {
        if (data.ok) {
          $("#show_pathologies").modal("hide");
        }
      })
      .fail(function () {
        console.log("Fail")
      })
  });

}

function initializeSelect2NewPathologyModal() {
  $('#organ_select').select2({
    placeholder: "Porfavor primero seleccione un organo"
  });

  $('#organ_location_select').select2({
    placeholder: "Porfavor seleccione una localización"
  });

  $('#pathology_select').select2({
    placeholder: "Porfavor seleccione un hallazgo"
  });

  $('#diagnostic_select').select2({
    placeholder: "Porfavor seleccione un diagnóstico"
  });

  $('#diagnostic_distribution_select').select2({
    placeholder: "Porfavor seleccione una distribución de diagnóstico"
  });

  $('#diagnostic_intensity_select').select2({
    placeholder: "Porfavor seleccione una intensidad de diagnóstico"
  });
}

function clearSelectNewPathologyModal(modal_closed) {
  if (modal_closed) {
    $("#organ_select").children('option:not(:first)').remove();
  }

  $("#organ_location_select").children('option:not(:first)').remove();
  $("#pathology_select").children('option:not(:first)').remove();
  $("#diagnostic_select").children('option:not(:first)').remove();
  $("#diagnostic_distribution_select").children('option:not(:first)').remove();
  $("#diagnostic_intensity_select").children('option:not(:first)').remove();
}

function loadSelectNewPathologyModal(organ_index) {
  $.each(new_pathology_data[organ_index].organ_locations, function (i, item) {
    $("#organ_location_select").append(
      $('<option />').val(item.id).text(item.name)
    );
  });

  $.each(new_pathology_data[organ_index].pathologys, function (i, item) {
    $("#pathology_select").append(
      $('<option />').val(item.id).text(item.name)
    );
  });

  $.each(new_pathology_data[organ_index].diagnostics, function (i, item) {
    $("#diagnostic_select").append(
      $('<option />').val(item.id).text(item.name)
    );
  });

  $.each(new_pathology_data[organ_index].diagnostic_distributions, function (i, item) {
    $("#diagnostic_distribution_select").append(
      $('<option />').val(item.id).text(item.name)
    );
  });

  $.each(new_pathology_data[organ_index].diagnostic_intensity, function (i, item) {
    $("#diagnostic_intensity_select").append(
      $('<option />').val(item.id).text(item.name)
    );
  });
}

function loadDiagnosticTable(data) {
  if ($.fn.DataTable.isDataTable('#diagnostic_table')) {
    $('#diagnostic_table').DataTable().clear().destroy();
  }

  populateDiagnosticTable(data);

  $('#diagnostic_table').DataTable({
    ordering: false,
    paginate: false,
    autoWidth: false,
    columnDefs: [
      { "width": "10%", "targets": 3 }
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateDiagnosticTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.slice_id;
    row.slice_name = item.slice_name;
    row.organs = item.organs.join(', ');
    row.store_index = i;
    row.identification_cage = 'E-' + item.identification_cage;

    addDiagnosticRow(row)
  });
}

function addDiagnosticRow(data) {
  var blockStoreTemplate = document.getElementById("diagnostic_row").innerHTML;

  var templateFn = _.template(blockStoreTemplate);
  var templateHTML = templateFn(data);

  $("#diagnostic_table tbody").append(templateHTML)
}

function loadPathologyTable(data) {
  if ($.fn.DataTable.isDataTable('#pathology_table')) {
    $('#pathology_table').DataTable().clear().destroy();
  }

  populatePathologyTable(data);

  $('#pathology_table').DataTable({
    ordering: false,
    paginate: false,
    autoWidth: false,
    columnDefs: [
      { "width": "10%", "targets": 3 }
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populatePathologyTable(data) {
  $.each(data.reports, function (i, item) {
    var row = {};

    row.report_id = item.report_id;
    row.diagnostic = item.diagnostic;
    row.diagnostic_distribution = item.diagnostic_distribution
    row.diagnostic_intensity = item.diagnostic_intensity
    row.organ = item.organ
    row.organ_location = item.organ_location;
    row.pathology = item.pathology;

    addPathologyRow(row)
  });
}

function addPathologyRow(data) {
  var blockStoreTemplate = document.getElementById("pathology_row").innerHTML;

  var templateFn = _.template(blockStoreTemplate);
  var templateHTML = templateFn(data);

  $("#pathology_table tbody").append(templateHTML)
}
