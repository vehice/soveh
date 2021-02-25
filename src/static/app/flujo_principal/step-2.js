bd_correlative = 0;
current_correlative = 0;
organs;

function init_step_2() {
  var entryform_id = $('#entryform_id').val();

  var table = $('#identifications').DataTable({
    "rowId": "id",
    "columnDefs": [
      {
        "targets": 0,
        "className": 'details-control',
        "orderable": false,
        "data": null,
        "render": function (data, type, row, meta) {
          return `<i class="fa fa-chevron-right fa-fx" data-ident="${row.id}"></i>`;
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
          return `<input name="cage" class="form-control-table" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 3, "orderable": false, "data": "group",
        "render": function (data, type, row, meta) {
          return `<input name="group" class="form-control-table" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 4, "orderable": false, "data": "group",
        "render": function (data, type, row, meta) {
          return `<input name="_group" class="form-control-table" value="${data ? data : ""}" >`;
        }
      },
      {
        "targets": 5, "orderable": false, "data": "weight",
        "render": function (data, type, row, meta) {
          return `<input name="weight" class="form-control-table" type="number" step="0.1" min="0" value="${data ? data : "0"}" >`;
        }
      },
      {
        "targets": 6, "orderable": false, "data": "extra_features_detail",
        "render": function (data, type, row, meta) {
          return `<textarea name="extra_features_detail" class="form-control-table" rows="3" > ${data ? data : ""} </textarea>`;
        }
      },
      {
        "targets": 7, "orderable": false, "data": "is_optimum",
        "render": function (data, type, row, meta) {
          return `
          <select name="is_optimum" class="form-control-table">
            <option value="1"> Sí </option>
            <option value="0" ${(data != null && !data) ? 'selected' : ''}> No </option>
          </select>
          `;
        }
      },
      {
        "targets": 8, "orderable": false, "data": "observation",
        "render": function (data, type, row, meta) {
          return `<textarea name="observation" class="form-control-table" rows="3"> ${data ? data : ""} </textarea>`;
        }
      },
      {
        "targets": 9, "orderable": false, "data": "no_container",
        "render": function (data, type, row, meta) {
          return `<input id="amount_${row.id}" name="no_container" class="form-control-table amount" type="number" data-ident="${row.id}" value="${data ? data : "0"}" min="${data ? data : ""}">`;
        }
      },
      {
        "targets": 10, "orderable": false, "data": null,
        "render": function (data, type, row, meta) {
          return `<button class="btn btn-danger btn-sm deleteIdent" type="button" data-ident="${row.id}"><i class="fa fa-trash fa-fx"></i></button>`
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
        if (!element.deleted)
          addRow(element);
        current_correlative = Math.max(element.correlative, current_correlative)
      });
      bd_correlative = current_correlative;
    })
    .fail(function () {
      console.log("Fail")
    });

  function format(dataRow) {
    let data = retrieveDataRow(dataRow)
    let id = data.id;
    // color: #ffffff; background-color: #63d0ba; border: none
    let table_id = `units-table-${id}` // hay que linkearlo a la funcion ajax
    let table_template = `
    <div class="row justify-content-center">
      <div class="form-group pl-2 pt-2">
        <input type="checkbox" id="organs-${id}" class="switch2" />
        <label for="organs-${id}" class="font-medium-1 text-bold-600 ml-1">Organos para todas las unidades</label>
      </div>
      <div class="switch-div form-group pl-2 pt-2">
        <input type="checkbox" id="correlative-${id}" class="switch2 correlative" />
        <label for="correlative-${id}" class="font-medium-1 text-bold-600 ml-1">Correlativos</label>
      </div>
    </div>
    <table class='table w-100 table-unit'>
    <thead> 
    <th style="width:5%">#</th> 
    <th>Tipo</th> 
    <th style="width: 50%">Organos</th> 
    <th>Eliminar</th> 
    </thead>
    <div id="${table_id}_loading" class="text-center">
    Cargando ...
    </div>
    <tbody id="${table_id}">
    </tbody>
    </table>
    `
    let table = $(table_template);
    setTimeout(function () { //sustituir por una funcion ajax && ver en que punto guardar datos
      $(`#${table_id}_loading`).remove();
      $('.switchery').remove();
      var elems = $('.switch2');
      $.each(elems, function (key, value) {
        new Switchery($(this)[0], { className: 'switch2 switchery switchery-default' });
      });
      for (let index = 0; index < data.no_container; index++) {
        let rows = addUnitTemplate({
          ident_id: id,
          index: index,
          organs
        });
        $(`#${table_id}`).append(rows);
        $(`#select-${id}-${index}`).select2({
          templateResult: formatResultData,
          tags: true
        });
      }
    }, 1000)
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
    var url = Urls.new_identification(entryform_id);
    current_correlative += 1;
    addRow({
      id: `new_${current_correlative}`,
      correlative: current_correlative
    });

    // $.ajax({
    //   type: "GET",
    //   url: url,
    // })
    //   .done(function (data) {
    //     addRow(data.obj);
    //   })
    //   .fail(function () {
    //     console.log("Fail")
    //   });
  });

  $(document).on('click', '.deleteIdent', function () {
    var row = table.row($(this).parents('tr'));
    var url = Urls.remove_identification($(this).data('ident'));
    swal({
      title: "Desea borrar la identificación??",
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
    let id = $(this).data('ident');
    let amount_control = $(`#amount_${id}`);
    let new_value = amount_control.val() - 1;
    amount_control[0].min = new_value;
    amount_control.val(new_value);
    $(this).parent().parent().remove();
    amount_control.trigger('change', [true]);
  });

  $(document).on('change', '.form-control-table.amount', function (e, param1) {
    if (this.defaultValue == this.value)
      return;

    var direction = this.defaultValue < this.value
    this.defaultValue = this.value;

    let id = $(this).data('ident');
    let table_id = `units-table-${id}`;
    if (direction) {
      // Increase
      let rows = addUnitTemplate({
        ident_id: id,
        index: this.value
      });
      $(`#${table_id}`).append(rows);
      $(`#select-${id}-${this.value}`).select2({
        templateResult: formatResultData,
        tags: true
      });
    }
    else {
      if (!param1)
        $(`#${table_id} > tr:last`).remove();
    }
  });

  $(document).on('blur', '.form-control-table.amount', function () {
    this.min = this.value;
  });
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

$(document).on("select2:selecting", function (e) {
  let correlative_btn = '#correlative-2346';
  let new_id = `${e.params.args.data.id}`;
  let new_value = e.params.args.data.text;
  if (!$(correlative_btn)[0].checked) {
    new_id = `${e.params.args.data.id}-${Math.random()}`;
    new_value = e.params.args.data.text;
  }
  if ($('#organs-2346')[0].checked) {
    $.each($('#units-table-2346 .organs'), function (i, v) {
      let select = $(v);
      if (!$(correlative_btn)[0].checked) {
        select.append(`<option value="${new_id}">${new_value}</option>`);
      }
      let values = select.val()
      values.push(new_id);
      console.log(values);
      select.val(values);
      select.trigger('change');
    });
    e.preventDefault();
  }
  else {
    let select = $(e.target);
    if (!$(correlative_btn)[0].checked) {
      select.append(`<option value="${new_id}">${new_value}</option>`);
    }
    let values = select.val()
    values.push(new_id);
    console.log(values);
    select.val(values);
    select.trigger('change');
    e.preventDefault();
  }
});

$(document).on("select2:unselect", function (e) {
  if (e.params.data.id.search('-') != -1) {
    e.params.data.element.remove();
  }
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
});

function resetOrgansOptions(id, correlative) {
  var unitTemplate = document.getElementById("organos_options").innerHTML;
  var templateFn = _.template(unitTemplate);
  var templateHTML = templateFn({ organs });

  $.each($(`.organs-${id}`), function (i, v) {
    let select = $(v);
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
      select.val(selected)
    }
    else {
      let selected_unique = []
      selected.forEach(element => {
        let new_id = `${element}-${Math.random()}`;
        let new_value = element;
        select.append(`<option value="${new_id}">${new_value}</option>`);
        selected_unique.push(new_id);
      });
      select.val(selected_unique)
    }
    select.trigger('change')
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