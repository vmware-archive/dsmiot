/* 
  Show a bar plot of model coefficients
  Srivatsan Ramanujam <sramanujam@pivotal.io>, June-2015
  Based on the example: http://bl.ocks.org/mbostock/2368837
*/

function drawModelCoefficients(data) {
    var margin = {top: 30, right: 100, bottom: 10, left: 100},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.ordinal()
        .rangeRoundBands([0, height], .2);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top");

    /* Add heading for model coefficients bar plot */
    d3.select("#modelcoefs").html("\<h1 class=\"text-center\">Model Coefficients\</h1>"+"\<br>");         

    var svg = d3.select("#modelcoefs").append("svg")
     .attr("width", width + margin.left + margin.right)
     .attr("height", height + margin.top + margin.bottom)
     .append("g")
     .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    x.domain(d3.extent(data, function(d) { return d.coef; })).nice();
    y.domain(data.map(function(d) { return d.feature; }));

    var rectGroup = svg.selectAll(".bar")
     .data(data)
     .enter()
     .append("g");
    
    //Draw the bars
    rectGroup.append("rect")
     .attr("class", function(d) { return d.coef < 0 ? "bar negative" : "bar positive"; })
     .attr("x", function(d) { return x(Math.min(0, d.coef)); })
     .attr("y", function(d) { return y(d.feature); })
     .attr("width", function(d) { return Math.abs(x(d.coef) - x(0)); })
     .attr("height", y.rangeBand());
     
    //Add a labelt o the bars 
    rectGroup.append("text")
     .attr("class", "bar text")
     .attr("x", function(d) { return x(Math.min(0, d.coef)); })
     .attr("y", function(d) { return y(d.feature) + y.rangeBand()/2; })
     .attr("dy", ".35em")
     .text(function(d) { return d.feature; });

    svg.append("g")
     .attr("class", "x axis")
     .call(xAxis);

    svg.append("g")
     .attr("class", "y axis")
     .append("line")
     .attr("x1", x(0))
     .attr("x2", x(0))
     .attr("y2", height);

    function type(d) {
      d.coef = +d.coef;
      return d;
    }
}

function drawModelCoefficientsOld(data) {
    var margin = {top: 30, right: 10, bottom: 10, left: 10},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.ordinal()
        .rangeRoundBands([0, height], .2);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top");

    /* Clear existing elements */
    d3.select("#modelcoefs_spinner").html("");

    var svg = d3.select("#modelcoefs").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.tsv("../data/barplot_sample.tsv", type, function(error, data) {
      x.domain(d3.extent(data, function(d) { return d.value; })).nice();
      y.domain(data.map(function(d) { return d.name; }));

      svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", function(d) { return d.value < 0 ? "bar negative" : "bar positive"; })
        .attr("x", function(d) { return x(Math.min(0, d.value)); })
        .attr("y", function(d) { return y(d.name); })
        .attr("width", function(d) { return Math.abs(x(d.value) - x(0)); })
        .attr("height", y.rangeBand());

      svg.append("g")
        .attr("class", "x axis")
        .call(xAxis);

      svg.append("g")
        .attr("class", "y axis")
        .append("line")
        .attr("x1", x(0))
        .attr("x2", x(0))
        .attr("y2", height);
    });

    function type(d) {
      d.value = +d.value;
      return d;
    }
}