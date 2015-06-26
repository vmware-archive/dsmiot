/* 
  Drilldown functionality for heatmaps
  Show time-series plots for various well parameters
  Srivatsan Ramanujam <sramanujam@pivotal.io>, June-2015
  Modified sample plots from https://github.com/mbostock/d3/wiki/Gallery
*/

function tseries(well_id, hour, prob, div_id, data, feature, yaxis_label, line_color) {
    var margin = {top: 30, right: 20, bottom: 30, left: 60},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.time.scale().range([0, width]);

    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(d3.time.minutes, 5);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.ts_utc); })
        .y(function(d) { return y(d[feature]); });

    /* Draw the series plot on the div element */
    var svg = d3.select("#"+div_id).append("svg")
     .attr("width", width + margin.left + margin.right)
     .attr("height", height + margin.top + margin.bottom)
     .append("g")
     .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function(d) {
        d.ts_utc = d3.time.format.iso.parse(d.ts_utc).getTime();
        d[feature] = +d[feature];
    });

    x.domain(d3.extent(data, function(d) { return d.ts_utc; }));
    y.domain(d3.extent(data, function(d) { return d[feature]; }));

    svg.append("g")
     .attr("class", "x axis")
     .attr("transform", "translate(0," + height + ")")
     .call(xAxis);

    svg.append("g")
     .attr("class", "y axis")
     .call(yAxis)
     .append("text")
     .attr("transform", "rotate(-90)")
     .attr("y", -margin.left)
     .attr("dy", ".71em")
     .style("text-anchor", "end")
     .text(yaxis_label);

     svg.append("path")
     .datum(data)     
     .attr("class", "line")
     .attr("d", line)
     .style("stroke",line_color)
     .style("stroke-width","2.5px");

    //Title
    svg.append("text")
     .attr("x", (width / 2))
     .attr("y", -margin.top/2)
     .attr("text-anchor", "middle")  
     .style("font-size", "20px")
     .style("font-weight", "bold")
     .style("opacity","0.6")
     .text("well_id: "+well_id+", hour_of_day: "+hour+", p(failure in next hour): "+Number(prob*100.0).toFixed(2)+"%");
     
     /* Tooltip: based on http://bl.ocks.org/Caged/6476579 */
     var tip = d3.tip()
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
          return "<strong>"+feature+":</strong> <span style='color:red'>" + d[feature] + "</span>"+"<br>"+"<strong>ts_utc:</strong> <span style='color:green'>" + (new Date(d.ts_utc)).toUTCString() + "</span>";
      });           
     
     svg.call(tip);  
          
     svg.selectAll(".circle")
     .data(data)
     .enter()
     .append("svg:circle")
     .attr("class", "circle")
     .attr("cx", function (d) {
        return x(d.ts_utc);
     })
     .attr("cy", function (d) {
       return y(d[feature]);
     })
     .attr("r", 1)
     .attr("fill", "none")
     .attr("stroke", line_color)
     .on('mouseover', tip.show)
     .on('mouseout', tip.hide);     
     /* End of tooltip */
}

function invokeTimeSeries(well_id, hour, prob) {
    d3.select("#tseries").html("");
    d3.select("#tseries").html("<h1 class=\"text-center\">Well Features : Series Plots</h1>"+"<br>"+  
        "<span id='tseries_spinner'><img src='../img/spinner.gif' class=\"customer-spinner\"></span>"+
        "<div id='tseries_depth' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_rpm' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_rop' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_wob' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_flowinrate' class=\"text-center\"></div><br><br>"+
        "<div id='tseries_bitpos' class=\"text-center\"></div>"
    );     
    
    /* Scroll to the time-series plots */
    $('html,body').animate({
       scrollTop: $("#tseries").offset().top
    });
        
    $.getJSON(
        "/_drillrig_tseries", 
        {
            well_id:well_id,
            hour:hour
        },
        function (data) {             
            d3.select("#tseries_spinner").html(""); 
            
            /* Show the time series plots */
            /*heatmapDrilldown(well_id, hour, "tseries_rpm", "Time Series Plot for RPM", "RPM", "forestgreen");
            heatmapDrilldown(well_id, hour, "tseries_rop", "Time Series Plot for Rate of Penetration", "Rate of Penetration", "tomato");
            heatmapDrilldown(well_id, hour, "tseries_wob", "Time Series Plot for Weight on Bit", "Weight on Bit", "mediumvioletred");
            heatmapDrilldown(well_id, hour, "tseries_flowinrate", "Time Series Plot for Flow-in Rate", "Flow-in Rate", "slateblue");
            heatmapDrilldown(well_id, hour, "tseries_bitpos", "Time Series Plot for Bit Position", "Bit Position", "deeppink");*/
            tseries(well_id, hour, prob, 'tseries_depth', data.tseries, 'depth', "depth", "orange");
            tseries(well_id, hour, prob, 'tseries_rpm', data.tseries, 'rpm', "rpm", "forestgreen");
            tseries(well_id, hour, prob, 'tseries_rop', data.tseries, 'rop', "rate of penetration", "tomato");
            tseries(well_id, hour, prob, 'tseries_wob', data.tseries, 'wob', "weight on bit", "mediumvioletred");
            tseries(well_id, hour, prob, 'tseries_flowinrate', data.tseries, 'flow_in_rate', "flow-in Rate", "slateblue");
            tseries(well_id, hour, prob, 'tseries_bitpos', data.tseries, 'bit_position', "bit position", "turquoise");
        }
    );
}

function heatmapDrilldown(well_id, hour, div_id, title, yaxis_label, line_color) {
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

    d3.tsv("../data/tseries_sample.tsv", function(error, data) {
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
         .attr("y", 0)
         .attr("text-anchor", "middle")  
         .style("font-size", "20px")
         .style("opacity","0.6")
         .text(title+": Well ID - "+well_id+" Hour of Day - "+hour);
    });
}