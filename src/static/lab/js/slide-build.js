$(document).ready(function () {
  /* VARIABLES */

  const dlgArmarSlide = new bootstrap.Modal(
    document.getElementById("dlgArmarSlide")
  );

  const selectCase = $("#selectCase");
  const selectUnit = $("#selectUnit");
  const selectCassette = $("#selectCassette");
  const selectStain = $("#selectStain");

  selectStain.select2();

  // Main table which displays all availables Cases to build Slides from.
  const tableIndex = $(".zero-configuration").DataTable({
    data: slides,

    columns: [
      {
        data: "case.fields.no_caso",
        name: "case",
        type: "string",
        title: "Caso",
        orderData: [0, 1],
      },
      {
        data: "identification.fields.cage",
        name: "identification",
        type: "string",
        title: "Est/Jau",
        orderData: [0],
      },
      {
        data: "identification.fields.group",
        name: "group",
        type: "string",
        title: "Grupo",
        orderData: [1],
      },
      {
        data: "unit.fields.correlative",
        name: "unitCorrelative",
        type: "num",
        title: "# Unidad",
      },
      {
        data: "cassette.fields.correlative",
        name: "cassetteCorrelative",
        type: "num",
        title: "# Cassette",
        render: (data) => {
          if (data) {
            return `${data}`;
          } else {
            return "N/A";
          }
        },
      },
      {
        data: "caseUrl",
        name: "caseDetail",
        type: "html",
        title: "Detalle",
        render: (data, type, row, meta) => {
          return `<a class="detailTrigger" href="${data}">Ver Detalle</a>`;
        },
      },
    ],

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

    rowsGroup: [0, 1, 2, 3],

    oLanguage: {
      sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
    },
  });

  const tableBuild = $("#tableBuildDialog").DataTable({
    data: [],
    columns: [
      {
        data: "case.fields.no_caso",
        name: "case",
        type: "string",
        title: "Caso",
        orderData: [0, 1],
      },
      {
        data: "unit.fields.correlative",
        name: "unitCorrelative",
        type: "num",
        title: "# Unidad",
      },
      {
        data: "cassette",
        name: "cassetteCorrelative",
        type: "num",
        title: "# Cassette",
        render: (data) => {
          if (data) {
            return `${data.fields.correlative}`;
          } else {
            return `N/A`;
          }
        },
      },
      {
        data: "stain.text",
        name: "stain",
        type: "string",
        title: "Tincion",
      },
      {
        data: "quantity",
        name: "slides",
        type: "number",
        title: "Cant. Slide",
      },
    ],

    rowsGroup: [0, 1, 2, 3, 4],

    select: {
      style: "multi",
    },
  });

  // Array of Unit Ids from the index table.
  var selectedItems = [];

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
        selected.push(element);
      });
    selectedItems = selected;
  }

  function getUnitByPk(pk) {
    const unit = selectedItems.find((item) => item.unit.pk == pk);
    return unit;
  }

  function getCassetteByPk(pk) {
    const cassette = selectedItems.find((item) => item.cassette.pk == pk);
    return cassette;
  }

  function groupBy(xs) {
    return xs.reduce(function (rv, x) {
      (rv[x["case"].fields.no_caso] = rv[x["case"].fields.no_caso] || []).push(
        x
      );
      return rv;
    }, {});
  }

  /* END FUNCTIONS*/

  /* EVENTS */

  tableIndex.on("select.dt deselect.dt", () => {
    setSelectedUnits();
  });

  $(".zero-configuration").on("click", ".detailTrigger", function (e) {
    e.preventDefault();
    const url = $(e.target).attr("href");
    $.get(url, function (data, textStatus) {
      Swal.fire({
        html: data,
        width: "80%",
      });
    });
  });

  $(".btn-close").click(() => {
    dlgArmarSlide.hide();
  });

  $("#btnArmarSlide").click(() => {
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    $("#buildAt").val(now.toISOString().slice(0, 16));

    dlgArmarSlide.show();

    let cases = selectedItems.map((item, index) => {
      return {
        id: index,
        text: `${item.case.fields.no_caso}`,
      };
    });
    cases.unshift({
      id: -1,
      text: "Seleccione un Caso",
    });
    selectCase.select2({
      data: cases,
    });
    selectStain.select2();
  });

  $("#btnDeleteSelected").click(() => {
    tableBuild.rows(".selected").remove().draw(false);
  });

  selectCase.on("change", (e) => {
    const index = e.target.value;

    if (index < 0) return;

    const selectedCase = selectedItems[index].case;

    const filteredItems = selectedItems.filter(
      (item) => item.case == selectedCase
    );

    let units = filteredItems.map((item) => {
      return {
        id: item.unit.pk,
        text: `${item.identification.fields.cage} / ${item.unit.fields.correlative}`,
      };
    });

    units.unshift({
      id: -1,
      text: `Seleccione Ident/Unidad`,
    });

    selectUnit.empty();
    for (const unit of units) {
      selectUnit.append(new Option(unit.text, unit.id));
    }

    if (selectUnit.hasClass("select2-hidden-accessible")) {
      selectUnit.select2("destroy");
    }
    selectUnit.select2();
  });

  selectUnit.on("change", (e) => {
    const pk = e.target.value;

    if (pk < 0) return;

    const filteredItems = selectedItems.filter(
      (item) => item.unit.pk == pk && item["cassette"] != null
    );

    let cassettes = filteredItems.map((item) => {
      return {
        id: item.cassette.pk,
        text: `${item.cassette.fields.correlative}`,
      };
    });

    cassettes.unshift({
      id: -1,
      text: "Seleccione un Cassette",
    });

    selectCassette.empty();
    for (const cassette of cassettes) {
      selectCassette.append(new Option(cassette.text, cassette.id));
    }

    if (selectCassette.hasClass("select2-hidden-accessible")) {
      selectCassette.select2("destroy");
    }
    selectCassette.select2();
  });

  $("#btnCreateSlide").click(() => {
    const selectedCase = selectCase.select2("data")[0].id;
    const unit = getUnitByPk(selectUnit.select2("data")[0].id);
    let cassette = null;
    if (
      selectCassette.hasClass("select2-hidden-accessible") &&
      selectCassette.select2("data")[0].id > 0
    ) {
      cassette = getCassetteByPk(selectCassette.select2("data")[0].id).cassette;
    }
    const stain = selectStain.select2("data")[0];
    const quantity = parseInt($("#inputQty").val());

    const row = {
      case: selectedItems[selectedCase].case,
      unit: unit.unit,
      cassette: cassette,
      stain: stain,
      quantity: quantity,
    };

    tableBuild.row.add(row).draw();
  });

  $("#btnSaveSlide").click(() => {
    const build_at = $("#buildAt").val();

    const data = tableBuild.rows().data();
    const grouped = groupBy(data);
    let slides = [];
    let text = "";
    for (const group in grouped) {
      let group_count = 1;
      for (const row of grouped[group]) {
        for (let i = 0; i < row.quantity; i++) {
          text += `<li class="list-group-item">${group},${row.stain.text},${group_count}</li>`;
          let cassette = null;
          if (row.cassette) {
            cassette = row.cassette.pk;
          }
          slides.push({
            unit_id: row.unit.pk,
            stain_id: row.stain.id,
            correlative: group_count++,
            cassette_id: cassette,
          });
        }
      }
    }

    Swal.fire({
      title: "Se crearan los siguientes slides:",
      html: `<ul class="list-group list-group-flush overflow-auto" style="max-height: 18rem;">${text}</ul>`,
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax(Urls["lab:slide_build"](), {
          data: JSON.stringify({
            build_at: build_at,
            slides: slides,
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
          },
          error: (xhr, textStatus, error) => {
            Swal.fire({
              icon: "error",
            });
          },
        });
      }
    });
  });

  /* END EVENTS */
});
