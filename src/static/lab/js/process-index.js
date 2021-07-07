const datatable = $("#datatable");
const selProcess = $("#selProcess");

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

selProcess.change((e) => {
  const process_id = parseInt(e.target.value);
  if (Number.isInteger(process_id) && process_id > 0) {
    $.ajax(Urls["lab:process_units"](process_id), {
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (data, textStatus) => {
        // TODO: Display units from server
        console.log({ data });
      },
      error: (xhr, textStatus, error) => {
        console.error({ xhr, textStatus, error });
        Swal.fire({
          icon: "error",
        });
      },
    });
  }
  return;
});
