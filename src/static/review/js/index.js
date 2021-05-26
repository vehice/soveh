Dropzone.autoDiscover = false;
$(document).ready(() => {
  $("#waiting, #formating, #reviewing, #sending")
    .sortable({
      connectWith: ".state",
    })
    .disableSelection();

  $("#sending, #finished")
    .sortable({
      connectWith: "#finished",
    })
    .disableSelection();

  $("#newFiles").dropzone({
    previewsContainer: null,
    dictDefaultMessage: "Arrastre sus archivos aqui",
    acceptedFiles: ".csv, .doc, .docx, .ods, .odt, .pdf, .xls, .xlsx",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    init: function () {
      this.on("processing", (file) => {
        if (parseInt(analysis) > 0) {
          this.options.url = Urls["review:files"](analysis);
        }
      });
    },
  });

  const selectRecipients = $("#selectRecipients");

  const dlgNewRecipient = new bootstrap.Modal(
    document.getElementById("dlgRecipient")
  );
  const dlgFileList = new bootstrap.Modal(
    document.getElementById("fileDialog")
  );

  let waiting;
  let formating;
  let reviewing;
  let sending;
  let finished;

  let analysis;

  Promise.all([
    getReviews(0),
    getReviews(1),
    getReviews(2),
    getReviews(3),
    getReviews(4),
  ]).then((values) => {
    waiting = parseResponse(values[0]);
    formating = parseResponse(values[1]);
    reviewing = parseResponse(values[2]);
    sending = parseResponse(values[3]);
    finished = parseResponse(values[4]);

    populateList("#waiting", waiting);
    populateList("#formating", formating);
    populateList("#reviewing", reviewing);
    populateList("#sending", sending);
    populateList("#finished", finished);
  });

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

  async function getReviews(stage) {
    let response = await fetch(Urls["review:list"](stage));

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  function parseResponse(response) {
    return response.map((row) => {
      return {
        analysis: JSON.parse(row.analysis)[0],
        exam: JSON.parse(row.exam)[0],
        case: JSON.parse(row.case)[0],
      };
    });
  }

  function populateList(id, array) {
    const list = $(id);
    list.empty();

    for (const item of array) {
      list.append(`<li class="list-group-item">
                        <small>
                            <a href="#" class="serviceItem" id="${item.analysis.pk}">
                                ${item.case.fields.no_caso} - ${item.exam.fields.name} - ${item.case.fields.company}
                            </a>
                        </small>
                    </li>`);
    }

    updateCount(id);
  }

  function updateCount(id) {
    if (!id.includes("#")) {
      id = `#${id}`;
    }
    const count = $(`${id} li`).length;
    $(`${id}Count`).text(`(${count})`);
  }

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

  function getStateName(state) {
    switch (parseInt(state)) {
      case 0:
        return "En Espera";
      case 1:
        return "Formato";
      case 2:
        return "Revision";
      case 3:
        return "Por enviar";
    }
  }

  /* EVENTS */

  $(".state").on("sortreceive", (event, ui) => {
    const currentState = ui.sender[0].id;
    const nextState = event.target.id;
    let state;

    switch (nextState) {
      case "waiting":
        state = 0;
        break;
      case "formating":
        state = 1;
        break;
      case "reviewing":
        state = 2;
        break;
      case "sending":
        state = 3;
        break;
      case "finished":
        state = 4;
        break;
    }
    updateCount(currentState);
    updateCount(nextState);

    const analysisId = ui.item[0].children[0].children[0].id;

    $.ajax(Urls["review:stage"](analysisId), {
      data: JSON.stringify({
        state: state,
      }),

      method: "POST",

      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (data, textStatus) => {
        toastr.success("Actualizado exitosamente.");
      },

      error: (xhr, textStatus, error) => {
        toastr.error("Ocurrió un error.");
        location.reload();
      },
    });
  });

  $("ul.list-group").on("click", ".serviceItem", (e) => {
    e.preventDefault();
    const title = `Archivos: ${e.target.innerText}`;
    analysis = e.target.id;
    $("#fileDialog h5.modal-title").text(title);

    dlgFileList.show();

    $.get(Urls["review:mail_list"](analysis), (response) => {
      const mailList = JSON.parse(response["mail_lists"]);

      const selected = JSON.parse(response["current_lists"]);
      if (mailList.length > 0) {
        if (selectRecipients.hasClass("select2-hidden-accessible")) {
          selectRecipients.select2("destroy");
        }
        const options = mailList.map((mail) => {
          const isSelected = selected.some(
            (item) => item.fields.mail_list == mail.pk
          );
          return {
            id: mail.pk,
            text: mail.fields.name,
            selected: isSelected,
          };
        });
        selectRecipients.select2({
          data: options,
          width: "100%",
          multiple: true,
        });
      }
    });

    $.ajax(Urls["review:files"](analysis), {
      method: "GET",

      success: (data, textStatus) => {
        const prereports = JSON.parse(data.prereports);
        const prereportList = $("#prereportList");
        prereportList.empty();

        for (const file of prereports) {
          prereport.append(
            `<li class="list-group-item">${file.fields.file}</li>`
          );
        }

        const reviews = JSON.parse(data.reviews);
        const reviewList = $("#reviewList");
        reviewList.empty();

        for (const file of reviews) {
          const created = new Date(file.fields.created_at);
          reviewList.append(
            `<li class="list-group-item">
              <a href="${Urls["review:download_file"](file.pk)}">
                ${file.fields.path}
                - ${getStateName(file.fields.state)}
                - ${created.toLocaleString()}
              </a>
            </li>`
          );
        }
      },
      error: (xhr, textStatus, error) => {
        toastr.error(error);
      },
    });
  });

  selectRecipients.on("change", (e) => {
    const selected = selectRecipients
      .select2("data")
      .map((selected) => parseInt(selected.id));

    $.ajax(Urls["review:mail_list"](analysis), {
      method: "POST",
      data: JSON.stringify(selected),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      contentType: "application/json; charset=utf-8",

      success: () => {
        toastr.success("Actualizado exitosamente");
      },
    });
  });

  $("#finished").on("sortreceive", (e, ui) => {
    const analysisId = ui.item[0].children[0].children[0].id;
    $.get(Urls["review:analysis_emails"](analysisId), (response) => {
      let data = JSON.parse(response);
      let text = "";
      for (const mailList of data) {
        text += `<b>${mailList.name}:</b>`;
        for (const recipient of JSON.parse(mailList.recipients)) {
          text += `<p>${recipient.fields.first_name} (${recipient.fields.email})<p>`;
        }
      }
      Swal.fire({
        title: "Se enviara un correo a los siguientes contactos, ¿esta seguro?",
        html: text,
        input: "select",
        inputOptions: {
          1: "ESP",
          0: "ENG",
        },
        inputPlaceholder: "Seleccione idioma para el correo",
        showCancelButton: true,
        cancelButtonText: "Cancelar",
      }).then((result) => {
        if (result.isConfirmed) {
          toastr.info("Enviando correos...");
          $.ajax(Urls["review:send_email"](analysisId), {
            method: "PUT",
            data: JSON.stringify(result.value),
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
            },
            contentType: "application/json; charset=utf-8",

            success: (response) => {
              if (response.status === "OK") {
                toastr.success("Correo enviado.");
              } else {
                toastr.error("Ocurrió un error.");
                switch (response.code) {
                  case 0:
                    toastr.info(
                      "No se encontró archivo en estado `Para Enviar` disponible."
                    );
                    break;
                  case 1:
                    toastr.info("Ocurrio un error enviando el correo.");
                    break;
                }
              }
            },
          });
        } else {
          toastr.info("Operacion cancelada.");
          setTimeout(location.reload, 1500);
        }
      });
    });
  });
});
