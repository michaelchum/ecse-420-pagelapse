$(function()
{
    // bind 
    $(window).resize(resize_site);

    // load the website
    setTimeout("load_site()", 0);

    // setup typer
    $('[data-typer-targets]').typer();

    // registration toggle
    /*
    $("#pre-register").click(function()
    {
      $(this).fadeOut(100, function()
      {
        $("#register").fadeIn();
      });
    });
    */ 
});

function load_site()
{
  resize_site();
}

// added in resize hacks
function resize_site()
{
  $("header").height( $(window).height() * 0.45 );
  $("#teaser").height( $("#teaser h1").height() * 1.1);
  $("#logo-wrapper").offset({top : ($("header").height() - $("#logo-wrapper").height()) / 2});
}
