/* Heatmap of failure probabilities by (well_id, hour_of_day) pairs */
function drillHeatmap(data){
  
  document.getElementById("pthresh").value = ""+data[0].p_thresh;
  //var f1 = document.createElement("form");
  //var i = document.createElement("input");
  //i.type = "text";

  d3.select("#heatmap").append("h4").html("Wells with P(Failure) \>= "+ data[0].p_thresh +"\<br>");

  var margin = { top: 100, right: 0, bottom: 100, left: 100 },
        width = 1400 - margin.left - margin.right;
    var well_ids = d3.set(data.map(function(d){
                         return d.well_id;
                     }
                   )).values();
    var times = ["12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a"];
    var gridSize = 35,
        height = well_ids.length*gridSize,
        //buckets = 9,
        buckets = 10,
        colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58", "#000000"], // alternatively colorbrewer.YlGnBu[9]
        legendElementWidth = gridSize*times.length/buckets;

    var colorScale = d3.scale.quantile()
        //.domain([0, d3.max(data, function (d) { return d.prob; })])
        .domain([0, 1.0])
        .range(colors);

    /* Clear existing elements */
    d3.select("#hmap_spinner").html("")

    /* Start painting heatmap */
    var svg = d3.select("#heatmap").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var dayLabels = svg.selectAll(".dayLabel")
        .data(well_ids)
        .enter().append("text")
        .text(function (d) { return "well_"+d; })
        .attr("x", 0)
        .attr("y", function (d, i) { return i * gridSize; })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
        .attr("class", function (d, i) { return "dayLabel mono axis"; });

    var timeLabels = svg.selectAll(".timeLabel")
        .data(times)
        .enter().append("text")
        .text(function(d) { return d; })
        .attr("x", function(d, i) { return i * gridSize; })
        .attr("y", 0)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + gridSize / 2 + ", -6)")
        .attr("class", function(d, i) { return ((i >= 8 && i <= 17) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

    var heatMap = svg.selectAll(".hour")
        .data(data)
        .enter().append("rect")
        .attr("x", function(d) { return (d.hour_across_dates) * gridSize; })
        .attr("y", function(d) { return (d.rank_id-1) * gridSize; })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "hour bordered")
        .attr("width", gridSize)
        .attr("height", gridSize)
        .style("fill", colors[0]);

    heatMap.transition().duration(1000)
      .style("fill", function(d) { return colorScale(d.prob); });

    heatMap.append("title").text(function(d) { return d.prob; });

    /* Drill-downs */
    heatMap.on('click', function(d) { invokeTimeSeries(d.well_id, d.yr, d.mth, d.dt, d.hour, d.prob);});

    var legend = svg.selectAll(".legend")
        .data([0].concat(colorScale.quantiles()), function(d) { return d; })
        .enter().append("g")
        .attr("class", "legend");

    legend.append("rect")
    .attr("x", function(d, i) { return legendElementWidth * i; })
    .attr("y", -1.5*gridSize)
    .attr("width", legendElementWidth)
    .attr("height", gridSize / 2)
    .style("fill", function(d, i) { return colors[i]; });

    legend.append("text")
    .attr("class", "mono")
    .text(function(d) { return "≥ " + Number(d).toFixed(2); })
    .attr("x", function(d, i) { return legendElementWidth * i; })
    .attr("y", -2.0*gridSize);
}
