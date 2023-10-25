$(document).ready(function () {
    $(window).on("resize", function() {
        if (isNavbarTogglerVisible() && $('#user-nav').hasClass('navbar-right')) {
          // Toggler button is visible
          console.log("Navbar toggler button is visible.");
          // Your code for the mobile view
          $('#user-nav').removeClass("navbar-right");
        } else if (!isNavbarTogglerVisible() && !$('#user-nav').hasClass('navbar-right')){
          // Toggler button is hidden
          console.log("Navbar toggler button is hidden.");
          // Your code for the larger screen view
          $('#user-nav').addClass("navbar-right");
        }
      });     
});

function isNavbarTogglerVisible() {
    let togglerButton = $(".navbar-toggler");
    return togglerButton.is(":visible");
  }