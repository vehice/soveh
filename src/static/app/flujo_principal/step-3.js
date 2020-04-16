var data_step_3;

function init_step_3() {
  var entryform_id = $('#entryform_id').val();
  var url = Urls.entryform_id(entryform_id);

  $.ajax({
    type: "GET",
    url: url,
    async: false,
  })
  .done(function (data) {
    // console.log(data)
    data_step_3 = data
    $('.showShareBtn').removeClass("hidden");
    $('.showLogBtn').removeClass("hidden");
    $('.showSummaryBtn').removeClass("hidden");
    $('.newAnalysisBtn').addClass("hidden");
    $('.newAnalysisBtn5').addClass("hidden");
    // fillSummary(data);

    if ($.fn.DataTable.isDataTable('#cassettes_table')) {
      // TODO: Fix efecto al destruir la tabla
      $('#cassettes_table').DataTable().clear().destroy();
    }

    loadCassetteData(data_step_3);

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
    // $('[name*="cassette[organ]"] > option').prop('selected', 'selected');
    $('[name*="cassette[organ]"]').trigger('change');
    
    $('[name*="cassette[organ]"]').on("select2:unselecting", function (e) {
      if (e.params.args.originalEvent) {
        e.params.args.originalEvent.stopPropagation();
      }
    });
  })
  .fail(function () {
  })

  $('#datetime_processor_loaded_at').datetimepicker({
    locale: 'es',
    keepOpen: false,
    format:'DD/MM/YYYY HH:mm'
  });

  // $('#datetime_processor_loaded_at').on("dp.change", function (e) {
  //   if (e.date) {
  //     $("#processor_loaded_at_submit").val(e.date.format());
  //   }
  // });
}

function validate_step_3(){  
  // Validates date
  if ( $('#processor_loaded_at').val() == "") {
    toastr.error(
      'Para continuar debes ingresar la fecha y hora del procesado de tejido.', 
      'Ups!', 
      {positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width'}
    );
    $('#processor_loaded_at').focus();
    return false;
  }
  return true;
}

$(document).on('click', '.remove_cassette', function (e) {
  var cassette_index = $(this).data('cassette');
  $('#cassettes_table tr:eq('+(cassette_index)+')').remove();

  var table_size = $('#cassettes_table tr').length;

  for (i = cassette_index; i < table_size; i++) {
    
    old_index = i + 1;

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[sample_id]["+old_index+"]']").
      prop('name', 'cassette[sample_id]['+i+']');

    $('#cassettes_table tr:eq('+i+')').find("select[name*='cassette[organ]["+old_index+"]']").
      prop('name', 'cassette[organ]['+i+']');

    current_cassette_name = $('#cassettes_table tr:eq('+i+')').find("td:eq(2)").text();
    new_cassette_name = $.trim(
      current_cassette_name.replace('C'+old_index.toString(), 
        'C'+(i).toString()
      )
    );

    $('#cassettes_table tr:eq('+i+')').find("td:eq(2)").
      text(new_cassette_name);

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[cassette_name]["+old_index+"]']").
      prop('name', 'cassette[cassette_name]['+i+']');

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[cassette_name]["+i+"]']").
      val(new_cassette_name);

    $('#cassettes_table tr:eq('+i+')').find('.add_cassette_to_sample').
      attr('data-cassette', i);

  }
  toastr.success('Cassette eliminado correctamente.', 'Listo!');
});

$(document).on('click', '.add_cassette_to_sample', function (e) {
  var parent_tr = $(this).closest('tr');
  parent_tr.find('select[name*="cassette[organ]"]').select2('destroy');
  var clone_tr = parent_tr.clone();
  var current_cassette_index = parseInt($(this).data('cassette'));
  var new_cassette_index = current_cassette_index + 1;
  
  clone_tr.find("input[name*='cassette[sample_id]["+current_cassette_index+"]']").
    prop('name', 'cassette[sample_id]['+new_cassette_index+']');

  clone_tr.find("select[name*='cassette[organ]["+current_cassette_index+"]']").
    prop('name', 'cassette[organ]['+new_cassette_index+']');

  current_cassette_name = clone_tr.find("td:eq(2)").text();
  new_cassette_name = $.trim(
    current_cassette_name.replace('C'+current_cassette_index.toString(), 
      'C'+(new_cassette_index).toString()
    )
  );
  clone_tr.find("td:eq(2)").
    text(new_cassette_name);

  clone_tr.find("input[name*='cassette[cassette_name]["+current_cassette_index+"]']").
    prop('name', 'cassette[cassette_name]['+new_cassette_index+']');

  clone_tr.find("input[name*='cassette[cassette_name]["+new_cassette_index+"]']").
  val(new_cassette_name);


  clone_tr.find(".add_cassette_to_sample").remove();
  clone_tr.find('td:eq(4)').append('<button title="Eliminar Cassette" tooltip="" type="button" data-cassette="'+new_cassette_index+'" class="btn btn-icon btn-danger remove_cassette"><i class="fa fa-trash"></i></button>');
  clone_tr.insertAfter(parent_tr);
  clone_tr.addClass("bg-success bg-accent-1");
  parent_tr.find('select[name*="cassette[organ]"]').select2();
  clone_tr.find('select[name*="cassette[organ]"]').find('option').prop('selected', 'selected').end().select2();

  var new_index = clone_tr.index() + 1;
  var table_size = $('#cassettes_table tr').length;

  for (i = new_index + 1; i < table_size; i++) {
    
    old_index = i - 1;

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[sample_id]["+old_index+"]']").
      prop('name', 'cassette[sample_id]['+i+']');

    $('#cassettes_table tr:eq('+i+')').find("select[name*='cassette[organ]["+old_index+"]']").
      prop('name', 'cassette[organ]['+i+']');

    current_cassette_name = $('#cassettes_table tr:eq('+i+')').find("td:eq(2)").text();
    new_cassette_name = $.trim(
      current_cassette_name.replace('C'+old_index.toString(), 
        'C'+(i).toString()
      )
    );

    $('#cassettes_table tr:eq('+i+')').find("td:eq(2)").
      text(new_cassette_name);

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[cassette_name]["+old_index+"]']").
      prop('name', 'cassette[cassette_name]['+i+']');

    $('#cassettes_table tr:eq('+i+')').find("input[name*='cassette[cassette_name]["+i+"]']").
      val(new_cassette_name);

    $('#cassettes_table tr:eq('+i+')').find('.add_cassette_to_sample').
      attr('data-cassette', i);
  }

  toastr.success('Se asignó un nuevo cassette exitosamente.', 'Listo!');

});

function loadCassetteData(data) {
  if (data.entryform.cassettes.length > 0){
    $('[name="processor_loaded_at"]').val(moment(data.entryform.cassettes[0].processor_loaded_at).format("DD/MM/YYYY HH:mm") || "");
    $('#processor_loaded_at_submit').val(data.entryform.cassettes[0].processor_loaded_at);

    $.each(data.samples, function (i, sample) {
      $.each(sample.cassettes_set, function (j, cassette) {
        var row = {
          'sample_id' : sample.id,
          'sample_index' : sample.index,
          'cassette_index' : cassette.index,
          'cassette_name' : cassette.cassette_name,
          'sample_name' : sample.identification.cage+'-'+sample.identification.group,
          'organs': sample.organs_set
        };
        addCasseteRow(row);
        $.each(cassette.organs_set, function(i, item){
          $('#cassette-organ-'+cassette.index+' option[value="'+item.id+'"]').prop('selected', true);
        });
      });
    });   
  } else {

    $('[name="processor_loaded_at"]').val("");
    $('#processor_loaded_at_submit').val("");

    cassette_preffix = "";
    if ( data.entryform.subflow != "N/A" ){
      cassette_preffix = data.entryform.no_caso + '-' + data.entryform.subflow + '_C';
    } else {
      cassette_preffix = data.entryform.no_caso + '_C';
    }
    var exams = 0;
    $.each(data.samples, function (i, sample) {
      if(sample.organs_set.length > 0){
        // if (sample.)
        var row = {
          'sample_id' : sample.id,
          'sample_index' : sample.index,
          'cassette_index' : sample.index,
          'cassette_name' : cassette_preffix + '' +sample.index,
          'sample_name' : sample.identification.cage+'-'+sample.identification.group,
          'organs': sample.organs_set
        };
        addCasseteRow(row);
        $.each( $('#cassette-organ-'+sample.index+' > option'), function(i, item){
          $(item).prop('selected', true);
        });
        exams+=1;
      }
    });  
    if(!exams){
      
    }
  }
}

function addCasseteRow(data) {
  var cassetteRowTemplate = document.getElementById("cassette_row").innerHTML;

  var templateFn = _.template(cassetteRowTemplate);
  var templateHTML = templateFn(data);

  $("#cassettes_table tbody").append(templateHTML)
}
