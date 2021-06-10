const dlgArmarCassette = new bootstrap.Modal(
  document.getElementById("dlgProcess")
);

$(document).ready(function () {
  $("#datatable").DataTable({
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

  $("#btnProcess").on("click", () => {
    dlgArmarCassette.show();
    $("#datatable")
      .DataTable()
      .rows({ selected: true })
      .data()
      .each((element) => {
        console.log({ element });
      });
  });

  $(".detailTrigger").click(function (e) {
    e.preventDefault();
    const url = $(e.target).attr("href");
    $.get(url, function (data, textStatus) {
      console.log(data);
      Swal.fire({
        html: data,
        width: "80%",
      });
    });
  });
});
