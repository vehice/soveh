function init_step_4() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.cassette_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      $('.showSummaryBtn').removeClass("hidden");
      $('.newAnalysisBtn').removeClass("hidden");
      fillSummary(data);
      fillNewAnalysis(data);
      loadBlockTable(data);
    })
    .fail(function () {
      console.log("Fail")
    })
    
    if ($('#exam_new_select').hasClass("select2-hidden-accessible")) {
      $('#exam_new_select').select2('destroy');
      $('#exam_new_select').off('select2:select');
      $('#exam_new_select').off('select2:unselect');
    }
  
    $('#exam_new_select').select2();
    
    $('#exam_new_select').on("select2:select", function (e) {
      var data = e.params.data;
      addNewExamToSamples(data);
    });
  
    $('#exam_new_select').on("select2:unselect", function (e) {
      var data = e.params.data;
      removeNewExamFromSamples(data);
    });
  
    $('#exam_new_select').on("select2:unselecting", function (e) {
      if (e.params.args.originalEvent) {
        e.params.args.originalEvent.stopPropagation();
      }
    });
}

$(document).on('change', '#block_table :checkbox', function (e) {
  if (e.target.checked) {
    $("[name='" + e.target.id + "']").val(moment().format());
  } else {
    $("[name='" + e.target.id + "']").val("");
  }
})

$(document).on('click', '.block_start_all', function (e) {
  $("input[type=checkbox][id^='block_start_block']" ).trigger('click');
});

$(document).on('click', '.block_end_all', function (e) {
  $("input[type=checkbox][id^='block_end_block']" ).trigger('click');
});

$(document).on('click', '.slice_start_all', function (e) {
  $("input[type=checkbox][id^='block_start_slice']" ).trigger('click');
});

$(document).on('click', '.slice_end_all', function (e) {
  $("input[type=checkbox][id^='block_end_slice']" ).trigger('click');
});

function loadBlockTable(data) {
  if ($.fn.DataTable.isDataTable('#block_table')) {
    $('#block_table').DataTable().clear().destroy();
  }

  populateBlockTable(data);

  var elems = Array.prototype.slice.call(document.querySelectorAll('.switchery'));

  elems.forEach(function (html) {
    new Switchery(html);
  });

  $('[data-toggle="popover"]').popover();

  $('#block_table').DataTable({
    ordering: false,
    paginate: false,
    // scrollX: true,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });
}

function populateBlockTable(data) {

  $.each(data.cassettes, function (i, item) {
    var row = {};

    row.sample_id = item.sample.id;
    row.sample_index = item.sample.index;
    row.cassette_name = item.cassette_name;
    row.cassette_pk = item.id;
    row.cassette_index = item.index;
    row.organs = item.organs_set.join(", ")
    row.no_slice = item.sample.exams_set.length;
    row.block_index = i;

    if (item.slices_set.length > 0) {
      row.start_block = item.slices_set[0].start_block;
      row.end_block = item.slices_set[0].end_block;
      row.start_slice = item.slices_set[0].start_slice;
      row.end_slice = item.slices_set[0].end_slice;
    } else {
      row.start_block = "";
      row.end_block = "";
      row.start_slice = "";
      row.end_slice = "";
    }

    row.slice_info = "<ol>";
    $.each(item.sample.exams_set, function (i, elem) {
      row.slice_info += "<li><p><strong>Cassette:</strong> " + row.cassette_name + " <strong> </br>Muestra: </strong>" + row.sample_index + " <strong> </br>Corte: </strong>" +row.cassette_name+"-S"+(i+1).toString()+" <strong> </br>An&aacute;lisis: </strong>" + elem.name + "</p></li>"
    })
    row.slice_info += "</ol>";

    addBlockRow(row)

    if (item.slices_set.length > 0) {
      $("[data-index='" + i + "']").find(".switchery").trigger("click");
    }
  });
}

function addBlockRow(data) {
  var blockRowTemplate = document.getElementById("block_dyeing_row").innerHTML;

  var templateFn = _.template(blockRowTemplate);
  var templateHTML = templateFn(data);

  $("#block_table tbody").append(templateHTML)
}

function fillNewAnalysis(data) {
  organs_list = data.organs;
  loadNewSamples(data.samples, data.organs);
  loadNewExams(data.exams_set);
  $.each(data.entryform.analyses, function(i, item){
    $('#exam_new_select option[value="'+item.exam_id+'"]').prop('selected', true);
  });
  $('#exam_new_select').trigger('change');
}

function loadNewExams(exams) {
  $("#exam_new_select").html("");
  $.each(exams, function (i, item) {
    var html = '<option data-examtype="'+item.exam_type+'" value="'+item.id+'">'+item.name+'</option>';
    $('#exam_new_select').append($(html));
  });
}

function addNewExamToSamples(exam){
  $('#samples_new_table .samples_new_exams').each( function(i){
      var sampleId = $(this).data('index');
      $('.delete_new-'+sampleId).hide();
      $('#sampleNro_new-'+sampleId)[0].rowSpan = $('#sampleNro_new-'+sampleId)[0].rowSpan + 1; 
      $('#sampleIden_new-'+sampleId)[0].rowSpan = $('#sampleIden_new-'+sampleId)[0].rowSpan + 1; 
      //show organs options
      var html = addNewOrgansOptions(exam.text, $(exam.element).data('examtype'), sampleId, exam.id);
      $("#sample_new-"+sampleId).after(html);
    // }
  }); 
  $('.organs_new_select-'+ exam.id).select2();
  $('.organs_new_select-'+ exam.id).on('select2:select', function(e){
    var values = e.params.data.id;
    $.each($('.organs_new_select-'+ exam.id), function(i,v){
      var old_values = $(v).val();
      old_values.push(values);
      $(v).val(old_values);
      $(v).trigger('change');
    });
  });
}

function removeNewExamFromSamples(exam){
  $('#samples_new_table .analis_new_row').each( function(i){
    if($(this).data('sampleid') == exam.id && !$(this).hasClass('old_row')){
      var sampleIndex = $(this).data('sampleindex');
      $('#sampleNro_new-'+sampleIndex)[0].rowSpan = $('#sampleNro_new-'+sampleIndex)[0].rowSpan - 1; 
      $('#sampleIden_new-'+sampleIndex)[0].rowSpan = $('#sampleIden_new-'+sampleIndex)[0].rowSpan - 1; 
      $(this).remove();
      if($('#sampleIden_new-'+sampleIndex)[0].rowSpan == 1)
        $('.delete_new-'+sampleIndex).show();
    }
  }); 
}

function loadNewSamples(samples, organs){
  $("#samples_new_table tbody").html("");
  $.each(samples, function (i, v){
    addNewSampleRow(v, organs);
    $.each(v.sample_exams_set, function(j,item){
      $('.delete_new-'+v.id).hide();
      var html = addOldOrgansOptions(item.exam_name, item.exam_type, v.id, item.exam_id, v.id+"-"+($('#sampleNro_new-'+v.id)[0].rowSpan + 1));
      $('#sampleNro_new-'+v.id)[0].rowSpan = $('#sampleNro_new-'+v.id)[0].rowSpan + 1; 
      $('#sampleIden_new-'+v.id)[0].rowSpan = $('#sampleIden_new-'+v.id)[0].rowSpan + 1; 
      $("#sample_new-"+v.id).after(html);
     
      $('.organs_new_select-'+ item.exam_id).select2();
      $('.organs_new_select-'+ item.exam_id).on('select2:select', function(e){
        var values = e.params.data.id;
        $.each($('.organs_new_select-'+ item.exam_id), function(i,v){
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
      $('#select'+v.id+"-"+$('#sampleNro_new-'+v.id)[0].rowSpan).val(values);
      $('#select'+v.id+"-"+$('#sampleNro_new-'+v.id)[0].rowSpan).trigger('change');
    });
  });
 

  $('.samples_organs').select2();
}

function addNewSampleRow (sample, organs) {
  var sampleRowTemplate = document.getElementById("sample_new_row").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'sample': sample, 'organs': organs});

  $("#samples_new_table tbody").append(templateHTML)
}

function addNewOrgansOptions(analisis, analisis_type, sampleId, sampleIndex, optionId = null) {
  var sampleRowTemplate = document.getElementById("add_new_analisis").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs_list, 'type': analisis_type, 'analisis': analisis, 'sampleId': sampleId, 'sampleIndex': sampleIndex, 'optionId': optionId});
  return templateHTML;
}

function addOldOrgansOptions(analisis, analisis_type, sampleId, sampleIndex, optionId = null) {
  var sampleRowTemplate = document.getElementById("add_old_analisis").innerHTML;

  var templateFn = _.template(sampleRowTemplate);
  var templateHTML = templateFn({'organs': organs_list, 'type': analisis_type, 'analisis': analisis, 'sampleId': sampleId, 'sampleIndex': sampleIndex, 'optionId': optionId});
  return templateHTML;
}

function deleteNewAnalisis(sampleId, sampleIndex){
  $('#analisis_new-'+sampleId+'-'+sampleIndex).remove();
  $('#sampleNro_new-'+sampleId)[0].rowSpan = $('#sampleNro_new-'+sampleId)[0].rowSpan - 1; 
  $('#sampleIden_new-'+sampleId)[0].rowSpan = $('#sampleIden_new-'+sampleId)[0].rowSpan - 1; 
  if($('#sampleIden_new-'+sampleId)[0].rowSpan == 1)
    $('.delete_new-'+sampleId).show();
  var exist = 0;
  $('#samples_new_table .analis_new_row').each( function(i){
    if($(this).data('sampleid') == sampleIndex){
      exist +=1;
    }
  }); 
  if(!exist){
    var old_values = $('#exam_new_select').val();
    old_values.splice(old_values.indexOf(sampleIndex), 1);
    $('#exam_new_select').val(old_values);
    $('#exam_new_select').trigger('change');
  }
}

function submitNewAnalysis(){
  var url = Urls.workflow();
  form_data = $("#modal_3 :input").serialize();
  var response;
  $.ajax({
    type: "POST",
    url: url,
    data: form_data + "&id_next_step=3&previous_step=0",
    async: false,
  })
  .done(function (data) {
    init_step_4();
    $("#new_analysis").modal("hide");

  })
  .fail(function (data) {
    console.log("Fail");
  })
}