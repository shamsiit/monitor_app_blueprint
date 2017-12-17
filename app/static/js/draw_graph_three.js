function draw_detail_graph(url,url2,url3,id_name){

  d3.select("svg").remove();

            //console.log(host_name);

             function getDateTimeFromTimestamp(unixTimeStamp) {
    var date = new Date(unixTimeStamp);
    return ('0' + date.getDate()).slice(-2) + '/' + ('0' + (date.getMonth() + 1)).slice(-2) + '/' + date.getFullYear() + ' ' + ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2);
  }

  var id = "#"+ id_name;

  var unit = "";

  console.log(id);

  var w = $(id).width();
  var h = 300;
  var sources;
  var data = [];
  var number_of_prediction = 10;
  var algo = 'arima';

var margin = {top: 10, right: 40, bottom: 100, left: 60},
    margin2 = {top: 230, right: 40, bottom: 20, left: 60},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom,
    height2 = h - margin2.top - margin2.bottom;
 
var color = d3.scale.category10();
 
var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
 
var x = d3.time.scale().range([0, width]),
    x2 = d3.time.scale().range([0, width]),
    y = d3.scale.linear().range([height, 0]),
    y2 = d3.scale.linear().range([height2, 0]);
 
var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(5),
    xAxis2 = d3.svg.axis().scale(x2).orient("bottom").ticks(5),
    yAxis = d3.svg.axis().scale(y).orient("left");
 
var brush = d3.svg.brush()
    .x(x2)
    .on("brush", brush);

var brush2 = d3.svg.brush()
    .x(x2)
    .on("brushend",brushend);   
 
var line = d3.svg.line()
    .defined(function(d) { return !isNaN(d.mean); })
    .interpolate("cubic")
    .x(function(d) { return x(d.time); })
    .y(function(d) { return y(d.mean); });
 
var line2 = d3.svg.line()
    .defined(function(d) { return !isNaN(d.mean); })
    .interpolate("cubic")
    .x(function(d) {return x2(d.time); })
    .y(function(d) {return y2(d.mean); });
 
var svg = d3.select(id).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);
 
svg.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width)
    .attr("height", height);

 
var focus = svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      
var context = svg.append("g")
  .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");
 
d3.json(url, function(error, dat) {
  
  var data_pre_procces = dat.results;

  unit = data_pre_procces["unit"];
  
  for(var i=0;i<data_pre_procces["time"].length;i++){
       var d = {}
       d.time = data_pre_procces["time"][i];
       d.mean = data_pre_procces["mean"][i];
       //console.log(data_pre_procces["time"][i]);
       data.push(d);
  }

  //console.log(data);
  
  color.domain(d3.keys(data_pre_procces).filter(function(key) {console.log(key); return key!="name"; }));
 
/*    data.forEach(function(d) {
      d.time = getDateTimeFromTimestamp(d.time*1000);
    });
*/
  sources = color.domain().map(function(name) {
      //console.log(data);
      return {
        name: name,
        values: data.map(function(d) {
          //console.log(d['mean']);
          return {time: +d['time'], mean: +d['mean']};
        })
      };
    });


    //console.log(sources);
 
    x.domain(d3.extent(data, function(d) { return d.time; }));
    y.domain([0,
              d3.max(sources, function(c) { return d3.max(c.values, function(v) { return v.mean; }); }) ]);
    x2.domain(x.domain());
    y2.domain(y.domain());

    xAxis.tickFormat(function(d){  return d3.time.format('%b %d %H:%M')(new Date(d*1000)); });

    xAxis2.tickFormat(function(d){  return d3.time.format('%b %d %H:%M')(new Date(d*1000)); });
    yAxis.tickFormat(function(d){ return d+""+unit; });

    //console.log(sources);
    
    var focuslineGroups = focus.selectAll("g")
        .data(sources)
      .enter().append("g");
      
    var focuslines = focuslineGroups.append("path")
        .attr("class","line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", "green")
        .attr("clip-path", "url(#clip)");
    
    focus.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
 
    focus.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    focus.append("g")
        .attr("class", "x brush")
        .call(brush2)
      .selectAll("rect")
        .attr("y", -6)
        .attr("height", height + 7)
        .on("mousemove", mousemove);

    var bisectDate = d3.bisector(function(d) { return d.time; }).left;


    var tempFocus = svg.append("g")
      .attr("class", "focus");     
      
      //.style("display", "none");

   tempFocus.append("circle")
      .attr("r", 4.5)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

   tempFocus.append("text")
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(data, x0, 1),
        d0 = data[i - 1],
        d1 = data[i],
        d = x0 - d0.time > d1.time - x0 ? d1 : d0;
        tempFocus
        .attr("transform", "translate(" + x(d.time) + "," + y(d.mean) + ")");

        var t = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(parseInt(d.time)*1000));
        
        tempFocus.select("text").text(d.mean+""+unit+" , "+t);
  }  
        
    var contextlineGroups = context.selectAll("g")
        .data(sources)
      .enter().append("g");
    
    var contextLines = contextlineGroups.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line2(d.values); })
        .style("stroke", "green")
        .attr("clip-path", "url(#clip)");
 
    context.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis2);
 
    context.append("g")
        .attr("class", "x brush")
        .call(brush)
      .selectAll("rect")
        .attr("y", -6)
        .attr("height", height2 + 7);
        
        
});
 
function brush() {
  x.domain(brush.empty() ? x2.domain() : brush.extent());
  focus.selectAll("path.line").attr("d",  function(d) {return line(d.values)});
  focus.select(".x.axis").call(xAxis);
  focus.select(".y.axis").call(yAxis);
}

function brushend(){
    var s = d3.event.target.extent();
    var d1 = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(s[0]*1000));
    var d2 = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(s[1]*1000));

    if(d1 != d2){
      re_draw(url,url2,url3,id_name,d1,d2);
    }
    

}

d3.select("#number_of_prediction").on("change",function(){

    number_of_prediction = this.options[this.selectedIndex].value;
    var arr = url3.split("/");
    arr[4] = algo;
    arr[5] = number_of_prediction;
    str = "";
    for(var i=0;i<arr.length;i++){
           str = str+"/"+arr[i];
    }

    var url = str.substring(0, 0) + '' + str.substring(0+1);
    console.log(url);
    drawForecastLine(sources,data,url);
  });

//start forecast
d3.select("#forecastbtn").on("change",function(){
    algo = this.options[this.selectedIndex].value;
    var arr = url3.split("/");
    arr[4] = algo;
    arr[5] = number_of_prediction;
    str = "";
    for(var i=0;i<arr.length;i++){
           str = str+"/"+arr[i];
    }

    var url = str.substring(0, 0) + '' + str.substring(0+1);
    console.log(url);
    drawForecastLine(sources,data,url);
  });

//end forecast



function re_draw(url,url2,url3,id_name,from_date,to_date){

  d3.select("svg").remove();

  var arr = url2.split("/");
    console.log(arr[6]+"    "+arr[7]);
    arr[6] = from_date;
    arr[7] = to_date;
    var str = "";
    for(var i=0;i<arr.length;i++){
      str = str+"/"+arr[i];
    }

    urlNew = str.substring(0, 0) + '' + str.substring(0+1);

    console.log(urlNew);


  var id = "#"+ id_name;

  var unit = "";

  console.log(id);

  var w = $(id).width();
  var h = 300;

var margin = {top: 10, right: 40, bottom: 100, left: 60},
    margin2 = {top: 230, right: 40, bottom: 20, left: 60},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom,
    height2 = h - margin2.top - margin2.bottom;

var data = []; 
var sources;
var number_of_prediction = 10;   
var algo = 'arima';
 
var color = d3.scale.category10();
 
var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
 
var x = d3.time.scale().range([0, width]),
    x2 = d3.time.scale().range([0, width]),
    y = d3.scale.linear().range([height, 0]),
    y2 = d3.scale.linear().range([height2, 0]);
 
var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(5),
    xAxis2 = d3.svg.axis().scale(x2).orient("bottom").ticks(5),
    yAxis = d3.svg.axis().scale(y).orient("left");
 
var brush = d3.svg.brush()
    .x(x2)
    .on("brush", brush);

var brush2 = d3.svg.brush()
    .x(x2)
    .on("brushend",brushend);    
 
var line = d3.svg.line()
    .defined(function(d) { return !isNaN(d.mean); })
    .interpolate("cubic")
    .x(function(d) { return x(d.time); })
    .y(function(d) { return y(d.mean); });
 
var line2 = d3.svg.line()
    .defined(function(d) { return !isNaN(d.mean); })
    .interpolate("cubic")
    .x(function(d) {return x2(d.time); })
    .y(function(d) {return y2(d.mean); });
 
var svg = d3.select(id).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);
 
svg.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width)
    .attr("height", height);

 
var focus = svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
      
var context = svg.append("g")
  .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");
 
d3.json(urlNew, function(error, dat) {
  
  var data_pre_procces = dat.results;

  unit = data_pre_procces["unit"];

  
  
  for(var i=0;i<data_pre_procces["time"].length;i++){
       var d = {}
       d.time = data_pre_procces["time"][i];
       d.mean = data_pre_procces["mean"][i];
       //console.log(data_pre_procces["time"][i]);
       data.push(d);
  }

  //console.log(data);
  
  color.domain(d3.keys(data_pre_procces).filter(function(key) {console.log(key); return key!="name"; }));
 
/*    data.forEach(function(d) {
      d.time = getDateTimeFromTimestamp(d.time*1000);
    });
*/
  sources = color.domain().map(function(name) {
      //console.log(data);
      return {
        name: name,
        values: data.map(function(d) {
          //console.log(d['mean']);
          return {time: +d['time'], mean: +d['mean']};
        })
      };
    });


    //console.log(sources);
 
    x.domain(d3.extent(data, function(d) { return d.time; }));
    y.domain([0,
              d3.max(sources, function(c) { return d3.max(c.values, function(v) { return v.mean; }); }) ]);
    x2.domain(x.domain());
    y2.domain(y.domain());

    xAxis.tickFormat(function(d){  return d3.time.format('%b %d %H:%M')(new Date(d*1000)); });

    xAxis2.tickFormat(function(d){  return d3.time.format('%b %d %H:%M')(new Date(d*1000)); });

    yAxis.tickFormat(function(d){  return d+""+unit; });

    //console.log(sources);
    
    var focuslineGroups = focus.selectAll("g")
        .data(sources)
      .enter().append("g");
      
    var focuslines = focuslineGroups.append("path")
        .attr("class","line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", "green")//.style("stroke", function(d) {return color('green');})
        .attr("clip-path", "url(#clip)");
    
    focus.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
 
    focus.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    focus.append("g")
        .attr("class", "x brush")
        .call(brush2)
      .selectAll("rect")
        .attr("y", -6)
        .attr("height", height + 7)
        .on("mousemove", mousemove);   

    var bisectDate = d3.bisector(function(d) { return d.time; }).left;


    var tempFocus = svg.append("g")
      .attr("class", "focus");     
      
      //.style("display", "none");

   tempFocus.append("circle")
      .attr("r", 4.5)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

   tempFocus.append("text")
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(data, x0, 1),
        d0 = data[i - 1],
        d1 = data[i],
        d = x0 - d0.time > d1.time - x0 ? d1 : d0;
        tempFocus
        .attr("transform", "translate(" + x(d.time) + "," + y(d.mean) + ")");

        var t = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(parseInt(d.time)*1000));

        tempFocus.select("text").text(d.mean+""+unit+" , "+t);
  }    

        
    var contextlineGroups = context.selectAll("g")
        .data(sources)
      .enter().append("g");
    
    var contextLines = contextlineGroups.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line2(d.values); })
        .style("stroke", "green")  //.style("stroke", function(d) {return color('green');})
        .attr("clip-path", "url(#clip)");
 
    context.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis2);
 
    context.append("g")
        .attr("class", "x brush")
        .call(brush)
      .selectAll("rect")
        .attr("y", -6)
        .attr("height", height2 + 7);
        
        
});

function brush() {
  x.domain(brush.empty() ? x2.domain() : brush.extent());
  focus.selectAll("path.line").attr("d",  function(d) {return line(d.values)});
  focus.select(".x.axis").call(xAxis);
  focus.select(".y.axis").call(yAxis);
}

d3.select("#number_of_prediction").on("change",function(){

    number_of_prediction = this.options[this.selectedIndex].value;
    var arr = url3.split("/");
    arr[4] = algo;
    arr[5] = number_of_prediction;
    str = "";
    for(var i=0;i<arr.length;i++){
           str = str+"/"+arr[i];
    }

    var url = str.substring(0, 0) + '' + str.substring(0+1);
    console.log(url);
    drawForecastLine(sources,data,url);
  });

d3.select("#forecastbtn").on("change",function(){
    algo = this.options[this.selectedIndex].value;
    var arr = url3.split("/");
    arr[4] = algo;
    arr[5] = number_of_prediction;
    str = "";
    for(var i=0;i<arr.length;i++){
           str = str+"/"+arr[i];
    }

    var url = str.substring(0, 0) + '' + str.substring(0+1);
    console.log(url);
    drawForecastLine(sources,data,url);
  });
//end forecast

}

function drawForecastLine(sources,data,url){

var forecastData = [];  
var brushForecast = d3.svg.brush()
    .x(x2)
    .on("brush", brushForecastFunc);
d3.select("svg").remove();

var svg = d3.select("#maingraph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);    
 
svg.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width)
    .attr("height", height);

var focus = svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");  

var focusPrev = svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var context = svg.append("g")
  .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");  
  
var contextForecast = svg.append("g")
  .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

d3.json(url, function(error, dat) { 
 
   var data_pre_procces = dat.results;
   
   for(var i=0;i<data_pre_procces["time"].length;i++){
        var d = {}
        d.time = data_pre_procces["time"][i];
        d.mean = data_pre_procces["mean"][i];
        forecastData.push(d);
   }


  color.domain(d3.keys(data_pre_procces).filter(function(key) {return key!="name"; }));
  var sourcesForecast = color.domain().map(function(name) {
      //console.log(data);
      return {
        name: name,
        values: forecastData.map(function(d) {
          //console.log(d['mean']);
          return {time: +d['time'], mean: +d['mean']};
        })
      };
    });

  // var dataMin = d3.min(data, function(d) { return d.mean; });
   var dataMax = d3.max(data, function(d) { return d.mean; });
  // var forecastDataMin = d3.min(forecastData, function(d) { return d.mean; });
   var forecastDataMax = d3.max(forecastData, function(d) { return d.mean; });
  // var yMin = dataMin < forecastDataMin ? dataMin : forecastDataMin;
   var yMax = dataMax > forecastDataMax ? dataMax : forecastDataMax;

    x.domain(d3.extent(forecastData, function(d) { return d.time; }));
    y.domain([0, yMax]);
    x2.domain(x.domain());
    y2.domain(y.domain());

  var focuslineGroups = focus.selectAll("g")
        .data(sourcesForecast)
      .enter().append("g");

  var focuslines = focuslineGroups.append("path")
        .attr("class","line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", "red")
        .attr("clip-path", "url(#clip)");
  
  var focuslineGroupsPrev = focusPrev.selectAll("g")
        .data(sources)
      .enter().append("g");

  var focuslinesPrev = focuslineGroupsPrev.append("path")
        .attr("class","line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", "green")
        .attr("clip-path", "url(#clip)");      

  focus.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

  focus.append("g")
        .attr("class", "y axis")
        .call(yAxis);

  var contextlineGroups = context.selectAll("g")
        .data(sources)
      .enter().append("g");
    
    var contextLines = contextlineGroups.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line2(d.values); })
        .style("stroke", "green")
        .attr("clip-path", "url(#clip)");

    var contextlineGroupsForecast = contextForecast.selectAll("g")
        .data(sourcesForecast)
      .enter().append("g");

    var contextLinesForecast = contextlineGroupsForecast.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line2(d.values); })
        .style("stroke", "red")
        .attr("clip-path", "url(#clip)");      

 
    context.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis2);
 
  
    context.append("g")
        .attr("class", "x brush")
        .call(brushForecast)
      .selectAll("rect")
        .attr("y", -6)
        .attr("height", height2 + 7);      


  //start mouseover tooltip
  var prevTooltip = svg.append("g")
      .attr("class", "focus");     

  prevTooltip.append("circle")
      .attr("r", 4.5)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  prevTooltip.append("text")
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


  var forecastTooltip = svg.append("g")
      .attr("class", "focus");     

  forecastTooltip.append("circle")
      .attr("r", 4.5)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  forecastTooltip.append("text")
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");      

  svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .on("mousemove", mousemove);

 var bisectDate = d3.bisector(function(d) { return d.time; }).left;

function mousemove() {
         var x0 = x.invert(d3.mouse(this)[0]);  
         var i = bisectDate(data, x0, 1);
         if(i < data.length){
          var d0 = data[i - 1],
          d1 = data[i],
          d = x0 - d0.date > d1.date - x0 ? d1 : d0;
          prevTooltip.attr("transform", "translate(" + x(d.time) + "," + y(d.mean) + ")");
          var t = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(parseInt(d.time)*1000));
          prevTooltip.select("text").text(d.mean+""+unit+" , "+t);
         }
         
         var i_forecast= bisectDate(forecastData, x0, 1),
           d0_forecast = forecastData[i_forecast - 1],
           d1_forecast = forecastData[i_forecast],
           d_forecast = x0 - d0_forecast.date > d1_forecast.date - x0 ? d1_forecast : d0_forecast;
           
           forecastTooltip.attr("transform", "translate(" + x(d_forecast.time) + "," + y(d_forecast.mean) + ")");
           var t1 = d3.time.format('%Y-%m-%d %H:%M:%S')(new Date(parseInt(d_forecast.time)*1000));
           forecastTooltip.select("text").text(d_forecast.mean+""+unit+" , "+t1);
        }
  //end mouseover tooltip     
                
  });

function brushForecastFunc() {
  x.domain(brushForecast.empty() ? x2.domain() : brushForecast.extent());
  focus.selectAll("path.line").attr("d",  function(d) {return line(d.values)});
  focusPrev.selectAll("path.line").attr("d",  function(d) {return line(d.values)});

  focus.select(".x.axis").call(xAxis);
  focus.select(".y.axis").call(yAxis);
  }

}
}


        