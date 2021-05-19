/**
 * Returns the week number for this date.  dowOffset is the day of week the week
 * "starts" on for your locale - it can be from 0 to 6. If dowOffset is 1 (Monday),
 * the week returned is the ISO 8601 week number.
 * @param int dowOffset
 * @return int
 */
Date.prototype.getWeek = function (dowOffset) {
  /*getWeek() was developed by Nick Baicoianu at MeanFreePath: http://www.meanfreepath.com */

  dowOffset = typeof dowOffset == "int" ? dowOffset : 0; //default dowOffset to zero
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

  const efficiencyTable = $("#efficiencyTable");

  let averageEfficiency = echarts.init(
    document.getElementById("averageEfficiency")
  );

  let avgEffOptions = {
    tooltip: {
      formatter: "{a} <br/>{b} : {c}%",
    },
    series: [
      {
        type: "gauge",
        detail: { formatter: "{value}" },
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 7,
        splitNumber: 1,
        data: [{ value: 0, name: "Promedio Mensual" }],
        axisLine: {
          lineStyle: {
            color: [
              [0.57, "#FF6E76"],
              [0.7, "#58D9F9"],
              [1, "#7CFFB2"],
            ],
          },
        },
        splitLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        axisLabel: {
          show: false,
        },
        title: {
          show: false,
        },
        detail: {
          formatter: (value) => value.toFixed(1),
        },
        tooltip: {
          formatter: "{b}: {c}",
        },
      },
    ],
  };

  averageEfficiency.setOption(avgEffOptions);

  let monthlyEfficiency = echarts.init(
    document.getElementById("monthlyEfficiency")
  );

  let monthlyEffOptions = {
    xAxis: {
      type: "category",
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        data: [],
        type: "line",
        label: {
          show: true,
        },
      },
    ],
  };

  let barOptions = {
    xAxis: {
      type: "category",
      data: [],
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        data: [],
        type: "bar",
        label: {
          show: true,
        },
      },
    ],
  };

  monthlyEfficiency.setOption(monthlyEffOptions);

  let data;

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

  function filterDone() {
    return data.filter((analysis) => {
      const is_closed = analysis.workflow.form_closed;
      const manual_closed = analysis.report.manual_closing_date != null;
      const is_assigned = analysis.report.patologo != null;

      return (is_closed || manual_closed) && is_assigned;
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
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tincion",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patologo",
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
          title: "Derivacion",
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
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tincion",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patologo",
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
          title: "Derivacion",
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
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tincion",
        },
        {
          data: "user",
          name: "pathologist",
          type: "string",
          title: "Patologo",
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
          title: "En Revision",
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

  function initializeEfficiency() {
    if ($.fn.DataTable.isDataTable("#efficiencyTable")) {
      efficiencyTable.DataTable().clear().destroy();
    }

    const efficiency = filterDone();

    efficiencyTable.DataTable({
      data: efficiency,

      columns: [
        {
          data: "case.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "report.report_code",
          name: "reportCode",
          type: "string",
          title: "Informe",
        },
        {
          data: "exam.name",
          name: "service",
          type: "string",
          title: "Servicio",
        },
        {
          data: "user",
          name: "user",
          type: "num",
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
          data: "report.score_diagnostic",
          name: "score",
          type: "num",
          title: "Calificación",
          render: (data) => {
            if (data > 0) {
              return data;
            } else {
              return "S/I";
            }
          },
        },
        {
          data: "case.created_at",
          name: "createdAt",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "workflow.closed_at",
          name: "closedAt",
          type: "num",
          title: "Emisión",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });
  }

  function initializeCharts() {
    const efficiency = filterDone();

    // EFFICIENCY TABLE
    //
    // Get the lowest and highest week number so we can
    // loop in that range
    const startWeekEntry = _.minBy(efficiency, (item) => {
      const date = new Date(item.workflow.closed_at);
      return date.getWeek();
    });

    const endWeekEntry = _.maxBy(efficiency, (item) => {
      const date = new Date(item.workflow.closed_at);
      return date.getWeek();
    });

    const startWeek = new Date(startWeekEntry.workflow.closed_at).getWeek();
    const endWeek = new Date(endWeekEntry.workflow.closed_at).getWeek();

    const weekTr = $("#weeks");
    weekTr.empty();
    weekTr.append(`<th scope="col">Servicios</th>`);
    for (let i = startWeek; i < endWeek + 1; i++) {
      weekTr.append(`<th scope="col">${i}</th>`);
    }
    weekTr.append(`<th scope="col">Total</th>`);

    let doneByService = _.groupBy(efficiency, (item) => {
      return item.exam.name;
    });

    $("#serviceWeekTbody").empty();

    let serviceTotal = {};
    for (const service in doneByService) {
      const weekly = _.groupBy(doneByService[service], (item) => {
        const date = new Date(item.workflow.closed_at);
        return date.getWeek();
      });

      let row = "<tr>";
      row += `<td>${service}</td>`;

      let rowTotal = 0;

      for (let i = startWeek; i < endWeek + 1; i++) {
        if (i in weekly) {
          let totalSamples = 0;

          for (const item of weekly[i]) {
            totalSamples += parseInt(item.samples);
          }

          row += `<td>${totalSamples}</td>`;
          rowTotal += totalSamples;
          serviceTotal[i] =
            parseInt(serviceTotal[i] || 0) + parseInt(totalSamples);
        } else {
          row += `<td>N/A</td>`;
        }
      }

      if (isNaN(rowTotal)) {
        row += `<td>N/A</td>`;
      } else {
        row += `<td class="table-primary">${rowTotal}</td>`;
      }
      row += "</tr>";

      $("#serviceWeekTbody").append(row);
    }

    let row = "<tr class='table-primary'><td>Total</td>";
    for (let i = startWeek; i < endWeek + 1; i++) {
      if (isNaN(serviceTotal[i])) {
        row += `<td>N/A</td>`;
      } else {
        row += `<td>${serviceTotal[i]}</td>`;
      }
    }
    let grandTotal = Object.values(serviceTotal).reduce(
      (acc, curr) => acc + curr
    );

    if (isNaN(grandTotal)) {
      row += `<td>N/A</td>`;
    } else {
      row += `<td>${grandTotal}</td>`;
    }
    row += "</tr>";

    $("#serviceWeekTbody").append(row);

    // CHARTS

    let sumEffValue = 0;

    for (const row of efficiency) {
      sumEffValue += row.report.score_diagnostic;
    }

    const length = efficiency.filter((row) => row.report.score_diagnostic > 0)
      .length;

    const avg = sumEffValue / length;

    avgEffOptions.series[0].data[0].value = avg;
    averageEfficiency.setOption(avgEffOptions, true);

    const monthlyGrouped = _.groupBy(efficiency, (row) => {
      const date = new Date(row.workflow.closed_at);
      return `${date.getFullYear()}/${date.getMonth() + 1}`;
    });

    yAxis = [];

    for (const month in monthlyGrouped) {
      const group = monthlyGrouped[month];

      const length = group.filter((row) => row.report.score_diagnostic > 0)
        .length;

      let sumEffValue = 0;

      for (const row of group) {
        sumEffValue += row.report.score_diagnostic;
      }

      yAxis.push([month, (sumEffValue / length).toFixed(1)]);
    }

    monthlyEffOptions.series[0].data = yAxis.sort((a, b) => {
      const dateA = new Date(a[0]);
      const dateB = new Date(b[0]);
      return dateA - dateB;
    });
    monthlyEfficiency.setOption(monthlyEffOptions, true);
  }

  function updateView() {
    initializePending();
    initializeCurrent();
    initializeUnreview();
    initializeCharts();
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

    $.ajax(Urls["report:pathologist"](), {
      data: JSON.stringify({ date_start, date_end, user_id }),

      method: "POST",

      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (_data, textStatus) => {
        Swal.close();
        data = JSON.parse(_data);
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
