function init_step_4() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.slices_entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
    .done(function (data) {
      console.log(data);

      populateSliceData(data);
    })
    .fail(function () {
      console.log("Fail")
    })
}

function populateSliceData(data) {
  $.each(data.slices, function (i, item) {

    var row = {};

    row.slice_name = item.slice_name;
    row.exam_name = item.exam_name
    row.exam_stain = item.exam_stain
    row.value_step = '';
    row.current_step = '';
    row.total_step = '';

    addSliceElement(row)
  });
}

function addSliceElement(data) {
  var sliceElementTemplate = document.getElementById("slice_element").innerHTML;

  var templateFn = _.template(sliceElementTemplate);
  var templateHTML = templateFn(data);

  $("#slice_group").append(templateHTML)
}
