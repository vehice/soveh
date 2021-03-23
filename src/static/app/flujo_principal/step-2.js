var bd_correlative = 0;
var current_correlative = 0;
var organs;
var entryform;

function init_step_2() {
  var entryform_id = $('#entryform_id').val();

  var url = Urls.entryform_id(entryform_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    $('#identification_group_list').html('');
    entryform = data.entryform;
  })
  .fail(function () {
    console.log("Fail")
  });

  var table = $('#identifications').DataTable({
    "rowId": "id",
    "columnDefs": [
      {
        "targets": 0,
        "className": 'details-control',
        "orderable": false,
        "data": null,
        "render": function (data, type, row, meta) {
          return `<i class="fa fa-chevron-right fa-fx fa-2x" data-ident="${row.id}"></i>`;
        }
      },
      {

        "targets": 1, "orderable": false, "data": "correlative", "className": 'correlative-text',
        "render": function (data, type, row, meta) {
          return `${data ? data : ""}`;
        }
      },
      {
        "targets": 2, "orderable": false, "data": "cage",
        "render": function (data, type, row, meta) {
          return `<input name="cage" class="form-control-table ident-data" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 3, "orderable": false, "data": "group",
        "render": function (data, type, row, meta) {
          return `<input name="group" class="form-control-table ident-data" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 4, "orderable": false, "data": "client_case_number",
        "render": function (data, type, row, meta) {
          return `<input name="client_case_number" class="form-control-table ident-data" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 5, "orderable": false, "data": "weight",
        "render": function (data, type, row, meta) {
          return `<input name="weight" class="form-control-table ident-data" type="number" step="0.1" min="0" value="${data ? data : "0"}" >`;
        }
      },
      {
        "targets": 6, "orderable": false, "data": "extra_features_detail",
        "render": function (data, type, row, meta) {
          return `<textarea name="extra_features_detail" class="form-control-table ident-data" rows="3" > ${data ? data : ""} </textarea>`;
        }
      },
      {
        "targets": 7, "orderable": false, "data": "is_optimum",
        "render": function (data, type, row, meta) {
          return `
          <select name="is_optimum" class="form-control-table ident-data">
            <option value="1"> Sí </option>
            <option value="0" ${(data != null && !data) ? 'selected' : ''}> No </option>
          </select>
          `;
        }
      },
      {
        "targets": 8, "orderable": false, "data": "observation",
        "render": function (data, type, row, meta) {
          return `<textarea name="observation" class="form-control-table ident-data" rows="3"> ${data ? data : ""} </textarea>`;
        }
      },
      {
        "targets": 9, "orderable": false, "data": "quantity",
        "render": function (data, type, row, meta) {
          return `<input id="amount_${row.id}" name="quantity" class="form-control-table amount" type="number" data-ident="${row.id}" value="${data ? data : "0"}" min="${data ? data : ""}">`;
        }
      },
      {
        "targets": 10, "orderable": false, "data": null,
        "render": function (data, type, row, meta) {
          return `<button class="btn btn-danger deleteIdent" type="button" data-ident="${row.id}"><i class="fa fa-trash fa-fx"></i></button>`
        }
      },
    ],
    "info": false,
    "paging": false,
    "searching": false,
    "order": [[1, 'asc']]
  });

  var url = Urls.list_identification(entryform_id);
  $.ajax({
    type: "GET",
    url: url,
  })
  .done(function (data) {
    organs = data.data.organs;
    data.data.ident.forEach(element => {
      if (!element.deleted){
        addRow(element);
      }
      current_correlative = Math.max(element.correlative, current_correlative)
    });
    bd_correlative = current_correlative;
  })
  .fail(function () {
    console.log("Fail")
  });

  function format(dataRow) {
    let data = retrieveDataRow(dataRow)
    var id = data.id;
    var table_id = `units-table-${id}`
    var correlative_checked = ""
    if (data.samples_are_correlative)
      correlative_checked = "checked"
    var table_template = `
      <div class="row justify-content-center">
        <div class="form-group pl-2 pt-2">
          <input type="checkbox" id="organs-${id}" class="switch2" />
          <label for="organs-${id}" class="font-medium-1 text-bold-600 ml-1">Organos para todas las unidades</label>
        </div>
        <div class="switch-div form-group pl-2 pt-2">
          <input type="checkbox" id="correlative-${id}" class="switch2 correlative" ${correlative_checked} />
          <label for="correlative-${id}" class="font-medium-1 text-bold-600 ml-1">Correlativos</label>
        </div>
      </div>
      <table class='table w-100 table-unit' id="main-${table_id}">
      <thead> 
      <th style="width:5%">#</th> 
      <th>Tipo</th> 
      <th style="width: 65%">Órganos</th> 
      <th>Eliminar</th> 
      </thead>
      <div id="${table_id}_loading" class="text-center">
      Cargando ...
      </div>
      <tbody id="${table_id}">
      </tbody>
      </table>
    `
    var url = Urls.list_units(id);
    $.ajax({
      type: "GET",
      url: url
    })
    .done(function (response) {
      $(`#${table_id}_loading`).remove();
      $('.switchery').remove();
      var elems = $('.switch2');
      $.each(elems, function (key, value) {
        new Switchery($(this)[0], { className: 'switch2 switchery switchery-default' });
      });
      $.each(response.units, function(_, unit){
        let rows = addUnitTemplate({
          ident_id: id,
          id: unit.id,
          entry_format: entryform.entry_format[1],
          organs: organs,
          unit_correlative: unit.correlative
        });
        $(`#${table_id}`).append(rows);
        $(`#select-${id}-${unit.id}`).select2({
          templateResult: formatResultData,
          tags: true
        });
        $.each(unit.organs, function(_, org){
          selectOrgansWithConditions(org.id, org.name, id, $(`#select-${id}-${unit.id}`));
        });
      });
    })
    .fail(function () {
      console.log("Fail")
    });
    return table_template;    
  }

  function addRow(data) {
    let index = table.rows()[0].length;
    table.row.add(data).draw()
  }

  // Add event listener for opening and closing details
  $('#identifications tbody').on('click', 'td.details-control', function () {
    var tr = $(this).closest('tr');
    var icon = $($(this).children()[0]);
    var row = table.row(tr);

    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();

      icon.removeClass('fa-chevron-down');
      icon.addClass('fa-chevron-right');
      tr.removeClass('shown');
    }
    else {
      // Open this row
      row.child(format(row)).show();

      icon.removeClass('fa-chevron-right');
      icon.addClass('fa-chevron-down');
      tr.addClass('shown');
    }
  });

  $('#addIdent').on('click', function () {
    current_correlative += 1;
    var url = Urls.new_identification(entryform_id, current_correlative);
    let response
    $.ajax({
      type: "POST",
      url: url,
      async: false,
    })
    .done(function (data) {
      addRow({
        id: data.obj.id,
        correlative: data.obj.correlative
      });
    })
    .fail(function () {
      return false
    });
  });

  $(document).on('click', '.deleteIdent', function () {
    var row = table.row($(this).parents('tr'));
    var url = Urls.remove_identification($(this).data('ident'));
    swal({
      title: "Desea eliminar la identificación?",
      text: "Esta acción es permanente!",
      icon: "warning",
      showCancelButton: true,
      buttons: {
        cancel: {
          // text: "{{request.lang.cancel_case}}",
          value: null,
          visible: true,
          className: "btn-danger",
          closeModal: true,
        },
        confirm: {
          // text: "{{request.lang.next}}",
          value: true,
          visible: true,
          className: "",
          closeModal: true,
        }
      }
    }).then(isConfirm => {
      if (isConfirm) {
        remove_correlative = row.data().correlative;
        row.remove().draw();
        if (remove_correlative <= bd_correlative) {
          // OCULTAR EN BD ===> deleted = True
          $.ajax({
            type: "GET",
            url: url,
          })
            .done(function (data) {
            })
            .fail(function () {
              console.log("Fail")
            });
        }
        else {
          current_correlative--;
          table.rows().every(function (rowIdx, tableLoop, rowLoop) {
            var d = this.data();
            if (remove_correlative < d.correlative) {
              let data = retrieveDataRow(this);
              data.correlative--;
              this
                .data(data)
                .draw();
            }
          });
        }
      }
    });

  });

  $(document).on('click', '.unit-delete', function (e) {
    let id = $(this).data('id')
    let ident_id = $(this).data('ident')
    swal({
      title: "Desea eliminar la unidad?",
      text: "Esta acción es permanente!",
      icon: "warning",
      showCancelButton: true,
      buttons: {
        cancel: {
          // text: "{{request.lang.cancel_case}}",
          value: null,
          visible: true,
          className: "btn-danger",
          closeModal: true,
        },
        confirm: {
          // text: "{{request.lang.next}}",
          value: true,
          visible: true,
          className: "",
          closeModal: true,
        }
      }
    }).then(isConfirm => {
      if (isConfirm) {
        let url = Urls.remove_unit(id)
        $.ajax({
          type: "POST",
          url: url,
          async: false,
        })
        .done(function (data) {
          if (data.ok){
            let amount_control = $(`#amount_${ident_id}`)
            let new_value = amount_control.val() - 1
            amount_control[0].min = new_value
            amount_control[0].defaultValue = new_value
            amount_control.val(new_value)
            saveIdentification(ident_id)
            $("#unit-"+ident_id+"-"+id).remove()
            toastr.success(
              'Unidad eliminada exitosamente.',
              'Listo!',
            )
        } else {
            toastr.error(
              'No ha sido posible eliminar la unidad, intente nuevamente.',
              'Ups!',
            )
          }
        })
        .fail(function () {
          toastr.error(
            'No ha sido posible eliminar la unidad, intente nuevamente.',
            'Ups!',
          )
        })
      }
    })
  })

  $(document).on('change', '.form-control-table.amount', function (e, param1) {
    lockScreen(1);
    if (this.defaultValue == this.value)
      return;

    var direction = parseInt(this.defaultValue) < parseInt(this.value)

    var id = $(this).data('ident');
    let table_id = `units-table-${id}`;
    if (direction) {
      let data_saved = false
      
      for (let i = parseInt(this.defaultValue) + 1; i <= parseInt(this.value); i++) {
        let result_ident = saveIdentification(id)
        
        if (result_ident.ok){
          let last_tr_pos = parseInt(this.defaultValue)-1          
          let res = getUnits(id)
          
          if (res.ok){
            let units_correlatives = []
            res.units.forEach(function(u){
              units_correlatives.push(u.correlative);
            });
            let max_corr = units_correlatives.length > 0 ? Math.max(...units_correlatives) : 0
            let result_unit = createUnit(id, max_corr + 1)
            
            if (result_unit.ok) {
              let unit = result_unit.unit
              
              let rows = addUnitTemplate({
                ident_id: unit.identification,
                id: unit.id,
                entry_format: entryform.entry_format[1],
                organs:organs,
                unit_correlative: unit.correlative
              });

              $(`#${table_id}`).append(rows);
              
              $(`#select-${id}-${unit.id}`).select2({
                templateResult: formatResultData,
                tags: true
              });

              data_saved = true
            }
          }          
        }
      }
      if (data_saved){
        this.defaultValue = this.value
      }
    }
    else {
      this.value = this.defaultValue;
    }
    lockScreen(0);
  });

  $(document).on("select2:selecting", ".organs", function (e) {
    e.preventDefault();

    let new_id = `${e.params.args.data.id}`;
    let new_value = e.params.args.data.text;
    let ident_id = e.target.id.split("-")[1];
    let select = e.target

    selectOrgansWithConditions(new_id, new_value, ident_id, $(select));
    saveUnitsByIdentification(ident_id)

  });

  $(document).on("select2:unselect", ".organs", function (e) {
    if (e.params.data.id.search('-') != -1) {
      e.params.data.element.remove();
    }
    let ident_id = e.target.id.split("-")[1];
    saveUnitsByIdentification(ident_id)
  });

  $(document).on("change", ".correlative", function (e) {
    let id = e.target.id.split('-')[1];
    if (e.target.checked) {
      swal({
        title: "Organos en correlativos",
        text: "Se eliminarán los órganos repetidos",
        icon: "warning",
        showCancelButton: true,
        buttons: {
          cancel: {
            value: null,
            visible: true,
            className: "btn-danger",
            closeModal: true,
          },
          confirm: {
            value: true,
            visible: true,
            className: "",
            closeModal: true,
          }
        }
      }).then(isConfirm => {
        if (!isConfirm) {
          e.target.click();
          return;
        }
        resetOrgansOptions(id, true);
      });
    }
    else {
      resetOrgansOptions(id, false);
    }
    saveIdentification(id)
    saveUnitsByIdentification(id)
  });

  $(document).on("blur", ".ident-data", function () {
    let id = $(this).parent().parent().attr("id")
    saveIdentification(id)
  });

  $(document).on("change", ".unit-correlative", function (e, param1) {
    let correlative_input = this
    let ident_id = $(correlative_input).attr("id").split("-")[1]
    let current_unit_id = $(correlative_input).attr("id").split("-")[2]

    let current_correlative_value = correlative_input.value
    let current_default_value = correlative_input.defaultValue
    
    let correlative_switch_option = $('#correlative-'+ident_id).is(":checked")

    if (correlative_switch_option){
      if (checkDuplicatedOrgansInSameCorrelative(ident_id, current_unit_id)){
        correlative_input.value = current_default_value
        alertDuplicatedOrgansInSameCorrelative()
      } else {
        correlative_input.defaultValue = current_correlative_value
        saveUnitsByIdentification(ident_id)
      }
    } else {
      correlative_input.defaultValue = current_correlative_value;
      saveUnitsByIdentification(ident_id)
    }
  })
}

function alertDuplicatedOrgansInSameCorrelative(){
  swal({
    title: "Información",
    text: "No ha sido posible realizar el cambio debido a que existe duplicidad de órganos en muestra correlativa.",
    icon: "warning",
    showCancelButton: false,
  }); 
}

function checkDuplicatedOrgansInSameCorrelative(ident_id, unit_id, organs_selected=false){
  let current_correlative = $("#input-"+ident_id+"-"+unit_id).val()
  if (!organs_selected){
    var organs_selected = $("#select-"+ident_id+"-"+unit_id).val()
  }

  let organs_validator = false;
  $.each( $("#units-table-"+ident_id+" tr"), function (i, tr) {
    let tr_unit_id = $(tr).attr("id").split("-")[2]
    let tr_correlative_value = $(tr).find(".unit-correlative").val()
    if (unit_id != tr_unit_id && current_correlative == tr_correlative_value){
      let tr_organs_selected = $(tr).find(".organs").val()
      if (organs_selected.some(r=> tr_organs_selected.indexOf(r) >= 0)){
        organs_validator = true
        return false
      }
    }
  });
  return organs_validator
}

function addUnitTemplate(data) {
  var unitTemplate = document.getElementById("unit_template").innerHTML;

  var templateFn = _.template(unitTemplate);
  var templateHTML = templateFn(data);
  return templateHTML;
}

function retrieveDataRow(row) {
  var data = row.data();

  $.each($(`#${data.id} .form-control-table`), function (i, v) {
    data[v.name] = v.value;
  });

  return data;
}

/*** Select organs based on switches values (organs for all and correlative samples) ***/
function selectOrgansWithConditions(new_id, new_value, ident_id, select){
  let organs_switch_option = $('#organs-'+ident_id).is(":checked")
  let correlative_switch_option = $('#correlative-'+ident_id).is(":checked")

  if ( organs_switch_option ) {
    $.each( $("#units-table-"+ident_id+" .organs"), function (i, v) {
      let select = $(v)
      let unit_id = select.attr("id").split("-")[2]
      let values = select.val()

      if ( !correlative_switch_option ) {
        new_id = `${new_id}-${Math.random()}`
        select.append(`<option value="${new_id}">${new_value}</option>`)
        values.push(new_id)
        select.val(values)
        select.trigger('change')
      } else {
        values.push(new_id)
        if (!checkDuplicatedOrgansInSameCorrelative(ident_id, unit_id, values)){
          select.val(values)
          select.trigger('change')
        } else {
          alertDuplicatedOrgansInSameCorrelative()
        }
      }
    })
  } else {
    let values = select.val();
    let unit_id = select.attr("id").split("-")[2]
    if ( !correlative_switch_option ) {
      new_id = `${new_id}-${Math.random()}`;
      select.append(`<option value="${new_id}">${new_value}</option>`);
      values.push(new_id)
      select.val(values)
      select.trigger('change')
    } else {
      values.push(new_id)
      if (!checkDuplicatedOrgansInSameCorrelative(ident_id, unit_id, values)){
        select.val(values)
        select.trigger('change')
      } else {
        alertDuplicatedOrgansInSameCorrelative()
      }
    
    }
  }
}

function resetOrgansOptions(id, correlative) {
  var unitTemplate = document.getElementById("organos_options").innerHTML;
  var templateFn = _.template(unitTemplate);
  var templateHTML = templateFn({ organs });

  $.each($(`.organs-${id}`), function (i, v) {
    let select = $(v)
    let values = select.val()
    let selected = []

    values.forEach(element => {
      let x = element.split('-')[0];
      if (selected.indexOf(x) == -1) {
        selected.push(x);
      }
    });

    select.html(templateHTML)

    if (correlative) {
      select.val(selected).trigger('change')
    } else {
      let selected_unique = []
      selected.forEach(element => {
        let new_id = `${element}-${Math.random()}`;
        let new_value = select.find("option[value='"+element+"']").text();
        select.append(`<option value="${new_id}">${new_value}</option>`);
        selected_unique.push(new_id);
      });
      select.val(selected_unique).trigger('change')
    }
  });
}

function formatResultData(data) {
  if (!data.id) return data.text;
  if (data.element.selected) return
  return data.text;
};

function validate_step_2() {
  let sucess = 1;
  $.each($('input[name=no_container]'), function (i, v) {
    if ($(v).val() <= 0) {
      sucess = 0;

    }
  });
  if (!sucess) {
    toastr.error(
      'Para continuar todas las cantidades deben ser mayores a 0.',
      'Ups!',
      { positionClass: 'toast-top-full-width', containerId: 'toast-bottom-full-width' }
    );
  }
  return sucess;
}

function openOrgansKeypad(ident_id, index){
  var organs_keypad_template = document.getElementById("organs_keypad").innerHTML;
  var templateFn = _.template(organs_keypad_template);

  var data = {
    'ident_id': ident_id,
    'index': index,
    'organs': organs
  }

  var templateHTML = templateFn({ data });
  $("#organ_table_keypad_body").html(templateHTML);
  $("#organ_table_keypad").modal("show");
}

function AddOrgansFromKeypadToSelect(ident_id, index){
  
  let organs_selected_from_keypad = [];
  $('input[name="organs-keypad-checkbox[]"]').each(function (e) {
    if ($(this).is(":checked")) {
      organs_selected_from_keypad.push([$(this).data("id"), $(this).data("name")])
    }   
  });

  let organs_selector = '#select-'+ident_id+'-'+index;

  $.each(organs_selected_from_keypad, function(index, value){
    selectOrgansWithConditions(value[0], value[1], ident_id, $(organs_selector))
  });

  saveUnitsByIdentification(ident_id)

  $("#organ_table_keypad").modal("hide");
  
}

function createUnit(identification_id, correlative){
  let url = Urls.create_unit(identification_id, correlative)
  let response
  $.ajax({
    type: "POST",
    url: url,
    async: false,
  })
  .done(function (data) {
    response = data
  })
  .fail(function () {
    reponse = {ok: 0}
  });

  return response; 
}

function saveIdentification(id){
  let url = Urls.save_new_identification(id)
  let ident = retrieveDataRow( $("#identifications").DataTable().row($('#'+id)))
  ident["samples_are_correlative"] = $('#correlative-'+id).is(":checked") ? 1 : 0

  let response
  $.ajax({
    type: "POST",
    url: url,
    async: false,
    data: ident
  })
  .done(function (data) {
    response = data
  })
  .fail(function () {
    reponse = {ok: 0}
  });
  return response; 
}

function saveUnitsByIdentification(ident_id){
  let units = []
  $.each( $("#units-table-"+ident_id+" tr"), function (i, tr) {
    let unit = {}
    unit['id'] = $(tr).attr("id").split("-")[2]
    unit['correlative'] = $("#input-"+ident_id+"-"+unit['id']).val()
    unit['organs'] = $("#select-"+ident_id+"-"+unit['id']).val()
    units.push(unit)
  });

  let url = Urls.save_units()
  let response
  $.ajax({
    type: "POST",
    url: url,
    async: false,
    data: {'units': JSON.stringify(units)}
  })
  .done(function (data) {
    response = data
  })
  .fail(function () {
    reponse = {ok: 0}
  });
  return response; 


}

function getUnits(ident_id){
  let url = Urls.list_units(ident_id)
  let response
  $.ajax({
    type: "GET",
    url: url,
    async: false
  })
  .done(function (data) {
    response = data
  })
  .fail(function () {
    response = {ok:0}
  })
  return response
}