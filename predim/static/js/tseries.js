/* 
  Drilldown functionality for heatmaps
  Show time-series plots for various well parameters
*/

function tseries(div_id, data, title, yaxis_label, line_color) {
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.time.scale().range([0, width]);

    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(d3.time.hours, 1);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.ts_utc); })
        .y(function(d) { return y(d.value); });

    /* Draw the series plot on the div element */
    var svg = d3.select("#"+div_id).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function(d) {
        d.ts_utc = d3.time.format.iso.parse(d.ts_utc);
        d.value = +d.value;
    });

    x.domain(d3.extent(data, function(d) { return d.ts_utc; }));
    y.domain(d3.extent(data, function(d) { return d.value; }));

    svg.append("g")
     .attr("class", "x axis")
     .attr("transform", "translate(0," + height + ")")
     .call(xAxis);

    svg.append("g")
     .attr("class", "y axis")
     .call(yAxis)
     .append("text")
     .attr("transform", "rotate(-90)")
     .attr("y", 6)
     .attr("dy", ".71em")
     .style("text-anchor", "end")
     .text(yaxis_label);

    svg.append("path")
     .datum(data)
     .attr("class", "line")
     .attr("d", line);
     //.attr("style", "fill: none; stroke-width: 2px; stroke:"+line_color);
}

function invokeTimeSeries(well_id, hour) {
    d3.select("#tseries").html("");
    d3.select("#tseries").html("<h1 class=\"text-center\">Well Features : Series Plots</h1>"+"<br>"+  
        "<span id=\"tseries_spinner\"><img src='../img/spinner.gif' class=\"customer-spinner\"></span>"+
        "<div id='tseries_rpm' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_rop' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_wob' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_flowinrate' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_bitpos' class=\"text-center\"></div>"
    );     
    $.getJSON(
        "/_drillrig_tseries", 
        {
            well_id:well_id,
            hour:hour
        },
        function (data) {             
            d3.select("#tseries_spinner").html(""); 
            heatmapDrilldown("tseries_rpm", "Time Series Plot: RPM", "RPM", "forestgreen");
            heatmapDrilldown("tseries_rop", "Time Series Plot: Rate of Penetration", "Rate of Penetration", "tomato");
            heatmapDrilldown("tseries_wob", "Time Series Plot: Weight on Bit", "Weight on Bit", "mediumvioletred");
            heatmapDrilldown("tseries_flowinrate", "Time Series Plot: Flow-in Rate", "Flow-in Rate", "slateblue");
            heatmapDrilldown("tseries_bitpos", "Time Series Plot: Bit Position", "Bit Position", "deeppink");
            /*tseries('tseries_rpm', data.tseries, "Time Series Plot : RPM", "RPM", "steelblue");
            tseries('tseries_rop', data.tseries, "Time Series Plot: Rate of Penetration", "Rate of Penetration", "tomato");
            tseries('tseries_wob', data.tseries, "Time Series Plot: Weight on Bit", "Weight on Bit", "mediumvioletred");
            tseries('tseries_flowinrate', data.tseries, "Time Series Plot: Flow-in Rate", "Flow-in Rate", "slateblue");
            tseries('tseries_bitpos', data.tseries, "Time Series Plot: Bit Position", "Bit Position", "deeppink");*/
        }
    );
}

function heatmapDrilldown(div_id, title, yaxis_label, line_color) {
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var parseDate = d3.time.format("%d-%b-%y").parse;

    var x = d3.time.scale().range([0, width]);

    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });

    /* Draw the series plot on the div element */
    var svg = d3.select("#"+div_id).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.tsv("../data/data.tsv", function(error, data) {
      if (error) throw error;

      data.forEach(function(d) {
        d.date = parseDate(d.date);
        d.close = +d.close;
      });

      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain(d3.extent(data, function(d) { return d.close; }));

      svg.append("g")
         .attr("class", "x axis")
         .attr("transform", "translate(0," + height + ")")
         .call(xAxis);

      svg.append("g")
         .attr("class", "y axis")
         .call(yAxis)
         .append("text")
         .attr("transform", "rotate(-90)")
         .attr("y", 6)
         .attr("dy", ".71em")
         .style("text-anchor", "end")
         .text(yaxis_label);

      svg.append("path")
         .datum(data)
         .attr("class", "line")
         .attr("d", line)
         .style("stroke",line_color);
         
      svg.append("text")
         .attr("x", (width / 2))
         .attr("y", 2 - (margin.top / 2))
         .attr("text-anchor", "middle")  
         .style("font-size", "16px")
         .text(title);
    });
}