// Data Template
var organs;

$(function () {
  var url = Urls.entryform();
  $.ajax({
    type: "GET",
    url: url,
  })
    .done(function (data) {
      initialData(data);
      initialConf();

      organs = data.organs;
    })
    .fail(function () {
      console.log("Fail")
    })

  // Events

  $('#customer_select').on("select2:select", function (e) {
    var customer_type = $('#customer_select').find(':selected').data('type_customer')

    if (customer_type === 'l') {
      $("#center_input").val("");
      $("#center").hide();
      $("#order_number_input").val("")
      $("#order_number").show()
    } else {
      $("#center_input").val("");
      $("#center").show();
      $("#order_number_input").val("")
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

  $('#exam_select').on("select2:select", function (e) {
    var analysis_name = e.params.data.text;
    var analysis_id = e.params.data.id;
    var no_fish = countNoFish();
    var analysis_organs = organs;
    var analysis_index = $(this).select2('data').length

    var templateData = {
      'analysis_id': analysis_id, 'analysis_name': analysis_name,
      'analysis_fish': no_fish, 'analysis_organs': organs,
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

  $('#exam_select').on("select2:unselecting", function (e) {
    if (e.params.args.originalEvent) {
      e.params.args.originalEvent.stopPropagation();
    }

    var unselected_value = e.params.args.data.id;
    $('#exam_group').find('[data-id="' + unselected_value + '"]').remove();
  });
});

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
      'data-type_customer': item.type_customer
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



