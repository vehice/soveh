$(document).ready(function () {
  const tblProcess = $("tableProcess").DataTable({
    columns: [
      { title: "Caso", name: "case", data: 0 },
      { title: "Identificación", name: "identification", data: 0 },
      { title: "# Unidad", name: "unit", data: 0 },
      { title: "# Cassette", name: "cassette", data: 0 },
      { title: "Organos", name: "organs", data: 0 },
      { title: "Fecha Recepcion", name: "reception", data: 0 },
    ],
  });
});

function onChangeProcess(event) {
  const selected = event.target.value;
}
