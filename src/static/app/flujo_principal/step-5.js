function init_step_5(active = true) {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.analysis_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      $('.showSummaryBtn').removeClass("hidden");
      $('.newAnalysisBtn').addClass("hidden");
      if(active){
        $('.newAnalysisBtn5').removeClass("hidden");
      }
      // fillSummary(data);
      saltar=true;
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
    });
  
    $('#exam_new_select5').on("select2:unselect", function (e) {
      var data = e.params.data;
      removeNewExamFromSamples5(data);
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
    row.exam_name = item.exam_name;
    row.exam_stain = item.exam_stain;
    row.no_slice = item.slices.length;
    row.current_step = item.exam_type == 1 ? item.current_step : Math.floor(item.current_step/5);
    row.total_step = item.total_step;
    row.percentage_step = item.percentage_step;
    row.current_step_tag = item.current_step_tag;
    row.form_closed = item.form_closed;
    row.form_reopened = item.form_reopened;
    row.histologico = item.exam_type == 1;
    saltar=saltar && item.exam_type == 2;
    addAnalysisElement(row)
  });
}

function addAnalysisElement(data) {
  var analysisElementTemplate = document.getElementById("analysis_element5").innerHTML;

  var templateFn = _.template(analysisElementTemplate);
  var templateHTML = templateFn(data);

  $("#analysis_group").append(templateHTML)
}

function fillNewAnalysis2(data) {
  organs_list = data.organs;
  loadNewSamples5(data.samples, data.organs);
  loadNewExams5(data.exams_set);
  $.each(data.entryform.analyses, function(i, item){
    $('#exam_new_select5 option[value="'+item.exam_id+'"]').prop('selected', true);
  });
  $('#exam_new_select5').trigger('change');
}

function loadNewExams5(exams) {
  $("#exam_new_select5").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-examtype="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_new_select5').append($(html));
  });
}

function loadNewExams(exams) {
  $("#exam_new_select5").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-examtype="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
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
      var html = addNewOrgansOptions5(exam.text, $(exam.element).data('examtype'), sampleId, exam.id);
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
    init_step_5();
    $("#new_analysis5").modal("hide");

  })
  .fail(function (data) {
    console.log("Fail");
  })
}