$(document).ready(function () {
  /* VARIABLES */

  const dlgArmarCassette = new bootstrap.Modal(
    document.getElementById("dlgArmarCassette")
  );

  const dlgConfigurarCassette = new bootstrap.Modal(
    document.getElementById("dlgConfigurarCassette"),
    {
      backdrop: "static",
      keyboard: false,
    }
  );

  const selectUnit = $("#selectNewCassetteUnit");

  const rulesForm = {
    uniqueOrgans: $("#selUniqueOrgans"),
    groupOrgans: $("#selGroupOrgans"),
  };

  var rules = {
    uniques: [],
    groups: [],
    max: 0,
  };

  // organs was defined in the build.html as it was a variable returned from the server
  const organOptions = organs.map((organ) => {
    return {
      id: organ.pk,
      text: organ.fields.name,
    };
  });

  $(".organSelect").select2({
    data: organOptions,
    width: "100%",
  });

  // Main table which displays all availables Cases to build Cassettes from.
  const tableIndex = $(".zero-configuration").DataTable({
    dom: "Bfrtip",

    buttons: [
      {
        text: "Seleccionar todos",
        action: function () {
          tableIndex
            .rows({
              page: "current",
            })
            .select();
        },
      },

      {
        text: "Deseleccionar todos",
        action: function () {
          tableIndex
            .rows({
              page: "current",
            })
            .deselect();
        },
      },
    ],

    select: {
      style: "multi",
    },

    paging: false,

    rowsGroup: [1, 2, 3],

    oLanguage: {
      sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
    },
  });

  // Array of Unit Ids from the index table.
  var selectedItems = [];

  // Array of Cassettes from the build table.
  var selectedCassettes = [];

  // Array of Units used in logic for the build form.
  var units = [];

  // Modal table which displays selectedItems's Cassettes.

  const tableBuild = $("#tableBuildDialog").DataTable({
    ajax: {
      url: Urls["lab:cassette_prebuild"](),
      contentType: "application/json",
      type: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      data: function () {
        return JSON.stringify({
          selected: selectedItems,
          rules: rules,
        });
      },
      dataSrc: "",
    },

    paging: false,

    columns: [
      {
        data: "case",
        name: "case",
        type: "string",
        title: "Caso",
        orderData: [0, 1],
      },
      {
        data: "identification",
        name: "identification",
        type: "string",
        title: "Est/Jau",
        orderData: [0],
      },
      {
        data: "unit",
        name: "unitCorrelative",
        type: "num",
        title: "# Unidad",
      },
      {
        data: "cassette",
        name: "cassetteCorrelative",
        type: "num",
        title: "# Cassette",
      },
      {
        data: "organs",
        name: "cassetteOrgans",
        title: "Organos",
        render: function (data, type, row, meta) {
          const select = $("<select>")
            .addClass(`unitSelectOrgan unit-${row.unit_id}`)
            .attr("id", `U${row.unit_id}C${row.cassette}`);

          return select.prop("outerHTML");
        },
      },
    ],

    rowsGroup: [0, 1, 2],

    select: {
      style: "multi",
    },
  });

  /* END VARIABLES*/

  /* FUNCTIONS */
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function setSelectedUnits() {
    let selected = [];
    let item = tableIndex
      .rows({ selected: true })
      .data()
      .each((element) => {
        selected.push(parseInt(element[5]));
      });
    selectedItems = selected;
  }

  function setSelectedCassettes() {
    let selected = [];
    let item = tableBuild
      .rows({ selected: true })
      .data()
      .each((element) => {
        selected.push({
          unitId: element.unit_id,
          cassette: element.cassette,
        });
      });

    selectedCassettes = selected;
  }

  // Convert the response received from the server
  // into a format that Select2 can handle
  // then initiate Select2.
  function activateNewCassetteUnitSelect(response) {
    let options = response.map((row) => {
      return {
        id: row.unit_id,
        text: `${row.case} / ${row.identification} / ${row.unit}`,
      };
    });
    selectUnit.select2({
      placeholder: "Selecciona caso / identificacion / unidad",
      allowClear: true,
      data: options,
      width: "100%",
    });
  }

  function activateOrganSelect() {
    $(".unitSelectOrgan").each(function (i, elem) {
      const unitId = elem.classList[1].split("-")[1];
      const cassetteId = $(this).attr("id").split("C")[1];
      const organs = getOrgansFromUnit(unitId);
      const cassetteOrgans = getOrgansFromCassette(unitId, cassetteId);
      const options = organs.map((organ) => {
        const isSelected = cassetteOrgans.some((row) => row.pk == organ.pk);
        return {
          id: organ.pk,
          text: organ.fields.name,
          selected: isSelected,
        };
      });
      $(this).select2({
        data: options,
        width: "100%",
        multiple: true,
      });
    });
  }

  function getUnitsFromUnitId(unitId) {
    return units.filter((row) => {
      return row.unit_id === parseInt(unitId);
    });
  }

  function getOrgansFromUnit(unitId) {
    const findAvailable = units.find((row) => row.unit_id == unitId);
    return JSON.parse(findAvailable.organs);
  }

  function getOrgansFromCassette(unitId, cassetteId) {
    const findAvailable = units.find(
      (row) => row.unit_id == unitId && row.cassette == cassetteId
    );
    let organs = [];
    try {
      organs = JSON.parse(findAvailable.cassette_organs);
    } catch (SyntaxError) {
      organs = [];
    }
    return organs;
  }

  function updateNumberCassettes() {
    let unitId = 1;
    let cassetteNumber = 1;

    tableBuild.rows().every(function (rowIdx, tableLoop, rowLoop) {
      const row = this.data();
      let currentCassetteCell = tableBuild.cell({ row: rowIdx, column: 3 });
      if (row.unit_id != unitId) {
        unitId = row.unit_id;
        cassetteNumber = 1;
      }
      currentCassetteCell.data(cassetteNumber);
      cassetteNumber += 1;
    });
  }

  function checkIfExists(organId) {
    const unique = rules.uniques.includes(organId);
    const group = rules.groups.some((group) => group.includes(organId));
    return unique || group;
  }

  /* END FUNCTIONS*/

  /* EVENTS */

  $("#btnCreateCassette").click(() => {
    const selectedUnit = selectUnit.select2("data");

    const unitList = units.filter(
      (row) => row.unit_id === parseInt(selectedUnit[0].id)
    );

    const cassetteCount = unitList.length + 1;

    const newRow = {
      case: unitList[0].case,
      identification: unitList[0].identification,
      organs: unitList[0].organs,
      unit: unitList[0].unit,
      unit_id: unitList[0].unit_id,
      cassette: cassetteCount,
      cassette_organs: [],
    };

    units.push(newRow);

    tableBuild.row.add(newRow).draw();

    activateOrganSelect();
    updateNumberCassettes();
  });

  $(".btn-close").click(function () {
    if (selectUnit.hasClass("select2-hidden-accessible")) {
      selectUnit.select2("destroy");
    }
    dlgArmarCassette.hide();
    dlgConfigurarCassette.hide();

    rules = {
      uniques: [],
      groups: [],
      max: 0,
    };
  });

  $("#btnDeleteSelected").click(() => {
    tableBuild.rows(".selected").remove().draw(false);

    units = units.filter((row) => {
      const unitId = row.unit_id;
      const cassetteId = row.cassette;
      return !selectedCassettes.some(
        (cassette) =>
          cassette.unitId == unitId && cassette.cassette == cassetteId
      );
    });
    selectedCassettes.length = 0;

    updateNumberCassettes();
  });

  $("#btnArmarCassette").click(function () {
    tableBuild.ajax.reload((response) => {
      // Unit details received from the server
      units = response;
      activateNewCassetteUnitSelect(response);
      activateOrganSelect();
    });

    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    $("#buildAt").val(now.toISOString().slice(0, 16));

    dlgArmarCassette.show();
  });

  $("#btnConfigurarCassette").click(() => {
    dlgConfigurarCassette.show();
  });

  tableIndex.on("select.dt deselect.dt", () => {
    setSelectedUnits();
  });

  tableBuild.on("select.dt deselect.dt", (e, dt, type, indexes) => {
    setSelectedCassettes();
  });

  $("#btnSaveCassette").click(() => {
    let new_cassettes = [];
    tableBuild.rows().every(function (rowIdx, tableLoop, rowLoop) {
      const data = this.data();
      const cassette = tableBuild.cell({ row: rowIdx, column: 3 }).data();
      const cell = tableBuild.cell({ row: rowIdx, column: 4 });
      const organs = $($(cell.node()).children()[0])
        .select2("data")
        .map((organ) => parseInt(organ.id));

      new_cassettes.push({
        id: data.unit_id,
        correlative: cassette,
        organs: organs,
      });
    });
    const build_at = $("#buildAt").val();
    $.ajax(Urls["lab:cassette_build"](), {
      data: JSON.stringify({
        build_at: build_at,
        units: new_cassettes,
      }),

      method: "POST",

      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (data, textStatus) => {
        Swal.fire({
          icon: "success",
          title: "Guardado",
        });
        location.reload();
      },
      error: (xhr, textStatus, error) => {
        Swal.fire({
          icon: "error",
        });
      },
    });
  });

  $("#btnGroupOrgans").click(() => {
    const selectedOrgans = rulesForm.groupOrgans.select2("data");
    let ids = [];
    let text = [];

    for (let select of selectedOrgans) {
      ids.push(parseInt(select.id));
      text.push(select.text);
    }
    rules.groups.push(ids);

    $("#tableGroupOrgans > tbody:last-child").append(
      `<tr>
            <td style="display: none;" class="groupIds">${ids.join(";")}</td>
            <td>${text.join(", ")}</td>
            <td>
                <button type="button" class="btn btn-danger">X</button>
            </td>
        </tr>`
    );

    rulesForm.groupOrgans.val(null).trigger("change");
  });

  $("#tableGroupOrgans").on("click", "button.btn-danger", function () {
    const ids = $(this).parent().siblings(".groupIds").text().split(";");
    const index = rules.groups.findIndex((group) => {
      return group === ids;
    });
    rules.groups.splice(index, 1);
    $(this).parents("tr").remove();
  });

  $("#selUniqueOrgans").on("select2:select select2:unselect", (e) => {
    const selected = $("#selUniqueOrgans")
      .select2("data")
      .map((row) => parseInt(row.id));

    rules.uniques = selected;
  });

  $("#dlgConfigurarCassette").on("select2:selecting", ".organSelect", (e) => {
    const id = parseInt(e.params.args.data.id);
    if (checkIfExists(id)) {
      Swal.fire({
        icon: "warning",
        title: "Ese organo ya fue seleccionado",
      });
      e.preventDefault();
    }
  });

  $("#inputMaxOrgans").on("input", (e) => {
    const value = parseInt(e.target.value);
    if (value < 0) {
      e.preventDefault();
      Swal.fire({
        icon: "warning",
        title: "Cantidad maxima no puede ser menor que 0.",
      });
      $(e.target).val(0);
    } else {
      rules.max = parseInt(e.target.value);
    }
  });

  $("#btnSaveConfiguration").click(() => {
    dlgConfigurarCassette.hide();
  });

  $(".detailTrigger").click(function (e) {
    e.preventDefault();
    const url = $(e.target).attr("href");
    $.get(url, function (data, textStatus) {
      Swal.fire({
        html: data,
        width: "80%",
      });
    });
  });

  $("#tableBuildDialog").on("select2:selecting", ".unitSelectOrgan", (e) => {
    const organ = parseInt(e.target.value);
    const unitId = e.target.id.split("C")[0].substring(1); //Selects contain an id made of U[Unit's pk]C[Cassette's correlative]
    const availableOrganCount = getOrgansFromUnit(unitId).filter(
      (row) => row.pk == organ
    ).length;
    const tableData = tableBuild
      .rows()
      .data()
      .filter((row) => row.unit == unitId);

    let currentCount = 0;

    tableData.each((row) => {
      const id = `U${row.unit}C${row.cassette}`;

      const select = $(`#${id}`).select2("data")[0].id;
      if (select == organ) currentCount++;
    });

    if (currentCount >= availableOrganCount) {
      e.preventDefault();
      Swal.fire({
        title: "No se puede agregar organo",
        icon: "error",
        text: "Ese organo ya esta asignado a otro Cassette de la misma Unidad.",
      });
      return;
    }
  });

  /* END EVENTS */
});
