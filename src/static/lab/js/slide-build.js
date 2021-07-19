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
    ajax: {
      url: Urls["lab:slide_prebuild"](),
      contentType: "application/json",
      type: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      data: function () {
        if (selectedItems && selectedItems.length > 0) {
          return JSON.stringify(
            selectedItems.map((item) => {
              const unit = item.unit.pk;
              const cassette = item.cassette ? item.cassette.pk : -1;
              return {
                unit,
                cassette,
              };
            })
          );
        }
        return [];
      },
      dataSrc: "",
    },
    columns: [
      {
        data: "case.no_caso",
        name: "case",
        type: "string",
        title: "Caso",
      },
      {
        data: "identification.cage",
        name: "identification",
        type: "num",
        title: "Ident.",
      },
      {
        data: "unit.correlative",
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
          if (data[0] && data[0].correlative) {
            return `${data[0].correlative}`;
          } else {
            return `N/A`;
          }
        },
      },
      {
        data: "stain.abbreviation",
        name: "stain",
        type: "string",
        title: "Tincion",
      },
      {
        data: "slide",
        name: "index",
        type: "string",
        title: "Correlativo",
        render: (data, type, row, meta) => {
          return data;
        },
      },
    ],

    rowsGroup: [0, 1, 2, 3],

    select: {
      style: "multi",
    },

    paging: false,
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

  function updateCorrelativeSlide() {
    let caseId = 1;
    let correlativeNumber = 1;

    tableBuild.rows().every(function (rowIdx, tableLoop, rowLoop) {
      const row = this.data();
      let currentCorrelativeCell = tableBuild.cell({ row: rowIdx, column: 5 });
      console.log({ row });
      if (row.case.id != caseId) {
        caseId = row.case.id;
        correlativeNumber = 1;
      }
      currentCorrelativeCell.data(correlativeNumber);
      correlativeNumber += 1;
    });
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
    tableBuild.ajax.reload();
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    $("#buildAt").val(now.toISOString().slice(0, 16));

    dlgArmarSlide.show();

    let cases = selectedItems
      .map((item, index) => {
        return {
          id: `${item.case.pk};${item.identification.pk};${item.unit.pk}`,
          text: `${item.case.fields.no_caso} / ${item.identification.fields.cage} / ${item.unit.fields.correlative}`,
        };
      })
      .filter(
        (row, index, self) =>
          index === self.findIndex((obj) => obj.id === row.id)
      );

    cases.unshift({
      id: -1,
      text: "Seleccione un Caso / Identificacion / Unidad",
    });

    selectCase.select2({
      data: cases,
    });
    selectStain.select2();
  });

  $("#btnDeleteSelected").click(() => {
    tableBuild.rows(".selected").remove().draw(false);
    updateCorrelativeSlide();
  });

  selectCase.on("change", (e) => {
    const pk = e.target.value.split(";")[2];

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
    const stain = selectStain.select2("data")[0];
    tableBuild
      .rows({ selected: true })
      .data()
      .each((value, index) => {
        const cassette = getCassetteByPk(value.cassette[0].id).cassette;
        const row = getUnitByPk(value.unit.id);

        let new_row = {
          case: {
            id: row.case.pk,
            no_caso: row.case.fields.no_caso,
          },
          identification: {
            id: row.identification.pk,
            cage: row.identification.fields.cage,
          },
          unit: {
            id: row.unit.pk,
            correlative: row.unit.fields.correlative,
          },
          stain: {
            id: stain.id,
            abbreviation: stain.text,
          },
          slide: 0,
        };

        if ("pk" in cassette && "fields" in cassette) {
          new_row.cassette = [
            {
              id: cassette.pk,
              correlative: cassette.fields.correlative,
            },
          ];
        } else {
          new_row.cassette = [
            {
              id: -1,
              correlative: "N/A",
            },
          ];
        }

        tableBuild.row.add(new_row).draw();
      });
    updateCorrelativeSlide();
  });

  $("#btnSaveSlide").click(() => {
    const build_at = $("#buildAt").val();

    let slides = [];
    let text = "";
    const data = tableBuild
      .rows()
      .data()
      .each((value, index) => {
        let new_slide = {
          unit_id: value.unit.id,
          stain_id: value.stain.id,
          correlative: index + 1,
        };
        if (value.cassette[0] && value.cassette[0].id > 0) {
          new_slide.cassette_id = value.cassette[0].id;
        }
        slides.push(new_slide);

        text += `<li class="list-group-item">${value.case.no_caso},${
          value.stain.abbreviation
        },${index + 1}</li>`;
      });

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
