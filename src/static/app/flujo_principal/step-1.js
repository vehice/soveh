// Data Template
var organs;

function init_step_1() {
  var url = Urls.entryform();
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    initialData(data);
    initialConf();
    loadData();

    organs = data.organs;
  })
  .fail(function () {
    console.log("Fail")
  });

  $('#identification_group').on("click", "#add_identification", function (e) {
    addIdentificationTemplate({
      temp_id : Math.random().toString(36).replace('0.', '')
    });
  });

  $('#identification_group').on("click", "#delete_identification", function (e) {
    $(this).closest(".identification").remove();
    refreshNoFish();
  })

  $('#identification_group').on('change', '[name="identification[no_fish]"]', function (e) {
    refreshNoFish();
  })

  $('#exam_select').on('change', function (e) {
    var selected = $(this).find("option:selected").val();
  });

  $('#loadSamplesToAnalysis').on("click", function (e) {
    var no_fish = countNoFish();

    if ( no_fish <= 0 ) {
      toastr.error(
        'Debes identificar muestras para poder continuar.', 
        'Ups!', 
        {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
      );
      $('input[name="identification[no_fish]"]').focus();
      return false;
    }

    if ( $('#exam_select :selected').length <= 0 ) {
      toastr.error(
        'Debes seleccionar al menos un análisis para asignar muestras.', 
        'Ups!', 
        {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
      );
      $('#exam_select').focus();
      return false;
    }
    $('#exam_group').html('<center><i class="fa fa-cog spinner font-large-3"></i></center>');

    var analysis = [];
    $.each($('#exam_select :selected'), function(i) {
      analysis.push({
        'id' : $(this).val(),
        'name' : $(this).text()
      });
    });

    var samples = [];
    var sample_index_start = 1;

    $('.identification').each(function(i) {
      var id_temp = $(this).find('input[name="identification[id]"]').val();
      var cage = $(this).find('input[name="identification[cage]"]').val();
      var group = $(this).find('input[name="identification[group]"]').val();
      var no_fish = parseInt($(this).find('input[name="identification[no_fish]"]').val()) || 0;
      var j;
      var end_index = no_fish + sample_index_start;
      for (j = sample_index_start; j < end_index; j++) { 
        samples.push({
          'identification_id' : id_temp,
          'cage' : cage,
          'group' : group,
          'sample_index' : j,
          'analysis' : analysis,
          'organs' : organs
        });
      }
      sample_index_start = end_index;

    });
    addAnalysisTemplate({'data': samples});
  });

  $("#exam_group").on("click", function (e) {
    if (e.target.id === 'delete_analysis') {
      var analysis_id = $(e.target).closest("[data-id]").data("id").toString();
      var analysis_select = $('#exam_select')
      var values_analysis_select = analysis_select.val();

      if (values_analysis_select) {
        var i = values_analysis_select.indexOf(analysis_id);
        if (i >= 0) {
          values_analysis_select.splice(i, 1);
          analysis_select.val(values_analysis_select).change();
        }
      }
      $(e.target).closest("[data-id]").remove()
    }
  });

  $(document).on('click', '#FlowDividerOptions a', function (e) {
    if (e.target.id === 'base_flowdivider_by_identification') {
      $('#flow_divide_option').val(1);
      $('[name="identification[no_fish]"]').each(function (i, element) {
        var no_fish = parseInt($(element).val()) || 0;
        var templateData = {
          'group_size_text' : no_fish.toString()+" PECES",
          'group_count': (i+1).toString()
        };
        addWorkGroupTemplateByIdentity(templateData);
      });
    } else {
      $('#flow_divide_option').val(2);
      var group_data = getManualGroupsData();
      $.each(group_data, function(i, item){
        var aux = {
          "group_fishes" : item,
          "group_nro" : i+1
        };
        addWorkGroupTemplateByManual(aux);
      });

      $('.fishSelection').select2({
        'placeholder': "Por favor selecciona los peces"
      });

      $('.fishSelection').on('select2:select', function (e) {
        var id = e.params.data.id;
        $(".fishSelection > option[value='"+id+"']").each(function (i, element) {
          $(element).prop("disabled", true);
        });
        $('.fishSelection').select2({
          'placeholder': "Por favor selecciona los peces"
        });
      });

      $('.fishSelection').on('select2:unselect', function (e) {
        var id = e.params.data.id;
        $(".fishSelection > option[value='"+id+"']").each(function (i, element) {
          $(element).prop("disabled", false);
        });
        $('.fishSelection').select2({
          'placeholder': "Por favor selecciona los peces"
        });
      });
    }
  });
  
  $('#select_if_divide_flow').on("change", function(e) {
    var if_split = $(this).val();
    $('#flow_divider_options').html("");

    if (if_split == "1"){
      if ( countNoFish() > 0 ){
        addFlowDividerTemplate();
        $('#FlowDividerOptions li:first-child a').trigger('click');
      } else {
        toastr.error('Es necesario completar la identificación de peces para poder subdividir el flujo de trabajo.', 'Aviso');
        $(this).find('option[value="0"]').prop('selected', true);
      }
    }
  });

  $(document).on('change', '#flowdivider_manual_group_quantity', function(e){
    var group_data = getManualGroupsData();
    $.each(group_data, function(i, item){
      var aux = {
        "group_fishes" : item,
        "group_nro" : i+1
      };
      addWorkGroupTemplateByManual(aux);
    });

    $('.fishSelection').select2({
      'placeholder': "Por favor selecciona los peces"
    });

    $('.fishSelection').on('select2:select', function (e) {
      var id = e.params.data.id;
      $(".fishSelection > option[value='"+id+"']").each(function (i, element) {
        $(element).prop("disabled", true);
      });
      $('.fishSelection').select2({
        'placeholder': "Por favor selecciona los peces"
      });
    });

    $('.fishSelection').on('select2:unselect', function (e) {
      var id = e.params.data.id;
      $(".fishSelection > option[value='"+id+"']").each(function (i, element) {
        $(element).prop("disabled", false);
      });
      $('.fishSelection').select2({
        'placeholder': "Por favor selecciona los peces"
      });
    });
  });

  $('#exam_select').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }
  });

  function getManualGroupsData() {
    var group_quantity = parseInt(parseFloat($('#flowdivider_manual_group_quantity').val()));
    var group_data = [];
    for (var i = 1; i <= group_quantity; i++) {
      var select = [];
      $('[name="identification[no_fish]"]').each(function (i, element) {
        var no_fish = parseInt($(element).val()) || 0;
        var identification_id = $(element).closest('.identification').get(0).id;
        var cage = $(element).closest('.identification').find('[name="identification[cage]"]').val();
        var group = $(element).closest('.identification').find('[name="identification[group]"]').val();
        for (var j = 1; j <= no_fish; j++) {
          select.push({
            'identification_id' : identification_id,
            'fish_num' : j,
            'cage': cage,
            'group': group
          });
        }
      });
      group_data.push(select);
    }
    return group_data;
  }

  function loadData() {
    var entryform_id = $('#entryform_id').val();
    var url = Urls.entryform_id(entryform_id);
    $.ajax({
      type: "GET",
      url: url,
    })
      .done(function (data) {
        var entryform = data.entryform;

        $('#customer_select').val(entryform.customer_id).trigger('change');
        $('#fixtative_select').val(entryform.fixative_id).trigger('change');
        $('#larvalstage_select').val(entryform.larvalstage_id).trigger('change');
        $('#watersource_select').val(entryform.watersource_id).trigger('change');
        $('#specie_select').val(entryform.specie_id).trigger('change');

        $('#observation').val(entryform.observation);
        $('#order_number_input').val(entryform.no_order);
        $('#request_number_input').val(entryform.no_request);
        $('#company_input').val(entryform.company);
        $('#center_input').val(entryform.center);
        $('#responsible_input').val(entryform.responsible);

        if (entryform.created_at) {
          $('[name="created_at"]').val(moment(entryform.created_at).format("DD/MM/YYYY HH:MM") || "");
        } else {
          $('[name="created_at"]').val("");
        }
        if (entryform.sampled_at) {
          $('[name="sampled_at"]').val(moment(entryform.sampled_at).format("DD/MM/YYYY HH:MM") || "");
        } else {
          $('[name="sampled_at"]').val("");
        }

        $('#created_at_submit').val(entryform.created_at);
        $('#sampled_at_submit').val(entryform.sampled_at);

        $.each(entryform.answer_questions, function (i, item) {
          var question_id = item.question_id
          var answer = item.answer

          $("#question_" + question_id + "_" + answer).prop('checked', true);
        });

        var identification_size = entryform.identifications.length;

        if (identification_size > 1) {
          for (var i = 1; i < identification_size; i++) {
            $("#add_identification").trigger("click");
          }
        }

        var identifications_cage = $('[name="identification[cage]"]');
        var identifications_group = $('[name="identification[group]"]');
        var identifications_no_fish = $('[name="identification[no_fish]"]');
        var identifications_no_container = $('[name="identification[no_container]"]')

        $.each(entryform.identifications, function (i, item) {
          $(identifications_cage[i]).val(item.cage);
          $(identifications_group[i]).val(item.group);
          $(identifications_no_fish[i]).val(item.no_fish);
          $(identifications_no_container[i]).val(item.no_container);
        });

        var exams_id = _.map(entryform.analyses, 'exam_id');

        if (exams_id.length > 0) {        
          $("#exam_select").val(exams_id).trigger("change");
          $('#loadSamplesToAnalysis').click();
        }

      })
      .fail(function () {
        console.log("Fail")
      })
  }
}

function validate_step_1(){
  var no_fish = countNoFish();
  
  // Validates Identifications
  if ( no_fish <= 0 ) {
    toastr.error(
      'Para continuar debes tener las muestras identificadas.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    $('input[name="identification[no_fish]"]').focus();
    return false;
  }

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

  // Validates samples asignation
  if ( $('input[name*="sample[index]"').length <= 0) {
    toastr.error(
      'Para continuar debes asignar los examenes seleccionados a las muestras ingresadas.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    $('#loadSamplesToAnalysis').focus();
    return false;
  }

  return true;
  
}

// Function for events

function countNoFish() {
  var no_fish = 0
  $('[name="identification[no_fish]"]').each(function (i, element) {
    no_fish += parseInt($(element).val()) || 0
  });

  return no_fish
}

function countSelectedFishes(){
  var no_fish = 0
  $('[name*="analysis[no_fish]"]').each(function (i, element) {
    no_fish += parseInt($(element).val()) || 0
  });

  return no_fish
}

function refreshNoFish() {
  var no_fish = countNoFish()

  $('[name*="analysis[no_fish]"]').each(function (i, element) {
    $(element).val(no_fish);
  });

  // $('#flow_divider').trigger('change');
}

function splitArrayByChunkSize(arr, n) {
  var rest = arr.length % n,
      restUsed = rest,
      partLength = Math.floor(arr.length / n),
      result = [];

  for(var i = 0; i < arr.length; i += partLength) {
      var end = partLength + i,
          add = false;

      if(rest !== 0 && restUsed) {
          end++;
          restUsed--;
          add = true;
      }

      result.push(arr.slice(i, end));

      if(add) {
          i++;
      }
  }
  return result;
}

// Template management

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

function addIdentificationTemplate(data) {
  var identificationTemplate = document.getElementById("identification_template").innerHTML;

  var templateFn = _.template(identificationTemplate);
  var templateHTML = templateFn(data);

  $("#identification_group").append(templateHTML);
}

function addQuestionReceptionTemplate(data) {
  var questionTemplate = document.getElementById("questionReception_template").innerHTML;
  var templateFn = _.template(questionTemplate);
  var templateHTML = templateFn(data);

  $("#question_reception").append(templateHTML);
}

function addWorkGroupTemplateByIdentity(data){
  var groupTemplate = document.getElementById("flowgroup_template").innerHTML;
  var templateFn = _.template(groupTemplate);
  var templateHTML = templateFn(data);

  $("#flowdivider_by_identification").append(templateHTML);
}

function addWorkGroupTemplateByManual(data) {
  var groupTemplate = document.getElementById("group_content_manual_template").innerHTML;
  var templateFn = _.template(groupTemplate);
  var templateHTML = templateFn(data);

  $("#flowdivider_manual_groups").append(templateHTML);
}

function addFlowDividerTemplate(){
  var dividerTemplate = document.getElementById("flowdivider_options_template").innerHTML;
  var templateFn = _.template(dividerTemplate);
  var templateHTML = templateFn();

  $("#flow_divider_options").append(templateHTML);
}
// Initial Data and Config

function initialConf() {
  addIdentificationTemplate({
    temp_id : Math.random().toString(36).replace('0.', '')
  });

  // $("#order_number").hide();
  // $("#center").hide();

  $('#datetime_created_at').datetimepicker({
    locale: 'es',
    keepOpen: false
  });

  $('#datetime_sampled_at').datetimepicker({
    locale: 'es',
    keepOpen: false
  });

  $('#datetime_created_at').on("dp.change", function (e) {
    if (e.date) {
      $("#created_at_submit").val(e.date.format());
    }
  });

  $('#datetime_sampled_at').on("dp.change", function (e) {
    if (e.date) {
      $("#sampled_at_submit").val(e.date.format());
    }
  });

  $('#exam_select').select2();

  $('#customer_select').select2({
    placeholder: "Porfavor seleccione un cliente"
  });

  $('#fixtative_select').select2({
    placeholder: "Porfavor seleccione un fijador"
  });

  $('#specie_select').select2({
    placeholder: "Porfavor seleccione una especie"
  });

  $('#larvalstage_select').select2({
    placeholder: "Porfavor seleccione un estadio desarrollo"
  });

  $('#watersource_select').select2({
    placeholder: "Porfavor seleccione una fuente de agua"
  });
}

function initialData(data) {
  loadCustomers(data.customers)
  loadFixtatives(data.fixtatives)
  loadSpecies(data.species)
  loadLarvalStages(data.larvalStages)
  loadWaterSources(data.waterSources)
  loadExams(data.exams)
  // loadOrgans(data.organs)
  loadQuestions(data.questionReceptionCondition)
}

function loadCustomers(customers) {
  $.each(customers, function (i, item) {
    $('#customer_select').append($('<option>', {
      value: item.id,
      text: item.name,
      'data-type-customer': item.type_customer
    }));
  });
}

function loadFixtatives(fixtatives) {
  $.each(fixtatives, function (i, item) {
    $('#fixtative_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadSpecies(species) {
  $.each(species, function (i, item) {
    $('#specie_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadLarvalStages(larvalStages) {
  $.each(larvalStages, function (i, item) {
    $('#larvalstage_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadWaterSources(waterSources) {
  $.each(waterSources, function (i, item) {
    $('#watersource_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadExams(exams) {
  $.each(exams, function (i, item) {
    $('#exam_select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

// function loadOrgans(organs) {
//   $.each(organs, function (i, item) {
//     $('#analysis-select').append($('<option>', {
//       value: item.id,
//       text: item.name
//     }));
//   });
// }

function loadQuestions(questionReceptionCondition) {
  $("#question_reception").html("");
  $.each(questionReceptionCondition, function (i, item) {
    var data = { 'question_id': item.id, 'question_text': item.text, 'question_index': i }
    addQuestionReceptionTemplate(data);
  });
}



