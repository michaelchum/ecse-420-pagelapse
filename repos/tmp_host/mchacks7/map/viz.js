d3.xml('drawing.svg', 'image/svg+xml', function(xml) {
  var node = document.importNode(xml.documentElement, true);
  d3.select('#viz').node().appendChild(node);
  //d3.select('#g14577').style('fill', function(d) {
    //return d.color = '#CC362B';
  //});
  removespinner();
  d3done();
});



$(document).ready(function() {
  loadEvents();
  var lastKey = '';
  var color;
  $(document.body).delegate("#eventslist>li","mouseenter",function(){
    console.log("HELLO MOFO");
    var floor = $(this).attr("data-floor");
    if(!floor)
    {
      floor = "";
    }
    var val = $(this).attr("data-building");
    for (var key in mappings) {
      if (val.indexOf(key) == 0) {
        color = d3.select("#g" + mappings[key] + floor).selectAll("*").style("fill");
        d3.select('#g' + mappings[key] + floor).selectAll('*').style('fill', '#CC362B');
        lastKey = key;
      }
    }
  });
  $(document.body).delegate("#eventslist>li","mouseleave",function(){
    var floor = $(this).attr("data-floor");
    if(!floor)
    {
      floor = "";
    }
      d3.select('#g' +  mappings[lastKey] + floor).selectAll("*").style("fill",color);
    });
});

$(window).resize(d3done);

function d3done()
{
  var optimalwidthscale = (window.innerWidth-200) / 200;
  var optimalheightscale = window.innerHeight / 150;
  var optscale = Math.min(optimalwidthscale,optimalheightscale) * 0.6;
  var optmargin = optscale*12;
  document.getElementById("viz").children[0].style.MozTransform = "scale(" + optscale + ") translateY(" + optmargin + "%)";
  document.getElementById("viz").children[0].style.webkitTransform = "scale(" + optscale + ") translateY(" + optmargin + "%)";
  document.getElementById("viz").children[0].style.transform = "scale(" + optscale + ") translateY(" + optmargin + "%)";
}

function removespinner()
{
  var spinner = document.getElementById("mapspin");
  spinner.outerHTML = "";
  delete spinner;
}

function loadEvents()
{
  $.getJSON("events.json",function(data){
    var htmlstring = "";
    $.each(data,function(itemnum,item){
      var date = new Date(item["time"]);
      var now = new Date();
      if(date < now)
      {
        htmlstring += "<li class='past' data-building='" + item["building"] + "' data-floor='" + item["floor"] + "'>";
      }else{
        htmlstring += "<li data-building='" + item["building"] + "' data-floor='" + item["floor"] + "'>";
      }
      htmlstring += "<p>"+item["name"]+"</p>";
      htmlstring += "<p>"+(new Date(item["time"]).toLocaleString()).replace(" ","<br>")+"</p>";
      htmlstring += "</li>";
    });
    $("#eventslist").html(htmlstring);
  });
}
