/**
 * Returns the week number for this date.  dowOffset is the day of week the week
 * "starts" on for your locale - it can be from 0 to 6. If dowOffset is 1 (Monday),
 * the week returned is the ISO 8601 week number.
 * @param int dowOffset
 * @return int
 */
Date.prototype.getWeek = function (dowOffset) {
  /*getWeek() was developed by Nick Baicoianu at MeanFreePath: http://www.meanfreepath.com */

  dowOffset = typeof dowOffset == "number" ? dowOffset : 0; //default dowOffset to zero
  var newYear = new Date(this.getFullYear(), 0, 1);
  var day = newYear.getDay() - dowOffset; //the day of week the year begins on
  day = day >= 0 ? day : day + 7;
  var daynum =
    Math.floor(
      (this.getTime() -
        newYear.getTime() -
        (this.getTimezoneOffset() - newYear.getTimezoneOffset()) * 60000) /
        86400000
    ) + 1;
  var weeknum;
  //if the year starts before the middle of a week
  if (day < 4) {
    weeknum = Math.floor((daynum + day - 1) / 7) + 1;
    if (weeknum > 52) {
      nYear = new Date(this.getFullYear() + 1, 0, 1);
      nday = nYear.getDay() - dowOffset;
      nday = nday >= 0 ? nday : nday + 7;
      /*if the next year starts before the middle of
              the week, it is week #1 of that year*/
      weeknum = nday < 4 ? 1 : 53;
    }
  } else {
    weeknum = Math.floor((daynum + day - 1) / 7);
  }
  return weeknum;
};

$(document).ready(function () {
  const pathologist = $("#pathologist");

  const pendingNumber = $("#pendingNumber");
  const pendingTable = $("#pendingTable");

  const currentNumber = $("#currentNumber");
  const currentTable = $("#currentTable");

  const unreviewNumber = $("#unreviewNumber");
  const unreviewTable = $("#unreviewTable");

  let data;

  let dateEnd = new Date().toLocaleDateString();
  $("#labelDateEnd").text(`Fecha por defecto: ${dateEnd}`);
  let dateStart = new Date();
  dateStart.setMonth(dateStart.getMonth() - 3);
  dateStart = dateStart.toLocaleDateString();
  $("#labelDateStart").text(`Fecha por defecto: ${dateStart}`);

  getData();

  /* FUNCTIONS */
  function dateDiff(a, b = null) {
    const date = new Date(a);
    const currentDate = b == null ? new Date() : new Date(b);
    const diffTime = currentDate - date;

    if (diffTime < 0) {
      return 0;
    }

    return Math.ceil(Math.abs(diffTime) / (1000 * 60 * 60 * 24));
  }

  function filterPending() {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.form_cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const is_assigned = analysis.report.patologo != null;

      return (
        !(form_closed || form_cancelled || manual_cancelled || manual_closed) &&
        is_assigned &&
        !pre_report_started
      );
    });
  }

  function filterCurrent() {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.form_cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const pre_report_ended = analysis.report.pre_report_ended;
      const is_assigned = analysis.report.patologo != null;

      return (
        !(form_closed || form_cancelled || manual_cancelled || manual_closed) &&
        is_assigned &&
        pre_report_started &&
        !pre_report_ended
      );
    });
  }

  function filterUnreview() {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.form_cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const pre_report_ended = analysis.report.pre_report_ended;
      const is_assigned = analysis.report.patologo != null;

      return (
        !(form_closed || form_cancelled || manual_cancelled || manual_closed) &&
        is_assigned &&
        pre_report_started &&
        pre_report_ended
      );
    });
  }

  function groupByMonth(data, key) {
    return data.reduce(function (rv, x) {
      (rv["workflow"][x[key]] = rv[x[key]] || []).push(x);
      return rv;
    }, {});
  }

  function initializePending() {
    const pending = filterPending();

    if ($.fn.DataTable.isDataTable("#pendingTable")) {
      pendingTable.DataTable().clear().destroy();
    }
    pendingNumber.text(pending.length);
    pendingTable.DataTable({
      data: pending,

      columns: [
        {
          data: "case.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "customer.name",
          name: "customer",
          type: "string",
          title: "Empresa",
        },
        {
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tinción",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patólogo",
          render: (data) => {
            return `${data.first_name[0]}${data.last_name[0]}`;
          },
        },
        {
          data: "samples",
          name: "samples",
          type: "number",
          title: "Cant. Muestras",
        },
        {
          data: "case.created_at",
          name: "entry_date",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            if (data == null || data == undefined) {
              return "";
            }
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_done_at",
          name: "derived_at",
          type: "num",
          title: "Derivación",
          render: (data) => {
            if (data == null || data == undefined) {
              return "";
            }
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_deadline",
          name: "derived_at",
          type: "num",
          title: "Plazo",
          render: (data) => {
            if (data == null || data == undefined) {
              return "";
            }
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_deadline",
          name: "delay",
          type: "num",
          title: "Atraso",
          render: (data) => {
            return dateDiff(data);
          },
        },
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });
  }

  function initializeCurrent() {
    if ($.fn.DataTable.isDataTable("#currentTable")) {
      currentTable.DataTable().clear().destroy();
    }

    const current = filterCurrent();
    currentNumber.text(current.length);
    currentTable.DataTable({
      data: current,

      columns: [
        {
          data: "case.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "customer.name",
          name: "customer",
          type: "string",
          title: "Empresa",
        },
        {
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tinción",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patólogo",
          render: (data) => {
            return `${data.first_name[0]}${data.last_name[0]}`;
          },
        },
        {
          data: "samples",
          name: "samples",
          type: "number",
          title: "Cant. Muestras",
        },
        {
          data: "case.created_at",
          name: "entry_date",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_done_at",
          name: "derived_at",
          type: "num",
          title: "Derivación",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_deadline",
          name: "derived_at",
          type: "num",
          title: "Plazo",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.pre_report_started_at",
          name: "delay",
          type: "num",
          title: "Inicio lectura",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.assignment_deadline",
          name: "delay",
          type: "num",
          title: "Atraso",
          render: (data) => {
            return dateDiff(data);
          },
        },
        {
          data: "report.pre_report_started_at",
          name: "delay",
          type: "num",
          title: "En Lectura",
          render: (data) => {
            return dateDiff(data);
          },
        },
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });
  }

  function initializeUnreview() {
    if ($.fn.DataTable.isDataTable("#unreviewTable")) {
      unreviewTable.DataTable().clear().destroy();
    }

    const unreview = filterUnreview();
    unreviewNumber.text(unreview.length);
    unreviewTable.DataTable({
      data: unreview,

      columns: [
        {
          data: "case.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "customer.name",
          name: "customer",
          type: "string",
          title: "Empresa",
        },
        {
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tinción",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patólogo",
          render: (data) => {
            return `${data.first_name[0]}${data.last_name[0]}`;
          },
        },
        {
          data: "samples",
          name: "samples",
          type: "number",
          title: "Cant. Muestras",
        },
        {
          data: "case.created_at",
          name: "entry_date",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.pre_report_started_at",
          name: "delay",
          type: "num",
          title: "Inicio lectura",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.pre_report_ended_at",
          name: "derived_at",
          type: "num",
          title: "Fin lectura",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report",
          name: "derived_at",
          type: "num",
          title: "Dias en lectura",
          render: (data) => {
            return dateDiff(
              data.pre_report_started_at,
              data.pre_report_ended_at
            );
          },
        },
        {
          data: "report.pre_report_ended_at",
          name: "delay",
          type: "num",
          title: "En Revisión",
          render: (data) => {
            return dateDiff(data);
          },
        },
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });
  }

  function updateView() {
    initializePending();
    initializeCurrent();
    initializeUnreview();
  }

  function getData() {
    const date_start = $("#dateStart").val();
    const date_end = $("#dateEnd").val();
    const user_id = $("#pathologist").val();
    Swal.fire({
      title: "Cargando...",
      allowOutsideClick: false,
    });
    Swal.showLoading();

    $.ajax(Urls["report:service"](), {
      data: JSON.stringify({ date_start, date_end, user_id }),

      method: "POST",

      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (_data, textStatus) => {
        Swal.close();
        data = _data;
        updateView();
      },
      error: (xhr, textStatus, error) => {
        Swal.fire({
          icon: "error",
        });
      },
    });
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

  /* EVENTS */

  $("#btnFilter").click(() => {
    getData();
  });
});
