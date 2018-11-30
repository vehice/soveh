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

      loadCassetteTable(data_step_2);
      loadData(data_step_2);
    })
    .fail(function () {
    })

  $('#datetime_processor_loaded_at').datetimepicker({
    locale: 'es',
  });

  $('#datetime_processor_loaded_at').on("dp.change", function (e) {
    if (e.date) {
      $("#processor_loaded_at_submit").val(e.date.format());
    }
  });

  function loadData(data) {
    var entryform = data.entryform;
    if (entryform.cassettes.length > 0) {
      var nro_fish_total = _.sumBy(entryform.identifications, 'no_fish');
      var nro_cassette = entryform.cassettes.length
      var nro_sample_cassette = nro_cassette / nro_fish_total;

      $('[name="processor_loaded_at"]').val(moment(entryform.cassettes[0].processor_loaded_at).format("DD/MM/YYYY HH:MM") || "");
      $('#processor_loaded_at_submit').val(entryform.cassettes[0].processor_loaded_at);

      $("#no_cassette").val(nro_sample_cassette)
    } else {
      $('[name="processor_loaded_at"]').val("");
      $('#processor_loaded_at_submit').val("");

      $("#no_cassette").val(1)
    }

    $.each(entryform.cassettes, function (i, item) {
      $('div[attr1="value1"][attr2="value2"]')
      $("#cassettes_table")
        .find("[data-sample-id='" + item.sample_id + "'][data-cassette-name='" + item.cassette_name + "']")
        .val(item.organs).trigger("change");
    });
  };
}

$(document).on('change', '#no_cassette', function (e) {
  loadCassetteTable(data_step_2);
})

$(document).on('click', '.remove_cassette', function (e) {
  var cassette_index = $(this).data('cassette');
  $('#cassettes_table tr:eq('+(cassette_index + 1)+')').remove();

  var table_size = $('#cassettes_table tr').length;
  for (i = cassette_index + 1; i < table_size; i++) {
    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[identification_id]"]')
      .prop('name', 'cassette[identification_id]['+(i-1).toString()+']');

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[sample_id]"]')
      .prop('name', 'cassette[sample_id]['+(i-1).toString()+']');

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[sample_no]"]')
      .prop('name', 'cassette[sample_no]['+(i-1).toString()+']')
      .val(i);

    $('#cassettes_table tr:eq('+i+')')
      .find('select[name*="cassette[organ]"]')
      .prop('name', 'cassette[organ]['+(i-1).toString()+']').select2();

    var cassette_name = $('#cassettes_table tr:eq('+(i-1)+')')
      .find('input[name*="cassette[cassette_name]"]')
      .val();

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[cassette_name]"]')
      .prop('name', 'cassette[cassette_name]['+(i-1).toString()+']')
      .val(cassette_name.replace('C'+(i-1).toString(), 'C'+(i).toString()));

    $('#cassettes_table tr:eq('+i+') td:eq(1)')
      .text(cassette_name.replace('C'+(i-1).toString(), 'C'+(i).toString()));
  }
  toastr.success('Cassette eliminado correctamente.', 'Listo!');
});

$(document).on('click', '.add_cassette_to_sample', function (e) {
  var parent_tr = $(this).closest('tr');
  parent_tr.find('select[name*="cassette[organ]"]').select2('destroy');
  var clone_tr = parent_tr.clone();
  var current_cassette_index = parseInt($(this).data('cassette'));
  var new_cassette_index = current_cassette_index + 1;

  clone_tr.find("input[name*='cassette[identification_id]["+current_cassette_index+"]']").
    prop('name', 'cassette[identification_id]['+new_cassette_index+']');
  clone_tr.find("input[name*='cassette[sample_id]["+current_cassette_index+"]']").
    prop('name', 'cassette[sample_id]['+new_cassette_index+']');
  clone_tr.find("input[name*='cassette[sample_no]["+current_cassette_index+"]']").
    prop('name', 'cassette[sample_no]['+new_cassette_index+']');
  clone_tr.find("input[name*='cassette[cassette_name]["+current_cassette_index+"]']").
    prop('name', 'cassette[cassette_name]['+new_cassette_index+']');
  clone_tr.find(".add_cassette_to_sample").remove();
  clone_tr.find('td:eq(3)').append('<button title="Eliminar Cassette" tooltip="" type="button" data-cassette="'+new_cassette_index+'" class="btn btn-icon btn-danger remove_cassette"><i class="fa fa-trash"></i></button>');
  clone_tr.insertAfter(parent_tr);
  clone_tr.addClass("bg-success bg-accent-1");
  parent_tr.find('select[name*="cassette[organ]"]').select2();

  var new_index = clone_tr.index();
  var table_size = $('#cassettes_table tr').length;
  
  for (i = new_index + 1; i < table_size; i++) { 
    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[identification_id]"]')
      .prop('name', 'cassette[identification_id]['+(i-1).toString()+']');

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[sample_id]"]')
      .prop('name', 'cassette[sample_id]['+(i-1).toString()+']');

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[sample_no]"]')
      .prop('name', 'cassette[sample_no]['+(i-1).toString()+']')
      .val(i);

    $('#cassettes_table tr:eq('+i+')')
      .find('select[name*="cassette[organ]"]')
      .prop('name', 'cassette[organ]['+(i-1).toString()+']').select2();

    var cassette_name = $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[cassette_name]"]')
      .val();

    $('#cassettes_table tr:eq('+i+')')
      .find('input[name*="cassette[cassette_name]"]')
      .prop('name', 'cassette[cassette_name]['+(i-1).toString()+']')
      .val(cassette_name.replace('C'+(i-1).toString(), 'C'+(i).toString()));

    $('#cassettes_table tr:eq('+i+') td:eq(1)')
      .text(cassette_name.replace('C'+(i-1).toString(), 'C'+(i).toString()));
  }

  toastr.success('Se asignó un nuevo cassette exitosamente.', 'Listo!');
});

function loadCassetteTable(data) {
  // var no_cassette = 1;

  if ($.fn.DataTable.isDataTable('#cassettes_table')) {
    // TODO: Fix efecto al destruir la tabla
    $('#cassettes_table').DataTable().clear().destroy();
  }

  populateCassetteTable(data);

  $('#cassettes_table').DataTable({
    ordering: false,
    paginate: false,
    columnDefs: [
      { "width": "20%", "targets": 0 },
      { "width": "20%", "targets": 1 },
      { "width": "60%", "targets": 2 }
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
  });

  $('[name*="cassette[organ]"]').select2();
  $('[name*="cassette[organ]"] > option').prop('selected', 'selected');
  $('[name*="cassette[organ]"]').trigger('change');
}

function populateCassetteTable(data) {
  var organs = data.organs;
  var cassette_index = 0;
  var fish_count_start = 1;
  $.each(data.identifications, function (i, item) {
    var identification_id = item.id;

    var array_index = _.range(fish_count_start, fish_count_start + item.no_fish);

    var id_muestra = data.entryform.no_caso + '-' + item.cage + '-' + item.group;
    // fish_count_start = fish_count_start + 1;

    $.each(array_index, function (j, item2) {
      fish_count_start = fish_count_start + 1;
      var row = {};

      row.identification_id = identification_id;
      row.sample_id = id_muestra + "-M" + (j+1).toString();
      row.sample_no = item2;
      if ( data.entryform.subflow != "N/A" ){
        row.cassette_name = data.entryform.no_caso + '-' + data.entryform.subflow + '_C' + item2;
      } else {
        row.cassette_name = data.entryform.no_caso + '_C' + item2;
      }
      row.cassette_organs = organs;
      row.cassette_index = cassette_index;

      cassette_index += 1;

      addCasseteRow(row)
    });
  });
}

function addCasseteRow(data) {
  var cassetteRowTemplate = document.getElementById("cassette_row").innerHTML;

  var templateFn = _.template(cassetteRowTemplate);
  var templateHTML = templateFn(data);

  $("#cassettes_table tbody").append(templateHTML)
}
