var patologos_list;
function init_step_3(active = true) {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.analysis_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      $('.showShareBtn').removeClass("hidden");
      $('.showLogBtn').removeClass("hidden");
      $('.showSummaryBtn').removeClass("hidden");
      $('.showAttachedFilesBtn').removeClass("hidden");
      $('.newAnalysisBtn').addClass("hidden");
      if(active){
        $('.newAnalysisBtn5').removeClass("hidden");
      }
      // fillSummary(data);
      saltar=true;
      patologos_list = data.patologos;
      fillNewAnalysis2(data);
      loadAnalysisData(data);
    })
    .fail(function () {
      console.log("Fail")
    })

    if ($('#exam_new_select5').hasClass("select2-hidden-accessible")) {
      $('#exam_new_select5').select2('destroy');
      $('#exam_new_select5').off('select2:select');
      $('#exam_new_select5').off('select2:unselect');
    }
  
    $('#exam_new_select5').select2();
    
    $('#exam_new_select5').on("select2:select", function (e) {
      var data = e.params.data;
      addNewExamToSamples5(data);
      addPatologoRow_5(data);
    });
  
    $('#exam_new_select5').on("select2:unselect", function (e) {
      var data = e.params.data;
      removeNewExamFromSamples5(data);
      removePatologoRow_5(data.id);
    });
  
    $('#exam_new_select5').on("select2:unselecting", function (e) {
      if (e.params.args.originalEvent) {
        e.params.args.originalEvent.stopPropagation();
      }
    });
}

function loadAnalysisData(data) {
  $("#analysis_group").empty();

  populateAnalysisData(data);
}

function populateAnalysisData(data) {
  $.each(data.analyses, function (i, item) {
    var row = {};

    row.form_id = item.form_id;
    row.id = item.id;
    row.exam_name = item.exam_name;
    row.exam_stain = item.exam_stain;
    row.no_slice = item.slices.length;
    row.current_step = item.current_step;
    row.total_step = item.total_step;
    row.percentage_step = item.percentage_step;
    row.current_step_tag = item.current_step_tag;
    row.form_closed = item.form_closed;
    row.cancelled = item.cancelled;
    row.form_reopened = item.form_reopened;
    // row.histologico = item.exam_type == 1;
    // saltar=saltar && item.exam_type == 2;
    row.service = item.service;
    row.service_name = item.service_name;
    row.patologo_name = item.patologo_name;
    addAnalysisElement(row)
  });
}

function addAnalysisElement(data) {
  var analysisElementTemplate = document.getElementById("analysis_element5").innerHTML;
  console.log(data)

  var templateFn = _.template(analysisElementTemplate);
  var templateHTML = templateFn(data);

  $("#analysis_group").append(templateHTML)
}

function fillNewAnalysis2(data) {
  organs_list = data.organs;
  loadNewSamples5(data.samples, data.organs);
  loadNewExams5(data.exams_set);
  $('#patologo_table_5 tbody').html('');
  $.each(data.entryform.analyses, function(i, item){
    $('#exam_new_select5 option[value="'+item.exam_id+'"]').prop('selected', true);
    addPatologoRow_5({text: item.exam__name, id: item.exam_id});
    $('#patologos-select_5-'+item.exam_id).val(item.patologo_id);
    $('#patologos-select_5-'+item.exam_id).trigger('change');
    $('#patologos-select_5-'+item.exam_id).attr('disabled', 'disabled');
  });
  $('#exam_new_select5').trigger('change');
}

function loadNewExams5(exams) {
  $("#exam_new_select5").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-service="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_new_select5').append($(html));
  });
}

function loadNewExams(exams) {
  $("#exam_new_select5").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-service="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_new_select5').append($(html));
  });
}

function addNewExamToSamples5(exam){
  $('#samples_new_table5 .samples_new_exams').each( function(i){
      var sampleId = $(this).data('index');
      $('.delete_new5-'+sampleId).hide();
      $('#sampleNro_new5-'+sampleId)[0].rowSpan = $('#sampleNro_new5-'+sampleId)[0].rowSpan + 1; 
      $('#sampleIden_new5-'+sampleId)[0].rowSpan = $('#sampleIden_new5-'+sampleId)[0].rowSpan + 1; 
      //show organs options
      var html = addNewOrgansOptions5(exam.text, $(exam.element).data('service'), sampleId, exam.id);
      $("#sample_new5-"+sampleId).after(html);
    // }
  }); 
  $('.organs_new_select5-'+ exam.id).select2();
  $('.organs_new_select5-'+ exam.id).on('select2:select', function(e){
    var values = e.params.data.id;
    $.each($('.organs_new_select5-'+ exam.id), function(i,v){
      var old_values = $(v).val();
      old_values.push(values);
      $(v).val(old_values);
      $(v).trigger('change');
    });
  });
}

function removeNewExamFromSamples5(exam){
  $('#samples_new_table5 .analis_new_row').each( function(i){
    if($(this).data('sampleid') == exam.id && !$(this).hasClass('old_row')){
      var sampleIndex = $(this).data('sampleindex');
      $('#sampleNro_new5-'+sampleIndex)[0].rowSpan = $('#sampleNro_new5-'+sampleIndex)[0].rowSpan - 1; 
      $('#sampleIden_new5-'+sampleIndex)[0].rowSpan = $('#sampleIden_new5-'+sampleIndex)[0].rowSpan - 1; 
      $(this).remove();
      if($('#sampleIden_new5-'+sampleIndex)[0].rowSpan == 1)
        $('.delete_new5-'+sampleIndex).show();
    }
  }); 
}


function loadNewSamples5(samples, organs){
  $("#samples_new_table5 tbody").html("");
  $.each(samples, function (i, v){
    addNewSampleRow5(v, organs);
    $.each(v.sample_exams_set, function(j,item){
      $('.delete_new5-'+v.id).hide();
      var html = addOldOrgansOptions5(item.exam_name, item.exam_type, v.id, item.exam_id, v.id+"-"+($('#sampleNro_new5-'+v.id)[0].rowSpan + 1));
      $('#sampleNro_new5-'+v.id)[0].rowSpan = $('#sampleNro_new5-'+v.id)[0].rowSpan + 1; 
      $('#sampleIden_new5-'+v.id)[0].rowSpan = $('#sampleIden_new5-'+v.id)[0].rowSpan + 1; 
      $("#sample_new5-"+v.id).after(html);
     
      $('.organs_new_select5-'+ item.exam_id).select2();
      $('.organs_new_select5-'+ item.exam_id).on('select2:select', function(e){
        var values = e.params.data.id;
        $.each($('.organs_new_select5-'+ item.exam_id), function(i,v){
          var old_values = $(v).val();
          old_values.push(values);
          $(v).val(old_values);
          $(v).trigger('change');
        });
      });
      var values = [];
      $.each(item.organ_id, function(j,w){
        values.push(w.id);
      });
      $('#select5-'+v.id+"-"+$('#sampleNro_new5-'+v.id)[0].rowSpan).val(values);
      $('#select5-'+v.id+"-"+$('#sampleNro_new5-'+v.id)[0].rowSpan).trigger('change');
    });
  });
 

  $('.samples_organs').select2();
}

function addNewSampleRow5 (sample, organs) {
  var sampleRowTemplate = document.getElementById("sample_new_row5").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'sample': sample, 'organs': organs});

  $("#samples_new_table5 tbody").append(templateHTML)
}

function addNewOrgansOptions5(analisis, analisis_type, sampleId, sampleIndex, optionId = null) {
  var sampleRowTemplate = document.getElementById("add_new_analisis5").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs_list, 'type': analisis_type, 'analisis': analisis, 'sampleId': sampleId, 'sampleIndex': sampleIndex, 'optionId': optionId});
  return templateHTML;
}

function addOldOrgansOptions5(analisis, analisis_type, sampleId, sampleIndex, optionId = null) {
  var sampleRowTemplate = document.getElementById("add_old_analisis5").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs_list, 'type': analisis_type, 'analisis': analisis, 'sampleId': sampleId, 'sampleIndex': sampleIndex, 'optionId': optionId});
  return templateHTML;
}

function deleteNewAnalisis5(sampleId, sampleIndex){
  $('#analisis_new5-'+sampleId+'-'+sampleIndex).remove();
  $('#sampleNro_new5-'+sampleId)[0].rowSpan = $('#sampleNro_new5-'+sampleId)[0].rowSpan - 1; 
  $('#sampleIden_new5-'+sampleId)[0].rowSpan = $('#sampleIden_new5-'+sampleId)[0].rowSpan - 1; 
  if($('#sampleIden_new5-'+sampleId)[0].rowSpan == 1)
    $('.delete_new5-'+sampleId).show();
  var exist = 0;
  $('#samples_new_table5 .analis_new_row').each( function(i){
    if($(this).data('sampleid') == sampleIndex){
      exist +=1;
    }
  }); 
  if(!exist){
    var old_values = $('#exam_new_select5').val();
    old_values.splice(old_values.indexOf(sampleIndex), 1);
    $('#exam_new_select5').val(old_values);
    $('#exam_new_select5').trigger('change');
  }
}

function submitNewAnalysis5(){
  var url = Urls.workflow();
  
  var disform = $("#modal_4").find(':disabled').prop('disabled', false);
  var form_data = $("#modal_4").find("select, input").serialize();
  disform.prop('disabled', true);

  var response;
  $.ajax({
    type: "POST",
    url: url,
    data: form_data + "&id_next_step=4&previous_step=0",
    async: false,
  })
  .done(function (data) {
    init_step_3();
    $("#new_analysis5").modal("hide");

  })
  .fail(function (data) {
    console.log("Fail");
  })
}

function addPatologoRow_5(exam) {
  var sampleRowTemplate = document.getElementById("patologo_row_5").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'exam': exam, 'patologos': patologos_list});

  $("#patologo_table_5 tbody").append(templateHTML)
  $('#patologos-select_5-'+exam.id).select2();
}

function removePatologoRow_5(exam_id){
  $('#exam_5-'+exam_id).remove();
}

function showServiceCommentsModal(form_id){
  $('#service_comments_modal').modal('show');
}

function deleteExternalReport(analysis_id, id){
  var url = Urls.service_reports_id(analysis_id, id);
  $.ajax({
    type: "DELETE",
    url: url,
  })
  .done(function (data) {
    toastr.success('', 'Informe eliminado exitosamente.');
    $('#sr-'+id).remove();
  })
  .fail(function () {
    toastr.error('', 'No ha sido posible eliminar el informe. Intente nuevamente.');
  });
}

function deleteServiceComment(analysis_id, id){
  var url = Urls.service_comments_id(analysis_id, id);
  $.ajax({
    type: "DELETE",
    url: url,
  })
  .done(function (data) {
    toastr.success('', 'Comentaario eliminado exitosamente.');
    $('#sc-'+id).remove();
  })
  .fail(function () {
    toastr.error('', 'No ha sido posible eliminar el informe. Intente nuevamente.');
  });
}

function showServiceReportsModal(id, service, case_closed, form_closed=false){

  $('#service_reports_internal').html('');
  if (service == 1){
    var temp_internal = '<h4>Generado por el sistema</h4>';
    temp_internal += '<div class="col-sm-12 pl-2 pb-2">';
    temp_internal += '<a target="_blank" href="/download-report/'+id+'"><i class="fa fa-download"></i> Descargar Informe</a>';
    temp_internal += '</div>';
    $('#service_reports_internal').html(temp_internal);
  }

  $('#service_reports_external').html('');
  var temp_external = '<h4>Agregados manualmente</h4>';
  temp_external += '<div id="reports_list" class="col-sm-12 pl-2 pb-2">';
  var url = Urls.service_reports(id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    if (data.reports.length > 0) {
      if (!form_closed) {
        $.each(data.reports, function(index, value){
          temp_external += '<div id="sr-'+value.id+'"><button class="btn btn-sm btn-danger" onclick="deleteExternalReport('+id+', '+value.id+')"><i class="fa fa-close"></i></button> <a target="_blank" href="'+value.path+'"><i class="fa fa-download"></i> '+value.name+'</a></div>';
        });
      } else {
        $.each(data.reports, function(index, value){
          temp_external += '<div id="sr-'+value.id+'"><a target="_blank" href="'+value.path+'"><i class="fa fa-download"></i> '+value.name+'</a></div>';
        });
      }
    } else {
      temp_external += '<div><h5 class="not_available_text">No hay informes disponibles</h5>';
    }
    temp_external += '</div>';
    $('#service_reports_external').html(temp_external);
  })
  .fail(function () {
    console.log("Fail")
  });

  if (!form_closed) {
    var url = Urls.service_reports(id);
    var temp_uploader = "<h4>Cargador de informes</h4>";
    temp_uploader += '<div class="col-sm-12"><form id="reports_uploader" action="'+url+'" class="dropzone needsclick">';
    temp_uploader += '<div class="dz-message" data-dz-message>';
    temp_uploader += '<center><span><h3>Arrastra o selecciona el informe que deseas cargar</h3></span></center>';
    temp_uploader += '</div>';    
    temp_uploader += '</form></div>';
    // temp += '<input type="reset" class="btn btn-secondary" data-dismiss="modal" value="Salir">';
    // temp += '<input type="button" class="btn btn-primary submit-file" value="Cargar Imágen""></div></div></div>';
    $('#service_reports_external_uploader').html('');
    $('#service_reports_external_uploader').html(temp_uploader);

    $("#reports_uploader").dropzone({
      autoProcessQueue: false,
      acceptedFiles: ".doc, .docx, .pdf",
      init: function() {
        var submitButton = document.querySelector(".submit-file")
        myDropzone = this;
        submitButton.addEventListener("click", function() {
          myDropzone.processQueue();
        });
        this.on('sending', function(file, xhr, formData){
          lockScreen(1);
        });

        this.on("success", function(file, responseText) {
          if (responseText.ok) {
            toastr.success('', 'Informe cargado exitosamente.');
            this.removeFile(file);
            $('.not_available_text').remove();
            $('#reports_list').prepend('<div id="sr-'+responseText.file.id+'"><button class="btn btn-sm btn-danger" onclick="deleteExternalReport('+id+', '+responseText.file.id+')"><i class="fa fa-close"></i></button> <a target="_blank" href="'+responseText.file.path+'"><i class="fa fa-download"></i> '+responseText.file.name+'</a></div>');
          } else {
            toastr.error('', 'No ha sido posible cargar el informe. Intente nuevamente.');
          }
          lockScreen(0);
        });

        this.on("error", function(file, response) {
          this.removeFile(file);
          bootbox.hideAll();
          toastr.error('', 'No ha sido posible cargar el informe. Intente nuevamente.');
          lockScreen(0);
        });

        this.on("addedfile", function() {
          if (this.files[1]!=null){
            this.removeFile(this.files[0]);
          }
        });
      },
    });
  }

  $('#service_reports_modal').modal('show');
}

function showServiceCommentsModal(id, case_closed, form_closed=false){
  var temp = '';
  var url = Urls.service_comments(id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    if (data.comments.length > 0){
      if (!form_closed) {
        $.each(data.comments, function(index, value){
          temp += '<p id="sc-'+value.id+'"><button class="btn btn-sm btn-danger" onclick="deleteServiceComment('+id+', '+value.id+')"><i class="fa fa-close"></i></button> <b>'+value.done_by+' ('+value.created_at+'):</b> <br> '+value.text+'</p>';
        });
        
      } else {
        $.each(data.comments, function(index, value){
          temp += '<p id="sc-'+value.id+'"><b>'+value.done_by+' ('+value.created_at+'):</b> <br> '+value.text+'</p>';
        });
      }
      
    } else {
      temp += '<p><h5 class="not_available_text">No hay comentarios disponibles</h5></p>';
    }

    if (!form_closed) {
      temp += '<h3>Ingresar nuevo comentario:</h3>';
      if (case_closed != 0){
        temp += '<div class="col-sm-12"><textarea data-id="'+id+'" class="form-control disabled" rows="3" id="input_service_comment"></textarea></div>';
      } else {
        temp += '<div class="col-sm-12"><textarea data-id="'+id+'" class="form-control" rows="3" id="input_service_comment"></textarea></div>';
      }
    }
    
    $('#service_comments').html(temp);
  })
  .fail(function () {
    console.log("Fail")
  });


  $('#service_comments_modal').modal('show');
}

function saveServiceComment(){
  var id = $('#input_service_comment').data('id');
  var text = $('#input_service_comment').val();
  var url = Urls.service_comments(id);
  $.ajax({
    type: "POST",
    url: url,
    data: {'comment': text}
  })
  .done(function (data) {
    $('.not_available_text').remove();
    $('#service_comments').prepend('<p id="sc-'+data.comment.id+'"><button class="btn btn-sm btn-danger" onclick="deleteServiceComment('+id+', '+data.comment.id+')"><i class="fa fa-close"></i></button> <b>'+data.comment.done_by+' ('+data.comment.created_at+'):</b> <br> '+data.comment.text+'</p>');
    
  })
  .fail(function () {
    console.log("Fail")
  });

}

function closeService(form_id, analysis_id){

  var got_reports = 0;
  var got_comments = 0;

  var url = Urls.service_comments(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
  .done(function (data) {
    if (data.comments.length > 0) {
      got_comments = data.comments.length;
    }
    
  })

  var url = Urls.service_reports(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
  .done(function (data) {
    if (data.reports.length > 0) {
      got_reports = data.reports.length;
    }
  })

  swal({
    title: "Confirmación",
    text: "Antes de continuar le informamos que el servicio tiene la cantidad de "+got_reports+" reportes adjuntos y "+got_comments+" comentarios. ¿Confirma que desea realizar el cierre del servicio?",
    icon: "warning",
    showCancelButton: true,
    buttons: {
      cancel: {
          text: "No, cancelar!",
          value: null,
          visible: true,
          className: "btn-light",
          closeModal: true,
      },
      confirm: {
          text: "Sí, confirmo!",
          value: true,
          visible: true,
          className: "btn-primary",
          closeModal: true,
      }
    }
    }).then(isConfirm => {
    if (isConfirm) {
      
      var url = Urls.close_service(form_id);
      $.ajax({
        type: "POST",
        url: url,
      })
      .done(function (data) {
        window.location.reload();
      })
      .fail(function () {
        console.log("Fail")
      });
    }
  });

}

function cancelService(form_id){

  swal({
    title: "Confirmación",
    text: "¿Confirma que desea anular el servicio?",
    icon: "warning",
    showCancelButton: true,
    buttons: {
      cancel: {
          text: "No, cancelar!",
          value: null,
          visible: true,
          className: "btn-light",
          closeModal: true,
      },
      confirm: {
          text: "Sí, confirmo!",
          value: true,
          visible: true,
          className: "btn-primary",
          closeModal: true,
      }
    }
    }).then(isConfirm => {
    if (isConfirm) {
      
      var url = Urls.cancel_service(form_id);
      $.ajax({
        type: "POST",
        url: url,
      })
      .done(function (data) {
        window.location.reload();
      })
      .fail(function () {
        console.log("Fail")
      });
    }
  });

}

function reopenSerivce(form_id){

  swal({
    title: "Confirmación",
    text: "¿Confirma que desea reabrir el servicio?",
    icon: "warning",
    showCancelButton: true,
    buttons: {
      cancel: {
          text: "No, cancelar!",
          value: null,
          visible: true,
          className: "btn-light",
          closeModal: true,
      },
      confirm: {
          text: "Sí, confirmo!",
          value: true,
          visible: true,
          className: "btn-primary",
          closeModal: true,
      }
    }
    }).then(isConfirm => {
    if (isConfirm) {
      
      var url = Urls.reopen_form(form_id);
      $.ajax({
        type: "POST",
        url: url,
      })
      .done(function (data) {
        window.location.reload();
      })
      .fail(function () {
        console.log("Fail")
      });
    }
  });

}