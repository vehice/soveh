var data_step_2;
var organs_list;
var patologos_list;

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
    $('.showSummaryBtn').removeClass("hidden");
    $('.showShareBtn').addClass("hidden");
    $('.showLogBtn').addClass("hidden");
    $('.newAnalysisBtn').addClass("hidden");
    $('.newAnalysisBtn5').addClass("hidden");
     // fillSummary(data);
    initialData(data);
    loadData(data);
  })
  .fail(function () {
  })

  if ($('#exam_select').hasClass("select2-hidden-accessible")) {
    $('#exam_select').select2('destroy');
    $('#exam_select').off('select2:select');
    $('#exam_select').off('select2:unselect');
  }

  $('#exam_select').select2();
  
  $('#exam_select').on("select2:select", function (e) {
    var data = e.params.data;
    addExamToSamples(data);
    // addPatologoRow(data);
  });

  $('#exam_select').on("select2:unselect", function (e) {
    var data = e.params.data;
    removeExamFromSamples(data);
    // removePatologoRow(data.id);
  });

  $('#exam_select').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }
  });
}

function loadExams(exams) {
  $("#exam_select").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-examtype="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_select').append($(html));
  });
}

function loadSamples(samples, organs){
  $("#samples_table tbody").html("");
  $.each(samples, function (i, v){
    addSampleRow(v, organs);
    $.each(v.sample_exams_set, function(j,item){
      $('.delete-'+v.id).hide();
      var html = addOrgansOptions(item.exam_name, item.exam_type, v.id, item.exam_id, v.id+"-"+($('#sampleNro-'+v.id)[0].rowSpan + 1));
      $('#sampleNro-'+v.id)[0].rowSpan = $('#sampleNro-'+v.id)[0].rowSpan + 1; 
      $('#sampleIden-'+v.id)[0].rowSpan = $('#sampleIden-'+v.id)[0].rowSpan + 1; 
      $("#sample-"+v.id).after(html);

      $('.organs-select-'+ item.exam_id).select2();
      $('.organs-select-'+ item.exam_id).on('select2:select', function(e){
        var values = e.params.data.id;
        $.each($('.organs-select-'+ item.exam_id), function(i,v){
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
      $('#'+v.id+"-"+$('#sampleNro-'+v.id)[0].rowSpan).val(values);
      $('#'+v.id+"-"+$('#sampleNro-'+v.id)[0].rowSpan).trigger('change');
    });
  });
 

  $('.samples_organs').select2();
  // $('.samples_exams').select2();

  // $('.samples_exams').on("select2:unselecting", function (e) {
  //   if (e.params.args.originalEvent) {
  //     e.params.args.originalEvent.stopPropagation();
  //   }
  // });
  
}

function initialData(data) {
  organs_list = data.organs;
  patologos_list = data.patologos;
  loadSamples(data.samples, data.organs);
  loadExams(data.exams);
}

function loadData(data){
  $('#patologo_table tbody').html('');
  // Fill analyses
  $.each(data.entryform.analyses, function(i, item){
    $('#exam_select option[value="'+item.exam_id+'"]').prop('selected', true);
    // addPatologoRow({text: item.exam__name, id: item.exam_id});
    $('#patologos-select-'+item.exam_id).val(item.patologo_id);
    $('#patologos-select-'+item.exam_id).trigger('change');
  });

  // Fill exams and organs per samples
  $.each(data.samples, function(i, item){
    $.each(item.exams_set, function(j, item2){
      var selected_exam = new Option(item2.name, item2.id, true, true);
      $('#sample-'+item.id+' .samples_exams').append(selected_exam).trigger('change');
    });

    $.each(item.organs_set, function(k, item3){
      var selected_organ = new Option(item3.name, item3.id, true, true);
      $('#sample-'+item.id+' .samples_organs').append(selected_organ).trigger('change');
    });
  });
}

function addExamToSamples(exam){
  $('#samples_table .samples_exams').each( function(i){
    // if($(this).val() == "" || $(this).val() == null){
      //show analisis selected
      // var new_exam = new Option(exam.text, exam.id, true, true);
      // $(this).append(new_exam).trigger('change');
      // $(this).val(exam.text);
      // $(this).data('id', exam.id);
      var sampleId = $(this).data('index');
      $('.delete-'+sampleId).hide();
      $('#sampleNro-'+sampleId)[0].rowSpan = $('#sampleNro-'+sampleId)[0].rowSpan + 1; 
      $('#sampleIden-'+sampleId)[0].rowSpan = $('#sampleIden-'+sampleId)[0].rowSpan + 1; 
      //show organs options
      var html = addOrgansOptions(exam.text, $(exam.element).data('examtype'), sampleId, exam.id);
      $("#sample-"+sampleId).after(html);
    // }
  }); 
  $('.organs-select-'+ exam.id).select2();
  $('.organs-select-'+ exam.id).on('select2:select', function(e){
    var values = e.params.data.id;
    $.each($('.organs-select-'+ exam.id), function(i,v){
      var old_values = $(v).val();
      old_values.push(values);
      $(v).val(old_values);
      $(v).trigger('change');
    });
  });
}

function removeExamFromSamples(exam){
  $('#samples_table .analis-row').each( function(i){
    if($(this).data('sampleid') == exam.id){
      var sampleIndex = $(this).data('sampleindex');
      $('#sampleNro-'+sampleIndex)[0].rowSpan = $('#sampleNro-'+sampleIndex)[0].rowSpan - 1; 
      $('#sampleIden-'+sampleIndex)[0].rowSpan = $('#sampleIden-'+sampleIndex)[0].rowSpan - 1; 
      $(this).remove();
      if($('#sampleIden-'+sampleIndex)[0].rowSpan == 1)
        $('.delete-'+sampleIndex).show();
    }
  }); 
}

function initialConf() {
  $('#exam_select').select2();
}

function validate_step_2(){
  // Validates sample exam assignation
  var missing_exams_select = false;
  $('#samples_table .samples_exams').each( function(i){
    var id = $(this).data('index');
    if ( $('.analis-row-'+id).length <= 0 ){
      $(this).focus();
      missing_exams_select = true;
      return 0;
    }
  });

  if (missing_exams_select){
    toastr.error(
      'Para continuar debes asignar al menos un análisis a realizar por muestra.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    return 0;
  }

  // Validates sample organ assignation
  var missing_organs_select = false;
  $('#samples_table .organs-select').each( function(i){
    if ( $(this).find(":selected").length <= 0 ){
      $(this).focus();
      missing_organs_select = true;
      return 0;
    }
  });

  if (missing_organs_select){
    toastr.error(
      'Para continuar es necesario definir el o los organos por muestra.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    return 0;
  }

  // Validates exam selection
  if ( $('#exam_select :selected').length <= 0 ) {
    toastr.error(
      'Para continuar debes tener seleccionado al menos un análisis.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    $('#exam_select').focus();
    return 0;
  }
  var saltar = 5;
  $.each($('#exam_select :selected'), function(i,v){
    if ($(v).data('examtype') == 1){
      saltar = 3;
    }
  });

  return saltar;
 
}


function addAnalysisTemplate(data) {
  var analysisTemplate = document.getElementById("analysis_template").innerHTML;

  var templateFn = _.template(analysisTemplate);
  var templateHTML = templateFn(data);

  $("#exam_group").html(templateHTML)
  $('.samples_organs').select2();
  $('.samples_analysis').select2();

  $('.samples_organs').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }
  });

  $('.samples_analysis').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }
  });
  
}

function addSampleRow(sample, organs) {
  var sampleRowTemplate = document.getElementById("sample_row").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'sample': sample, 'organs': organs});

  $("#samples_table tbody").append(templateHTML)
}

function addOrgansOptions(analisis, analisis_type, sampleId, sampleIndex, optionId = null) {
  var sampleRowTemplate = document.getElementById("add_analisis").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs_list, 'type': analisis_type, 'analisis': analisis, 'sampleId': sampleId, 'sampleIndex': sampleIndex, 'optionId': optionId});
  return templateHTML;
}

function deleteAnalisis(sampleId, sampleIndex, active){
  if(active)
  {
    $('#analisis-'+sampleId+'-'+sampleIndex).remove();
    $('#sampleNro-'+sampleId)[0].rowSpan = $('#sampleNro-'+sampleId)[0].rowSpan - 1; 
    $('#sampleIden-'+sampleId)[0].rowSpan = $('#sampleIden-'+sampleId)[0].rowSpan - 1; 
    if($('#sampleIden-'+sampleId)[0].rowSpan == 1)
      $('.delete-'+sampleId).show();
    var exist = 0;
    $('#samples_table .analis-row').each( function(i){
      if($(this).data('sampleid') == sampleIndex){
        exist +=1;
      }
    }); 
    if(!exist){
      var old_values = $('#exam_select').val();
      old_values.splice(old_values.indexOf(sampleIndex), 1);
      $('#exam_select').val(old_values);
      $('#exam_select').trigger('change');
      $('#exam-'+sampleIndex).remove();
    }
  }
}

// function addPatologoRow(exam) {
//   var sampleRowTemplate = document.getElementById("patologo_row").innerHTML;

//   var templateFn = _.template(sampleRowTemplate);
//   var templateHTML = templateFn({'exam': exam, 'patologos': patologos_list});

//   $("#patologo_table tbody").append(templateHTML)
//   $('#patologos-select-'+exam.id).select2();
// }

// function removePatologoRow(exam_id){
//   $('#exam-'+exam_id).remove();
// }