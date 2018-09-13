// Data Template
var organs;

function init_step_1() {
  var url = Urls.entryform();
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      console.log("PASOOOO 1");
      initialData(data);
      initialConf();
      loadData();

      organs = data.organs;
    })
    .fail(function () {
      console.log("Fail")
    })

  // Events

  $('#customer_select').on("change", function (e) {
    var customer_type = $('#customer_select').find(':selected').data('type-customer')

    if (customer_type === 'l') {
      $("#center_input").val("");
      $("#center").hide();
      $("#order_number_input").val("")
      $("#order_number").show()
    } else if ((customer_type === 's')) {
      $("#center_input").val("");
      $("#center").show();
      $("#order_number_input").val("")
      $("#order_number").hide()
    } else {
      $("#center").hide();
      $("#order_number").hide()
    }
  });

  $('#identification_group').on("click", "#add_identification", function (e) {
    addIdentificationTemplate();
  })

  $('#identification_group').on("click", "#delete_identification", function (e) {
    $(this).closest("#identification").remove();
    refreshNoFish();
  })

  $('#identification_group').on('change', '[name="identification[no_fish]"]', function (e) {
    refreshNoFish();
  })

  $('#exam_select').on('change', function (e) {
    var selected = $(this).find("option:selected").val();
  });

  $('#exam_select').on("select2:select", function (e) {
    var analysis_name = e.params.data.text;
    var analysis_id = e.params.data.id;
    var no_fish = countNoFish();
    var analysis_organs = organs;
    var analysis_index = $(this).select2('data').length

    var templateData = {
      'analysis_id': analysis_id, 'analysis_name': analysis_name,
      'analysis_fish': no_fish, 'analysis_organs': analysis_organs,
      'analysis_index': analysis_index
    };

    addAnalysisTemplate(templateData);
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

  $('#select_if_divide_flow').on("change", function(e) {
    var if_split = $(this).val();
    $('#flow_divider_options').html("");

    if (if_split == "1"){
      if ( countNoFish() > 0 ){
        addFlowDividerTemplate();
        $('[name="identification[no_fish]"]').each(function (i, element) {
          var no_fish = parseInt($(element).val()) || 0;
          var templateData = {
            'group_size_text' : no_fish.toString()+" PECES",
            'group_count': (i+1).toString()
          };
          addWorkGroupTemplate(templateData);
        });
      } else {
        toastr.error('Es necesario completar la identificación de peces para poder subdividir el flujo de trabajo.', 'Aviso');
        $(this).find('option[value="0"]').prop('selected', true);
      }
    }
  });

  $('#exam_select').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }

    var unselected_value = e.params.args.data.id;
    $('#exam_group').find('[data-id="' + unselected_value + '"]').remove();
  });

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

        $("#exam_select").val(exams_id).trigger("change");

      })
      .fail(function () {
        console.log("Fail")
      })
  }
}


// Function for events

function countNoFish() {
  var no_fish = 0
  $('[name="identification[no_fish]"]').each(function (i, element) {
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

  $("#exam_group").append(templateHTML)
  $('[name*="analysis[organ]"]').select2();

}

function addIdentificationTemplate() {
  var identificationTemplate = document.getElementById("identification_template").innerHTML;

  var templateHTML = _.template(identificationTemplate)();

  $("#identification_group").append(templateHTML);
}

function addQuestionReceptionTemplate(data) {
  var questionTemplate = document.getElementById("questionReception_template").innerHTML;
  var templateFn = _.template(questionTemplate);
  var templateHTML = templateFn(data);

  $("#question_reception").append(templateHTML);
}

function addWorkGroupTemplate(data){
  var groupTemplate = document.getElementById("flowgroup_template").innerHTML;
  var templateFn = _.template(groupTemplate);
  var templateHTML = templateFn(data);

  $("#flowdivider_by_identification").append(templateHTML);
}

function addFlowDividerTemplate(){
  var dividerTemplate = document.getElementById("flowdivider_options_template").innerHTML;
  var templateFn = _.template(dividerTemplate);
  var templateHTML = templateFn();

  $("#flow_divider_options").append(templateHTML);
}
// Initial Data and Config

function initialConf() {
  addIdentificationTemplate();

  $("#order_number").hide();
  $("#center").hide();

  $('#datetime_created_at').datetimepicker({
    locale: 'es',
  });

  $('#datetime_sampled_at').datetimepicker({
    locale: 'es',
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
  loadOrgans(data.organs)
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

function loadOrgans(organs) {
  $.each(organs, function (i, item) {
    $('#analysis-select').append($('<option>', {
      value: item.id,
      text: item.name
    }));
  });
}

function loadQuestions(questionReceptionCondition) {
  $.each(questionReceptionCondition, function (i, item) {
    var data = { 'question_id': item.id, 'question_text': item.text, 'question_index': i }
    addQuestionReceptionTemplate(data);
  });
}



