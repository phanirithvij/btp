(function () {
  'use strict'

  feather.replace()

  // Graphs
  var ctx = document.getElementById('myChart')
  // eslint-disable-next-line no-unused-vars
  fetch('/stats/lastweek').then(d => d.json()).then(x => {
    var myChart = new Chart(ctx, x);
  });
  // console.log(myChart);
}());