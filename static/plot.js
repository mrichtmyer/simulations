var trace1 = {
    x: [1, 2, 3, 4],
    y: [10, 9, 7, 6],
    type: 'scatter',
    name: 'Line 1'
  };
  
  var trace2 = {
    x: [1, 2, 3, 4],
    y: [3, 4, 4, 5],
    type: 'scatter',
    name: 'Line 2'
  };

  var trace3 = {
    x: [1, 2, 3, 4],
    y: [5, 6, 6, 5],
    type: 'scatter',
    fill: 'tonexty',
    name: 'Line 3'
  };

  var trace4 = {
      x: [1, 2, 3, 4],
      y: [7, 7, 6.5, 5.5],
      type: 'scatter',
      name: 'Line 4'
  };


  
  var data = [trace1, trace3, trace4];
  
  Plotly.newPlot('plot', data);



  d3.json('/site_data')
    .then(function(data){

    console.log(data.screen_pass);
    //console.log(data);
    //console.log(data.pre_screen.lower);

});