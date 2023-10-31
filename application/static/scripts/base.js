$(document).ready(function () {
    adjustElements()
    $(window).on("resize", adjustElements);     
});

function isNavbarTogglerVisible() {
    let togglerButton = $(".navbar-toggler");
    return togglerButton.is(":visible");
  }

function adjustElements(){
    if (isNavbarTogglerVisible() && $('#user-nav').hasClass('navbar-right')) {
        $('#user-nav').removeClass("navbar-right");
      } else if (!isNavbarTogglerVisible() && !$('#user-nav').hasClass('navbar-right')){
        console.log("Navbar toggler button is hidden.");
        $('#user-nav').addClass("navbar-right");
      }
}