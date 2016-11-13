window.onload = function () {
  var ticker = '{{ticker}}';
    var chart = new CanvasJS.Chart("chartContainer",
    {
      zoomEnabled: true,
      title:{
        text: ticker
      },
      axisX:{
        labelAngle: 30
      },
      
      axisY :{
        includeZero:false
      },
      
      data: data  // random generator below
      
    });

    chart.render();
  }
  
   var limit = 100000;    //increase number of dataPoints by increasing this
   
   var y = 0;
   var data = []; var dataSeries = { type: "line" };
   var dataPoints = [];
   for (var i = 0; i < limit; i += 1) {
    y += (Math.random() * 10 - 5);
    dataPoints.push({
      x: i - limit / 2,
      y: y
    });
  }
  dataSeries.dataPoints = dataPoints;
  data.push(dataSeries);
  
