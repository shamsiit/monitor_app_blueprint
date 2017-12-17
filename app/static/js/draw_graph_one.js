function draw_demo_graph(url,id_name){

            //console.log(host_name);

             function getDateTimeFromTimestamp(unixTimeStamp) {
    var date = new Date(unixTimeStamp);
    return ('0' + date.getDate()).slice(-2) + '/' + ('0' + (date.getMonth() + 1)).slice(-2) + '/' + date.getFullYear() + ' ' + ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2);
  }

  var id = "#"+ id_name;

  var unit = "";

  console.log(id);

  var w = $(id).width();
  var h = 250;

var margin = {top: 10, right: 40, bottom: 100, left: 40},
    margin2 = {top: 180, right: 40, bottom: 20, left: 40},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom,
    height2 = h - margin2.top - margin2.bottom;
 
var color = d3.scale.category10();
 
var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
 
var x = d3.time.scale().range([0, width]),
    x2 = d3.time.scale().range([0, width]),
    y = d3.scale.linear().range([height, 0]),
    y2 = d3.scale.linear().range([height2, 0]);
 
var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(2),
    xAxis2 = d3.svg.axis().scale(x2).orient("bottom").ticks(2),
    yAxis = d3.svg.axis().scale(y).orient("left");
 
var brush = d3.svg.brush()
    .x(x2)
    .on("brush", brush);
 
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

  var data = [];
  
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
  var sources = color.domain().map(function(name) {
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
        .style("stroke", "green") //.style("stroke", function(d) {return color('green');})
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
        .style("stroke", "green") //.style("stroke", function(d) {return color('green');})
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

        }


       