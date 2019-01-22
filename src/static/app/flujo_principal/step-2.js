var data_step_2;

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
    fillSummary(data);
    initialData(data);
    loadData(data);
  })
  .fail(function () {
  })

  $('#exam_select').select2();
  
  $('#exam_select').on("select2:select", function (e) {
    var data = e.params.data;
    addExamToSamples(data);
  });

  $('#exam_select').on("select2:unselect", function (e) {
    var data = e.params.data;
    removeExamFromSamples(data);
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
    $('#exam_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadSamples(samples, organs){
  $("#samples_table tbody").html("");
  $.each(samples, function (i, item){
    addSampleRow(item, organs);
  });

  $('.samples_organs').select2();
  $('.samples_exams').select2();

  $('.samples_exams').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }
  });
  
}

function initialData(data) {
  loadSamples(data.samples, data.organs);
  loadExams(data.exams);
}

function loadData(data){

  // Fill analyses
  $.each(data.entryform.analyses, function(i, item){
    $('#exam_select option[value="'+item.exam_id+'"]').prop('selected', true);
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
    var new_exam = new Option(exam.text, exam.id, true, true);
    $(this).append(new_exam).trigger('change');
  }); 
}

function removeExamFromSamples(exam){
  $('#samples_table .samples_exams').each( function(i){
    $(this).find("option[value='"+ exam.id+"']").remove();
    $(this).trigger('change');
  }); 
}

function initialConf() {
  $('#exam_select').select2();
}

function validate_step_2(){
  // Validates exam selection
  if ( $('#exam_select :selected').length <= 0 ) {
    toastr.error(
      'Para continuar debes tener seleccionado al menos un análisis.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    $('#exam_select').focus();
    return false;
  }

  // Validates sample exam assignation
  var missing_exams_select = false;
  $('#samples_table .samples_exams').each( function(i){
    if ( $(this).find(":selected").length <= 0 ){
      $(this).focus();
      missing_exams_select = true;
      return false;
    }
  });

  if (missing_exams_select){
    toastr.error(
      'Para continuar debes asignar al menos un análisis a realizar por muestra.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    return false;
  }

  // Validates sample organ assignation
  var missing_organs_select = false;
  $('#samples_table .samples_organs').each( function(i){
    if ( $(this).find(":selected").length <= 0 ){
      $(this).focus();
      missing_organs_select = true;
      return false;
    }
  });

  if (missing_organs_select){
    toastr.error(
      'Para continuar es necesario definir el o los organos por muestra.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    return false;
  }

  return true;
 
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
