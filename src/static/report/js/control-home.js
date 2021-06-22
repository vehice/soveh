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

  let pendingPathologistOptions = {
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b} : {c} ({d}%)",
    },
    series: [
      {
        name: "Informes por Patologos",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2,
        },
        type: "pie",
        label: {
          show: false,
          position: "center",
        },
        emphasis: {
          label: {
            show: true,
            fontSize: "40",
            fontWeight: "bold",
          },
        },
        data: [],
      },
    ],
  };
  let pendingServiceOptions = {
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b} : {c} ({d}%)",
    },
    series: [
      {
        name: "Informes por Servicios",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2,
        },
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

  let pendingPathologist = echarts.init(
    document.getElementById("pendingPathologist")
  );
  let pendingService = echarts.init(document.getElementById("pendingService"));

  pendingPathologist.setOption(pendingPathologistOptions);
  pendingService.setOption(pendingServiceOptions);

  getData();

  /* FUNCTIONS */

  function filterUnassigned(data) {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const is_assigned = analysis.report.patologo != null;
      const requires_assignment = analysis.exam.pathologists_assignment;

      return (
        !(form_closed || manual_closed) &&
        !(form_cancelled || manual_cancelled) &&
        !is_assigned &&
        requires_assignment
      );
    });
  }

  function filterPending(data) {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const pre_report_ended = analysis.report.pre_report_ended;
      const is_assigned = analysis.report.patologo != null;
      const requires_assignment = analysis.exam.pathologists_assignment;

      return (
        !(form_closed || form_cancelled || manual_cancelled || manual_closed) &&
        is_assigned &&
        requires_assignment &&
        pre_report_started &&
        pre_report_ended
      );
    });
  }

  function filterDone(data) {
    return data.filter((analysis) => {
      const form_closed = analysis.workflow.form_closed;
      const form_cancelled = analysis.workflow.cancelled;
      const manual_cancelled = analysis.report.manual_cancelled_date != null;
      const manual_closed = analysis.report.manual_closing_date != null;
      const pre_report_started = analysis.report.pre_report_started;
      const pre_report_ended = analysis.report.pre_report_ended;
      const is_assigned = analysis.report.patologo != null;
      const requires_assignment = analysis.exam.pathologists_assignment;

      return (
        (form_closed || manual_closed) &&
        !(form_cancelled || manual_cancelled) &&
        is_assigned &&
        requires_assignment &&
        pre_report_started &&
        pre_report_ended
      );
    });
  }

  function initializeChart(data) {
    let total = [0, 0, 0];
    data.forEach((element, index) => {
      avgTimeOptions.series[index].data = element.map((row) => [
        row[0],
        row[1],
      ]);
      avgPercentOptions.series[index].data = element.map((row) => [
        row[0],
        row[2],
      ]);

      let elementTotal = 0;

      for (const month in element) {
        elementTotal += element[month][1];
      }

      total[index] += elementTotal;
    });

    avgTotalOptions.series[0].data = total;

    avgTimeMonth.setOption(avgTimeOptions, true);
    avgPercentMonth.setOption(avgPercentOptions, true);
    avgTotal.setOption(avgTotalOptions, true);
  }

  function initializePending() {
    pendingNumber.text(pending.length);

    if ($.fn.DataTable.isDataTable("#pendingTable")) {
      pendingTable.DataTable().clear().destroy();
    }

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
          name: "company",
          type: "string",
          title: "Empresa",
        },
        {
          data: "case.center",
          name: "center",
          type: "string",
          title: "Centro",
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
          title: "Patólogo",
          render: (data) => {
            return `${data.first_name[0]}${data.last_name[0]}`;
          },
        },
        {
          data: "samples",
          name: "samples",
          type: "string",
          title: "Cant. Muestras",
          render: (data) => {
            if (isNaN(data)) {
              return "N/A";
            } else {
              return data;
            }
          },
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
          data: "report.pre_report_ended_at",
          name: "pre_report_done",
          type: "num",
          title: "Pre-Informe Terminado",
          render: (data) => {
            const date = new Date(data);
            return date.toLocaleDateString();
          },
        },
        {
          data: "report.pre_report_ended_at",
          name: "delay",
          type: "num",
          title: "En Espera",
          render: (data) => {
            return dateDiff(data);
          },
        },
        {
          data: "report.created_at",
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

    const pendingByService = _.groupBy(pending, (item) => {
      return item.exam.name;
    });

    const pendingByPathologist = _.groupBy(pending, (item) => {
      const data = item.user;
      return `${data.first_name[0]}${data.last_name[0]}`;
    });

    for (const pathologist in pendingByPathologist) {
      pendingPathologistOptions.series[0].data.push({
        value: pendingByPathologist[pathologist].length,
        name: pathologist,
      });
    }

    for (const service in pendingByService) {
      pendingServiceOptions.series[0].data.push({
        value: pendingByService[service].length,
        name: service,
      });
    }

    pendingPathologist.setOption(pendingPathologistOptions, true);
    pendingService.setOption(pendingServiceOptions, true);
  }

  function initializeUnassigned() {
    unassignedNumber.text(unassigned.length);

    if ($.fn.DataTable.isDataTable("#unassignedTable")) {
      unassignedTable.DataTable().clear().destroy();
    }

    unassignedTable.DataTable({
      data: unassigned,

      columns: [
        {
          data: "case.no_caso",
          name: "case",
          type: "string",
          title: "Caso",
        },
        {
          data: "customer.name",
          name: "company",
          type: "string",
          title: "Empresa",
        },
        {
          data: "case.center",
          name: "center",
          type: "string",
          title: "Centro",
        },
        {
          data: "exam.name",
          name: "exam",
          type: "string",
          title: "Servicio",
        },
        {
          data: "samples",
          name: "samples",
          type: "number",
          title: "Cant. Muestras",
        },
        {
          data: "stain.abbreviation",
          name: "stain",
          type: "num",
          title: "Tinción",
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
      ],

      oLanguage: {
        sUrl: "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json",
      },
    });
  }

  function getChartObject(grouped, startKeys, endKeys) {
    let object = [];
    for (const month in grouped) {
      const group = grouped[month];
      const length = group.length;

      let monthValue = 0;
      let monthPercent = 0;
      for (const row of group) {
        const value = parseInt(
          dateDiff(row[startKeys[0]][startKeys[1]], row[endKeys[0]][endKeys[1]])
        );
        const total =
          parseInt(
            dateDiff(row.case.created_at, row.report.pre_report_started_at)
          ) +
          parseInt(
            dateDiff(
              row.report.pre_report_started_at,
              row.report.pre_report_ended_at
            )
          ) +
          parseInt(
            dateDiff(row.report.pre_report_ended_at, row.workflow.closed_at)
          );

        monthValue += value;
        monthPercent += (value / total) * 100;
      }
      object.push([
        month,
        parseInt((monthValue / length).toFixed(1)),
        parseInt((monthPercent / length).toFixed(1)),
      ]);
    }

    return object.sort((a, b) => {
      const dateA = new Date(a[0]);
      const dateB = new Date(b[0]);
      return dateA - dateB;
    });
  }

  function updateView() {
    initializePending();
    initializeUnassigned();

    let finishedByMonth = _.groupBy(finished, (row) => {
      const date = new Date(row.workflow.closed_at);
      return `${date.getFullYear()}/${date.getMonth() + 1}`;
    });

    let date = new Date();
    date.setMonth(date.getMonth() - 6);

    for (const group in finishedByMonth) {
      const groupDate = new Date(group);

      if (date > groupDate) {
        delete finishedByMonth[group];
      }
    }

    let stages = [
      getChartObject(
        finishedByMonth,
        ["case", "created_at"],
        ["report", "pre_report_started_at"]
      ),
      getChartObject(
        finishedByMonth,
        ["report", "pre_report_started_at"],
        ["report", "pre_report_ended_at"]
      ),
      getChartObject(
        finishedByMonth,
        ["report", "pre_report_ended_at"],
        ["workflow", "closed_at"]
      ),
    ];

    initializeChart(stages);
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

      success: (data, textStatus) => {
        Swal.close();
        pending = filterPending(data.queryset);
        unassigned = filterUnassigned(data.unassigned);
        finished = filterDone(data.queryset);
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
