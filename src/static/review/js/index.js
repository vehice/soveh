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
    dictDefaultMessage: "Arrastre sus archivos aqui",
    acceptedFiles: ".csv, .doc, .docx, .ods, .odt, .pdf, .xls, .xlsx",
  });
  $("#newFiles").on("addedfile", (file) => {
    console.log({ file });
  });

  let waiting;
  let formating;
  let reviewing;
  let sending;
  let finished;

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
                            <a href="#" id="${item.analysis.pk}">
                                ${item.case.fields.no_caso} - ${item.exam.fields.name} - ${item.case.fields.company}
                            </a>
                        </small>
                    </li>`);
    }
  }

  /* EVENTS */

  $(".state").on("sortreceive", (event, ui) => {
    const stateName = event.target.id;
    let state;

    switch (stateName) {
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

    const analysisId = ui.item[0].id;

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
  });

  $("ul.list-group").on("click", "a", (e) => {
    e.preventDefault();
    const title = `Archivos: ${e.target.innerText}`;
    const analysisId = e.target.id;
    $("#fileDialog h5.modal-title").text(title);

    $("#fileDialog").modal("show");

    $.ajax(Urls["review:files"](analysisId), {
      method: "GET",

      success: (data, textStatus) => {
        const files = JSON.parse(data);
        const fileList = $("#fileList");
        fileList.empty();

        for (const file of files) {
          fileList.append(`<li class="list-group-item">${file}</li>`);
        }
      },
      error: (xhr, textStatus, error) => {
        Swal.fire({
          icon: "error",
        });
      },
    });
  });
});
