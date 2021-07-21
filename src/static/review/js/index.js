Dropzone.autoDiscover = false;
$(document).ready(() => {
  $("#waiting, #formating, #reviewing, #sending")
    .sortable({
      connectWith: ".state",
    })
    .disableSelection();

  $("#sending, #finished")
    .sortable({
      connectWith: ".finishing",
    })
    .disableSelection();

  $("#newFiles").dropzone({
    dictDefaultMessage: "Arrastre sus archivos aqui",
    acceptedFiles: ".csv, .doc, .docx, .ods, .odt, .pdf, .xls, .xlsx, .xlsm",
    createImageThumbnails: false,
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

  const selectRecipients = $(".selectRecipients");

  selectRecipients.select2();

  const selectMailList = $("#selectMailList");

  const dlgNewRecipient = new bootstrap.Modal(
    document.getElementById("recipientDialog"),
    {
      backdrop: "static",
    }
  );
  const dlgFileList = new bootstrap.Modal(
    document.getElementById("fileDialog"),
    {
      backdrop: "static",
    }
  );

  const dlgNewMailList = new bootstrap.Modal(
    document.getElementById("mailListDialog"),
    {
      backdrop: "static",
    }
  );
  const newRecipientForm = $("#newRecipientForm");

  const newMailListForm = $("#newMailListForm");

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
      const data = JSON.parse(row);
      return {
        analysis: data[0],
        case: data[1],
        exam: data[2],
        customer: data[3],
      };
    });
  }

  function populateList(id, array, filter = null) {
    const list = $(id);
    list.empty();

    let items = array;

    if (filter != null) {
      items = array.filter((item) => {
        if (item.case.fields.no_caso.toLowerCase().includes(filter)) {
          return true;
        }

        if (item.exam.fields.name.toLowerCase().includes(filter)) {
          return true;
        }

        if (item.customer.fields.name.toLowerCase().includes(filter)) {
          return true;
        }

        return false;
      });
    }

    for (const item of items) {
      list.append(`<li class="list-group-item">
                        <small>
                            <a href="#" class="serviceItem" id="${item.analysis.pk}">
                                ${item.case.fields.no_caso} - ${item.exam.fields.name} - ${item.customer.fields.name}
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

  function updateSelectRecipients() {
    $.get(Urls["review:recipients"](analysis), (response) => {
      const selectedRecipients = JSON.parse(response["current_recipients"]);
      const mailLists = JSON.parse(response["mail_lists"]);

      $("#mainRecipient").val(null).trigger("change");
      $("#ccRecipient").val(null).trigger("change");

      if (selectMailList.hasClass("select2-hidden-accessible")) {
        selectMailList.select2("destroy");
      }

      selectMailList.empty();

      selectMailList.append(
        `<option value="-1" selected>Agregar una lista de correos</option>`
      );
      for (const option of mailLists) {
        selectMailList.append(
          `<option value="${option.pk}">${option.fields.name}</option>`
        );
      }

      selectMailList.select2();

      const selectedMainRecipients = selectedRecipients
        .filter((selected) => selected.fields.is_main)
        .flatMap((selected) => [selected.fields.recipient]);

      const selectedCCRecipients = selectedRecipients
        .filter((selected) => !selected.fields.is_main)
        .flatMap((selected) => [selected.fields.recipient]);

      $("#mainRecipient").val(selectedMainRecipients).trigger("change");
      $("#ccRecipient").val(selectedCCRecipients).trigger("change");
    });
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

    updateSelectRecipients();

    dlgFileList.show();

    $.ajax(Urls["review:files"](analysis), {
      method: "GET",

      success: (data, textStatus) => {
        const prereports = data.prereports;
        const prereportList = $("#prereportList");
        prereportList.empty();

        for (const file of prereports) {
          prereportList.append(
            `<li class="list-group-item"><a href="${file.download}" target="_BLANK">${file.name}</a></li>`
          );
        }

        const reviews = data.reviews;
        const reviewList = $("#reviewList");
        reviewList.empty();

        for (const file of reviews) {
          const created = new Date(file.created_at);
          reviewList.append(
            `<li class="list-group-item">
              <a href="${file.download}" target="_BLANK">
                ${file.name}
                - ${getStateName(file.state)}
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
                    toastr.warning(
                      "No se encontró archivo en estado `Para Enviar` disponible."
                    );
                    break;
                  case 1:
                    toastr.warning(
                      "No seleccionó lista de correo, o la lista esta vacia."
                    );
                    break;
                  case 2:
                    toastr.warning("Ocurrio un error enviando el correo.");
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

  $("#btnRefreshRecipients").click(() => {
    toastr.info("Actualizando destinatarios...");
    updateSelectRecipients();
  });

  $("#search").on("input", (e) => {
    const queryString = e.target.value.toLowerCase();

    populateList("#waiting", waiting, queryString);
    populateList("#formating", formating, queryString);
    populateList("#reviewing", reviewing, queryString);
    populateList("#sending", sending, queryString);
    populateList("#finished", finished, queryString);
  });

  selectMailList.change((e) => {
    const mailListPk = selectMailList.select2("data")[0].id;

    if (mailListPk == -1) return;

    $.ajax(Urls["review:list_recipients"](mailListPk), {
      method: "GET",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      contentType: "application/json; charset=utf-8",

      success: (response) => {
        const recipients = response;

        const mains = recipients
          .filter((recipient) => recipient.is_main)
          .map((recipient) => recipient.id);
        const ccs = recipients
          .filter((recipient) => !recipient.is_main)
          .map((recipient) => recipient.id);

        $("#mainRecipient").val(mains).trigger("change");
        $("#ccRecipient").val(ccs).trigger("change");
      },
    });

    selectMailList.val(null).trigger("change");
    selectMailList.select2("close");
  });

  $("#btnCreateRecipient").click(() => {
    dlgNewRecipient.show();
  });

  $("#btnCreateMailList").click(() => {
    dlgFileList.hide();
    dlgNewMailList.show();
  });

  newRecipientForm.submit((e) => {
    e.preventDefault();
    const newRecipient = newRecipientForm
      .serializeArray()
      .reduce((acc, input) => ({ ...acc, [input.name]: input.value }), {});

    $.ajax(Urls["review:create_recipient"](), {
      method: "POST",
      data: JSON.stringify(newRecipient),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      contentType: "application/json; charset=utf-8",

      success: (response) => {
        toastr.success("Destinatario creado.");
        newRecipientForm.trigger("reset");
        updateSelectRecipients();
        dlgFileList.show();
        dlgNewRecipient.hide();
      },
      error: (err) => {
        toastr.error("Ha ocurrido un error.");
      },
    });
  });

  newMailListForm.submit((e) => {
    e.preventDefault();
    let newMailList = newMailListForm
      .serializeArray()
      .reduce((acc, input) => ({ ...acc, [input.name]: input.value }), {});

    newMailList.analysis_pk = analysis;
    const mains = $("#mainRecipient")
      .select2("data")
      .map((main) => {
        return {
          id: main.id,
          is_main: true,
        };
      });
    const ccs = $("#ccRecipient")
      .select2("data")
      .map((cc) => {
        return {
          id: cc.id,
          is_main: false,
        };
      });

    newMailList.recipients = [...mains, ...ccs];

    $.ajax(Urls["review:new_mail_list"](), {
      method: "POST",
      data: JSON.stringify(newMailList),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      contentType: "application/json; charset=utf-8",

      success: (response) => {
        toastr.success("Lista de correos creada.");
        newMailListForm.trigger("reset");
        dlgFileList.show();
        dlgNewMailList.hide();
      },
      error: (err) => {
        toastr.error("Ha ocurrido un error.");
      },
    });
  });

  $("#btnSaveRecipients").click(() => {
    const mainRecipients = $("#mainRecipient").select2("data");
    const ccRecipients = $("#ccRecipient").select2("data");

    let recipients = [];

    for (const [index, element] of mainRecipients.entries()) {
      recipients.push({
        pk: element.id,
        is_main: true,
      });
    }

    for (const [index, element] of ccRecipients.entries()) {
      recipients.push({
        pk: element.id,
        is_main: false,
      });
    }

    $.ajax(Urls["review:recipients"](analysis), {
      method: "POST",
      data: JSON.stringify(recipients),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      contentType: "application/json; charset=utf-8",

      success: () => {
        toastr.success("Actualizado exitosamente.");
      },

      error: () => {
        toastr.error("Ha ocurrido un error.");
      },
    });
  });
});
