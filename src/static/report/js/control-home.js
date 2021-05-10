$(document).ready(function () {
  const year = $("#year");
  const month = $("#month");
  const pendingNumber = $("#pendingNumber");
  const pendingTable = $("#pendingTable");
  const unassignedNumber = $("#unassignedNumber");
  const unassignedTable = $("#unassignedTable");

  let pending;
  let unassigned;
  let finished;

  let avgTimeOptions = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        label: {
          backgroundColor: "#6a7985",
        },
      },
    },
    legend: {
      data: [],
    },
    xAxis: [
      {
        type: "category",
        boundaryGap: false,
        data: [],
      },
    ],
    yAxis: [{ type: "value" }],
    series: [
      {
        name: "Ingreso hasta Lectura",
        type: "line",
        stack: "total",
        areaStyle: {},
        data: [],
      },
      {
        name: "Lectura hasta Pre-Informe",
        type: "line",
        stack: "total",
        areaStyle: {},
        data: [],
      },
      {
        name: "Pre-Informe hasta Cierre",
        type: "line",
        stack: "total",
        areaStyle: {},
        data: [],
      },
    ],
  };

  let avgPercentOptions = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        label: {
          backgroundColor: "#6a7985",
        },
      },
    },
    xAxis: {
      type: "category",
      data: [],
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        name: "Ingreso hasta Lectura",
        type: "bar",
        stack: "total",
        areaStyle: {},
        data: [],
      },
      {
        name: "Lectura hasta Pre-Informe",
        type: "bar",
        stack: "total",
        areaStyle: {},
        data: [],
      },
      {
        name: "Pre-Informe hasta Cierre",
        type: "bar",
        stack: "total",
        areaStyle: {},
        data: [],
      },
    ],
  };

  let avgTotalOptions = {
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b} : {c} ({d}%)",
    },
    series: [
      {
        name: "Porcentajes",
        type: "pie",
        label: {
          show: false,
        },
        data: [],
      },
    ],
  };

  let avgTimeMonth = echarts.init(document.getElementById("avgTimeMonth"));
  let avgTotal = echarts.init(document.getElementById("avgTotal"));
  let avgPercentMonth = echarts.init(
    document.getElementById("avgPercentMonth")
  );

  avgTimeMonth.setOption(avgTimeOptions);
  avgPercentMonth.setOption(avgPercentOptions);
  avgTotal.setOption(avgTotalOptions);

  getData();

  /* FUNCTIONS */

  function updateView() {
    pendingNumber.text(pending.length);

    if ($.fn.DataTable.isDataTable("#pendingTable")) {
      pendingTable.DataTable().clear().destroy();
    }

    pendingTable.DataTable({
      data: pending,

      columns: [
        {
          data: "case.fields.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "exam.fields.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.fields.abbreviation",
          name: "stain",
          type: "num",
          title: "Tincion",
        },
        {
          data: "user.fields",
          name: "pathologist",
          type: "string",
          title: "Patologo",
          render: (data) => {
            return `${data.first_name[0]}${data.last_name[0]}`;
          },
        },
        {
          data: "case.fields.created_at",
          name: "entry_date",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.fields.assignment_done_at",
          name: "derived_at",
          type: "num",
          title: "Derivacion",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.fields.assignment_deadline",
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

    unassignedNumber.text(unassigned.length);

    if ($.fn.DataTable.isDataTable("#unassignedTable")) {
      unassignedTable.DataTable().clear().destroy();
    }

    unassignedTable.DataTable({
      data: unassigned,

      columns: [
        {
          data: "case.fields.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "exam.fields.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "stain.fields.abbreviation",
          name: "stain",
          type: "num",
          title: "Tincion",
        },
        {
          data: "case.fields.created_at",
          name: "entry_date",
          type: "string",
          title: "Ingreso",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.fields.created_at",
          name: "delay",
          type: "num",
          title: "En Sistema",
          render: (data) => {
            return dateDiff(data);
          },
        },
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });

    const finishedByMonth = _.groupBy(finished, (row) => {
      const date = new Date(row.workflow.fields.closed_at);
      return `${date.getFullYear()}/${date.getMonth() + 1}`;
    });

    let months = [];
    let entryToRead = {
      percent: [],
      value: [],
    };
    let readToReview = {
      percent: [],
      value: [],
    };
    let reviewToSend = {
      percent: [],
      value: [],
    };

    for (const month in finishedByMonth) {
      const group = finishedByMonth[month];
      const length = group.length;

      let currentEtR = 0;
      let currentRtR = 0;
      let currentRtS = 0;

      let currentEtRPercent = 0;
      let currentRtRPercent = 0;
      let currentRtSPercent = 0;
      for (const row of group) {
        const rowEtR = parseInt(
          dateDiff(
            row.case.fields.created_at,
            row.report.fields.pre_report_started_at
          )
        );
        const rowRtR = parseInt(
          dateDiff(
            row.report.fields.pre_report_started_at,
            row.report.fields.pre_report_ended_at
          )
        );
        const rowRtS = parseInt(
          dateDiff(
            row.report.fields.pre_report_ended_at,
            row.workflow.fields.closed_at
          )
        );
        const rowTotal = rowEtR + rowRtR + rowRtS;

        currentRtR += rowRtR;
        currentEtR += rowEtR;
        currentRtS += rowRtS;

        currentRtRPercent += (rowRtR / rowTotal) * 100;
        currentEtRPercent += (rowEtR / rowTotal) * 100;
        currentRtSPercent += (rowRtS / rowTotal) * 100;
      }

      months.push(month);
      entryToRead.percent.push((currentEtRPercent / length).toFixed(1));
      readToReview.percent.push((currentRtRPercent / length).toFixed(1));
      reviewToSend.percent.push((currentRtSPercent / length).toFixed(1));

      entryToRead.value.push((currentEtR / length).toFixed(1));
      readToReview.value.push((currentRtR / length).toFixed(1));
      reviewToSend.value.push((currentRtS / length).toFixed(1));
    }

    avgTimeOptions.legend.data = months;
    avgTimeOptions.xAxis[0].data = months;
    avgTimeOptions.series[0].data = entryToRead.value;
    avgTimeOptions.series[1].data = readToReview.value;
    avgTimeOptions.series[2].data = reviewToSend.value;

    avgPercentOptions.xAxis.data = months;
    avgPercentOptions.series[0].data = entryToRead.percent;
    avgPercentOptions.series[1].data = readToReview.percent;
    avgPercentOptions.series[2].data = reviewToSend.percent;

    avgTotalOptions.series[0].data.length = 0;

    avgTotalOptions.series[0].data.push({
      value: entryToRead.value.reduce(
        (acc, current) => parseInt(acc) + parseInt(current)
      ),
      name: "Ingreso hasta Lectura",
    });

    avgTotalOptions.series[0].data.push({
      value: readToReview.value.reduce(
        (acc, current) => parseInt(acc) + parseInt(current)
      ),
      name: "Lectura hasta Pre-Informe",
    });

    avgTotalOptions.series[0].data.push({
      value: reviewToSend.value.reduce(
        (acc, current) => parseInt(acc) + parseInt(current)
      ),
      name: "Pre-Informe hasta Cierre",
    });

    avgTimeMonth.setOption(avgTimeOptions, true);
    avgPercentMonth.setOption(avgPercentOptions, true);
    avgTotal.setOption(avgTotalOptions, true);
  }

  function mapData(data, key) {
    return data[key].map((row) => {
      return {
        report: JSON.parse(row.report)[0],
        exam: JSON.parse(row.exam)[0],
        case: JSON.parse(row.case)[0],
        user: JSON.parse(row.user)[0],
        stain: JSON.parse(row.stain)[0],
        workflow: JSON.parse(row.workflow)[0],
      };
    });
  }

  function dateDiff(a, b = null) {
    const date = new Date(a);
    const currentDate = b == null ? new Date() : new Date(b);
    const diffTime = currentDate - date;

    if (diffTime < 0) {
      return 0;
    }

    return Math.ceil(Math.abs(diffTime) / (1000 * 60 * 60 * 24));
  }

  function getData() {
    Swal.fire({
      title: "Cargando...",
      allowOutsideClick: false,
    });
    Swal.showLoading();

    $.ajax(Urls["report:control"](), {
      method: "POST",

      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },

      contentType: "application/json; charset=utf-8",

      success: (_data, textStatus) => {
        Swal.close();
        // REFACTOR THIS IF DJANGO REST FRAMEWORK IS USED
        pending = mapData(_data, "pending");
        unassigned = mapData(_data, "unassigned");
        finished = mapData(_data, "finished");
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
