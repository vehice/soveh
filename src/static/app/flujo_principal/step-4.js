function init_step_4() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.analysis_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      $('.showSummaryBtn').removeClass("hidden");
      fillSummary(data);

      loadAnalysisData(data);
    })
    .fail(function () {
      console.log("Fail")
    })
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
    row.current_step = item.current_step;
    row.total_step = item.total_step;
    row.percentage_step = item.percentage_step;
    row.current_step_tag = item.current_step_tag;
    row.form_closed = item.form_closed;

    addAnalysisElement(row)
  });
}

function addAnalysisElement(data) {
  var analysisElementTemplate = document.getElementById("analysis_element").innerHTML;

  var templateFn = _.template(analysisElementTemplate);
  var templateHTML = templateFn(data);

  $("#analysis_group").append(templateHTML)
}
