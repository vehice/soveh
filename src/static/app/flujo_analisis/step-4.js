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

  $(document).on('click', '#show_pathology_link', function (e) {
    var slice_id = $(this).data("slice-id");
    var url = Urls.report_by_slice(slice_id);

    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        $('.showSummaryBtn').removeClass("hidden");
        // fillSummary(data);
        loadPathologyTable(data);

        $("#show_pathologies").modal("show");
      })
      .fail(function () {
        console.log("Fail")
      })
  });

  $(document).on('click', '#remove_pathology', function (e) {
    var report_id = $(this).data("report-id");
    var url = Urls.report_by_id(report_id);

    lockScreen(1);
    $.ajax({
      type: "DELETE",
      url: url,
    })
      .done(function (data) {
        if (data.ok) {
          $("#show_pathologies").modal("hide");
          toastr.success('', 'Hallazgo eliminado exitosamente.');
          setTimeout(function() {
            location.reload();
          }, 3000);
        } else {
          toastr.error('', 'No ha sido posible eliminar el hallazgo. Favor intente nuevamente.');
        }
      })
      .fail(function () {
        console.log("Fail")
      })
  });

  $(document).on('click', '#load_img', function(e) {
    var report_id = $(this).data('id');
    var url = Urls.images(report_id);
    var temp = "";
    temp += '<div class="modal fade" id="load_images_modal" role="dialog">';
    temp += '<div class="modal-dialog" role="document"><div class="modal-content"> <div class="modal-header"> <h3 class="modal-title"> Cargador de imágen </h3></div>';
    temp += '<div class="modal-body">';
    temp += '<div class="col-md-12"><form id="mydropzone2" action="'+url+'" class="dropzone needsclick">';
    temp += '<div class="dz-message" data-dz-message>';
    temp += '<center><span><h3>Arrastra o selecciona la imágen que deseas cargar</h3></span></center>';
    temp += '</div>';    
    temp += '</form></div><div class="col-md-12"><p><h5><strong>Observaciónes</strong></h5></p>';
    temp += '<div class="col-md-12"><textarea rows="3" class="form-control textarea-comments"></textarea></div>';
    temp += '</div></div>';
    temp += '<div class="modal-footer">';
    temp += '<input type="reset" class="btn btn-secondary" data-dismiss="modal" value="Salir">';
    temp += '<input type="button" class="btn btn-primary submit-file" value="Cargar Imágen""></div></div></div>';

    $('#uploader').html(temp);
    $("#mydropzone2").dropzone({
      autoProcessQueue: false,
      acceptedFiles: ".png, .jpeg, .jpg",
      init: function() {
        var submitButton = document.querySelector(".submit-file")
        myDropzone = this;
        submitButton.addEventListener("click", function() {
          myDropzone.processQueue();
        });
        this.on('sending', function(file, xhr, formData){
          lockScreen(1);
          var value = $('.textarea-comments').val();
          formData.append('comments', value);
        });

        this.on("success", function(file, responseText) {
          if (responseText.ok) {
            toastr.success('', 'Imágen cargada exitosamente.');
            $('.textarea-comments').val("");
            this.removeFile(file);
            $('#image-box-'+report_id).append('<a target="_blank" href="'+responseText.img_url+'">'+responseText.img_name+'</a>');
          } else {
            toastr.error('', 'No ha sido posible cargar la imágen. Intente nuevamente.');
          }
          lockScreen(0);
        });

        this.on("error", function(file, response) {
          this.removeFile(file);
          bootbox.hideAll();
          toastr.error('', 'No ha sido posible cargar la imágen. Intente nuevamente.');
          lockScreen(0);
        });

        this.on("addedfile", function() {
          if (this.files[1]!=null){
            this.removeFile(this.files[0]);
          }
        });
      },
    });
    $('#load_images_modal').modal('show');
  });

}

function saveReport(id) {
  var url = Urls.report();
  var form_id = id;
  var form_data = $("#new_pathology :input").serialize();
  var pathology = $('#pathology_select').find(':selected').text();
  lockScreen(1);
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
      toastr.success('', 'Hallazgo ingresado exitosamente.');
      setTimeout(function() {
        window.location.href = "/workflow/"+form_id+"/step_4";
      }, 1500);
    } else {
      toastr.error('', 'Error al ingresar hallazgo. Favor intentar nuevamente!');
      setTimeout(function() {
        window.location.href = "/workflow/"+form_id+"/step_4";
      }, 1500);
    }
  })
  .fail(function () {
    toastr.error('', 'Error al ingresar hallazgo. Favor intentar nuevamente!');
  })
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
    searching: false,
    columnDefs: [
      { "width": "7%", "targets": 3 }
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateDiagnosticTable(data) {
  $.each(data.slices, function (i, item) {
    var row = {};

    row.slice_id = item.id;
    row.slice_name = item.slice_name;
    row.sample_index = item.sample.index;
    
    $.each(data.samples, function (j, item2){
      if ( item2.id == item.sample.id ) {
        row.organs = item2.sample_exams_set[item.analysis_exam].organ_id;
        return false;
      }
    });
    // row.organs = item.organs;
    row.store_index = i;
    row.sample_identification = item.sample.identification.cage + '-' + item.sample.identification.group;
    row.paths = item.paths_count;

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
    row.images = item.images;

    addPathologyRow(row)
  });
}

function addPathologyRow(data) {
  var blockStoreTemplate = document.getElementById("pathology_row").innerHTML;

  var templateFn = _.template(blockStoreTemplate);
  var templateHTML = templateFn(data);

  $("#pathology_table tbody").append(templateHTML)
}
