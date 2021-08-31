const dlgProcesarCassette = new bootstrap.Modal(
    document.getElementById("dlgProcess")
);

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    $("#releaseAt").val(now.toISOString().slice(0, 16));

    const tableList = $("#datatable").DataTable({
        dom: "Bfrtip",

        ajax: {
            url: Urls["lab:slide_release"](),
            dataSrc: "",
        },

        columns: [
            { data: "id" },
            { data: "tag" },
            {
                data: "url",
                render: (data) => {
                    if (data == null) {
                        return `No`;
                    } else {
                        return `<a href="${data}">Si</a>`;
                    }
                },
            },
            {
                data: "created_at",
                render: (data) => {
                    const date = new Date(data);
                    return date.toLocaleDateString();
                },
            },
        ],

        buttons: [
            {
                text: "Seleccionar todos",
                action: function () {
                    tableList
                        .rows({
                            page: "current",
                        })
                        .select();
                },
            },

            {
                text: "Deseleccionar todos",
                action: function () {
                    tableList
                        .rows({
                            page: "current",
                        })
                        .deselect();
                },
            },
        ],

        columnDefs: [{ targets: [0], width: "1rem" }],

        select: {
            style: "multi",
        },

        paging: false,

        oLanguage: {
            sUrl:
                "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
        },
    });

    $("#btnRelease").click(() => {
        const releasedAt = $("#releaseAt").val();

        if (!releasedAt) {
            toastr.error("Fecha de disponibilizacion no puede estar vacia.");
            return;
        }

        let selectedSlidesPk = [];
        tableList
            .rows({ selected: true })
            .data()
            .each((test) => {
                selectedSlidesPk.push(test[0]);
            });

        $.ajax(Urls["lab:slide_release"](), {
            data: JSON.stringify({
                released_at: releasedAt,
                slides: selectedSlidesPk,
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
                }).then(() => {
                    location.reload();
                });
            },
            error: (xhr, textStatus, error) => {
                Swal.fire({
                    icon: "error",
                });
            },
        });
    });

    $("#btnRefresh").click(() => {
        tableList.ajax.reload();
    });
});
