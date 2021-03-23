var data_step_3;
var previous_data_exists = false;

function init_step_3() {
  console.log("init_step_3")
  var entryform_id = $('#entryform_id').val();
  var url = Urls.entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
  .done(function (data) {
    data_step_3 = data
    // console.log(data_step_3)
    $('.showSummaryBtn').removeClass("hidden");
    $('.showAttachedFilesBtn').removeClass("hidden");
    $('.showShareBtn').addClass("hidden");
    $('.showLogBtn').addClass("hidden");
    $('.newAnalysisBtn').addClass("hidden");
    $('.newAnalysisBtn5').addClass("hidden");
     // fillSummary(data);
    if (data.entryform.analyses.length > 0){
      previous_data_exists = true;
    }
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
  $('#stain_select').select2();
  $('#organs_select').select2({
    placeholder: "Órganos",
  });
  
  $('#exam_select').on("select2:select", function (e) {
    var data = e.params.data;
    let stain_id = $(data.element).data('stain')
    $("#stain_select").val(stain_id).trigger("change");
  });

  $('.switchery').remove();
  var elems = $('.switch2');
  $.each(elems, function (key, value) {
    new Switchery($(this)[0]);
  });
}

function loadExams(exams) {
  $("#exam_select").html("");
  $("#exam_select").append("<option>Seleccione Análisis</option>");
  $.each(exams, function (i, item) {
    var html = '<option data-stain="'+item.stain_id+'" data-service="'+item.service_id+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_select').append($(html));
  });
}

function loadStains(stains) {
  $("#stain_select").html("");
  $("#stain_select").append("<option>Seleccione Tinción</option>");
  $.each(stains, function (i, item) {
    var html = '<option value="'+item.id+'">'+item.abbreviation+'</option>';
    $('#stain_select').append($(html));
  });
}

function loadOrgans(organs) {
  $.each(organs, function (i, item) {
    var html = '<option value="'+item.id+'">'+item.abbreviation+'</option>';
    $('#organs_select').append($(html));
  });
}

function loadSamples(samples){
  $("#samples_table tbody").html("");
  var exams = [];
  $.each(samples, function(i, v){
    addSampleRow(v);
  });

  $('.sampleOrgansSelect').select2();
}

// Load prev samples and exams
function initialData(data) {
  loadSamples(data.samples);
  loadExams(data.exams);
  loadStains(data.stains);
  loadOrgans(data.organs);
}

function loadData(data){
  $.each(data.samples, function(i, sample){
    $.each(sample.sample_exams_set, function(_, value){
      console.log("value", value)
      let exam_id = value[0].exam_id
      let exam_name = value[0].exam_name
      let stain = {
        "id" : value[0].stain_id, 
        "abbr" : value[0].stain_abbr 
      }
      let rowspan = $('#sampleCheck-'+sample.id)[0].rowSpan + 1
      $('.delete-'+sample.id).hide();
      $('#sampleCheck-'+sample.id)[0].rowSpan = rowspan
      $('#sampleNro-'+sample.id)[0].rowSpan = rowspan 
      $('#sampleIden-'+sample.id)[0].rowSpan = rowspan
      $('#sampleOrgans-'+sample.id)[0].rowSpan = rowspan

      var html = addServiceRow(
        exam_name, 
        sample.id, 
        exam_id,
        stain,
        sample.organs_set,
        value[0].analysis_status
      );
      $("#sample-"+sample.id).after(html)
      let analisis_tr = $("#analisis-"+sample.id+"-"+exam_id+"-"+stain.id)
      let select_organs = analisis_tr.find(".organs-select").first()
      select_organs.select2();
      console.log("organs", value.map(o => o.organ_id))
      select_organs.val(value.map(o => o.organ_id)).trigger('change')
      
    });
  });
}

function addExamToSamples(){
  let analysis_selected = $("#exam_select").val();
  let stain_selected = $("#stain_select").val();
  let organs_selected = $("#organs_select").val();

  $.each(data_step_3.samples, function(i, sample){

    // if sample is checked 
    if ($("#sampleCheck-"+sample.id+" input").is(":checked")) {
      // add exam to empty samples
      let organs_to_analize = []

      for (let organ of organs_selected) {
        for (let elem of sample.organs_set){
          if (organ == elem.id) {
            organs_to_analize.push(elem)
          }
        }
      }
      
      let analisis_tr = $("#analisis-"+sample.id+"-"+analysis_selected+"-"+stain_selected)
      let select_organs = analisis_tr.find(".organs-select")
      
      if ( organs_to_analize.length > 0 && !analisis_tr.length ){
        let rowspan = $('#sampleCheck-'+sample.id)[0].rowSpan + 1
        $('.delete-'+sample.id).hide();
        $('#sampleCheck-'+sample.id)[0].rowSpan = rowspan
        $('#sampleNro-'+sample.id)[0].rowSpan = rowspan 
        $('#sampleIden-'+sample.id)[0].rowSpan = rowspan
        $('#sampleOrgans-'+sample.id)[0].rowSpan = rowspan

        var html = addServiceRow(
          $("#exam_select option:selected" ).text(), 
          sample.id, 
          analysis_selected,
          {"id": $("#stain_select").val(), "abbr": $("#stain_select option:selected" ).text()},
          sample.organs_set,
          "En Ingreso"
        );
        $("#sample-"+sample.id).after(html)
        let analisis_tr = $("#analisis-"+sample.id+"-"+analysis_selected+"-"+stain_selected)
        let select_organs = analisis_tr.find(".organs-select").first()
        select_organs.select2();
        select_organs.val(organs_to_analize.map(o => o.id)).trigger('change')
      
      } else if ( organs_to_analize.length > 0 && analisis_tr.length ) {

        let values = select_organs.val()
        for (let organ of organs_to_analize) {
          values.push(organ.id)
        }
        select_organs.val(values)
        select_organs.trigger('change')
      
      }
    }
  });
  return false
}

function removeExamFromSamples(){
  console.log("removeexam")

  let analysis_selected = $("#exam_select").val();
  let stain_selected = $("#stain_select").val();
  let organs_selected = $("#organs_select").val();

  $.each(data_step_3.samples, function(i, sample){

    // if sample is checked 
    if ($("#sampleCheck-"+sample.id+" input").is(":checked")) {
      let analisis_tr = $("#analisis-"+sample.id+"-"+analysis_selected+"-"+stain_selected)
      let select_organs = analisis_tr.find(".organs-select")
      
      if ( analisis_tr.length ){
        
        let organ_new_values = []
        let current_select_values = select_organs.val()
        for (let organ of current_select_values){
          if (!organs_selected.includes(organ)){
            organ_new_values.push(organ)
          }
        }
        if (organ_new_values.length > 0){
          select_organs.val(organ_new_values).trigger("change")
        } else {
          analisis_tr.remove()
          let rowspan = $('#sampleCheck-'+sample.id)[0].rowSpan
          $('#sampleCheck-'+sample.id)[0].rowSpan = rowspan - 1
          $('#sampleNro-'+sample.id)[0].rowSpan = rowspan - 1
          $('#sampleIden-'+sample.id)[0].rowSpan = rowspan - 1
          $('#sampleOrgans-'+sample.id)[0].rowSpan = rowspan - 1
          if (rowspan == 2)
            $('.delete-'+sample.id).show()
        }
      }
    }
  })
  return false
}

function validate_step_3(){
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
  // if ( $('#exam_select :selected').length <= 0 ) {
  //   toastr.error(
  //     'Para continuar debes tener seleccionado al menos un análisis.', 
  //     'Ups!', 
  //     {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
  //   );
  //   $('#exam_select').focus();
  //   return 0;
  // }

  return 1;
}

function addSampleRow(sample) {
  var sampleRowTemplate = document.getElementById("sample_row").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'sample': sample, 'organs': organs});

  $("#samples_table tbody").append(templateHTML)
}

function addServiceRow(analisis, sampleId, examId, stain, organs, status) {
  var sampleRowTemplate = document.getElementById("add_analisis").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs, 'stain':stain, 'analisis': analisis, 'sampleId': sampleId, 'examId': examId, 'status':status});
  return templateHTML;
}