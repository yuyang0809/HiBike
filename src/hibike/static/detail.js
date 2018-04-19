function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string','x')
    data.addColumn('number', 'Available bikes');
    data.addColumn('number', 'Available bike stands');
    data.addRows(alldata);

  var options = {
    title: 'Past 24 hours',
    hAxis: {
      title: 'Time',
      showTextEvery: 2
    },
    vAxis: {
      viewWindow:{min:-5},
      title: 'Numbers'
    },
    lineWidth: 2,
    width:800,
    height:400,
    pointSize: 5,
    viewWindow: {min: 0, max: 'auto'},
    gridlines: { count: 3},
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

  chart.draw(data, options);
}