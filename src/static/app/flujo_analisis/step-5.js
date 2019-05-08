function init_step_5(active = true) {
  var analysis_id = $('#analysis_id').val();
  var url = Urls.report_by_analysis(analysis_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    $('.showSummaryBtn').removeClass("hidden");
  })
  .fail(function () {
    console.log("Fail")
  })

  $('#summernote-hallazgos').summernote({
    toolbar: [
      ["style", ["style"]],
      ["font", ["bold", "underline", "clear"]],
      ["fontname", ["fontname"]],
      ["color", ["color"]],
      ["para", ["ul", "ol", "paragraph"]],
      ["table", ["table"]],
      //["insert", ["link", "picture", "video"]],
      // ["view", ["fullscreen", "codeview", "help"]]
  ],
  });

  $('#summernote-diagnosticos').summernote({
    toolbar: [
      ["style", ["style"]],
      ["font", ["bold", "underline", "clear"]],
      ["fontname", ["fontname"]],
      ["color", ["color"]],
      ["para", ["ul", "ol", "paragraph"]],
      ["table", ["table"]],
      //["insert", ["link", "picture", "video"]],
      // ["view", ["fullscreen", "codeview", "help"]]
  ],
  });
  $('#summernote-comentarios').summernote({
    toolbar: [
      ["style", ["style"]],
      ["font", ["bold", "underline", "clear"]],
      ["fontname", ["fontname"]],
      ["color", ["color"]],
      ["para", ["ul", "ol", "paragraph"]],
      ["table", ["table"]],
      //["insert", ["link", "picture", "video"]],
      // ["view", ["fullscreen", "codeview", "help"]]
  ],
  });

  $('#summernote-tablas').summernote({
    toolbar: [
      ["style", ["style"]],
      ["font", ["bold", "underline", "clear"]],
      ["fontname", ["fontname"]],
      ["color", ["color"]],
      ["para", ["ul", "ol", "paragraph"]],
      ["table", ["table"]],
      //["insert", ["link", "picture", "video"]],
      // ["view", ["fullscreen", "codeview", "help"]]
  ],
  });
  $('.table-hallazgos').find('tr:last').css('color', 'red').css('font-weight', 'bolder');
  if(!active){
    $.each($('.summernote'), function(i,v){
      $(v).summernote('disable');
    });
  }
}

function fillInputsFromSummernotes(){
  $('#box-findings').val($('#summernote-hallazgos').summernote('code'));
  $('#box-diagnostics').val($('#summernote-diagnosticos').summernote('code'));
  $('#box-comments').val($('#summernote-comentarios').summernote('code'));
  $('#box-tables').val($('#summernote-tablas').summernote('code'));
}