/* ===================================================================
 * Count - Main JS
 *
 * ------------------------------------------------------------------- */

(function ($) {
  "use strict";

  var cfg = {
      scrollDuration: 800, // smoothscroll duration
      mailChimpURL: "https://desktop.ng/submit-email?route=email",
    },
    $WIN = $(window);

  // Add the User Agent to the <html>
  // will be used for IE10 detection (Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0))
  var doc = document.documentElement;
  doc.setAttribute("data-useragent", navigator.userAgent);

  // svg fallback
  if (!Modernizr.svg) {
    $(".home-logo img").attr("src", "images/logo.png");
  }

  /* Preloader
   * -------------------------------------------------- */
  var ssPreloader = function () {
    $("html").addClass("ss-preload");

    $WIN.on("load", function () {
      // will first fade out the loading animation
      $("#loader").fadeOut("slow", function () {
        // will fade out the whole DIV that covers the website.
        $("#preloader").delay(300).fadeOut("slow");
      });

      // for hero content animations
      $("html").removeClass("ss-preload");
      $("html").addClass("ss-loaded");
    });
  };

  /* info toggle
   * ------------------------------------------------------ */
  var ssInfoToggle = function () {
    //open/close lateral navigation
    $(".info-toggle").on("click", function (event) {
      event.preventDefault();
      $("body").toggleClass("info-is-visible");
    });
  };

  /* slick slider
   * ------------------------------------------------------ */
  var ssSlickSlider = function () {
    $(".home-slider").slick({
      arrows: false,
      dots: false,
      autoplay: true,
      autoplaySpeed: 3000,
      fade: true,
      speed: 3000,
    });
  };

  /* placeholder plugin settings
   * ------------------------------------------------------ */
  var ssPlaceholder = function () {
    $("input, textarea, select").placeholder();
  };

  /* final countdown
   * ------------------------------------------------------ */
  var ssFinalCountdown = function () {
    var finalDate = new Date("December 6, 2026 15:37:25").getTime();
    //-date: "Mar 25 2021",

    $(".home-content__clock")
      .countdown(finalDate)
      .on("update.countdown finish.countdown", function (event) {
        var str =
          '<div class="top"><div class="time days">' +
          "%D <span>day%!D</span>" +
          "</div></div>" +
          '<div class="time hours">' +
          "%H <span>H</span></div>" +
          '<div class="time minutes">' +
          "%M <span>M</span></div>" +
          '<div class="time seconds">' +
          "%S <span>S</span></div>";

        $(this).html(event.strftime(str));
      });
  };

  /* AjaxChimp
   * ------------------------------------------------------ */
  var ssAjaxChimp = function () {
    $("#mc-form").ajaxChimp({
      language: "es",
      url: cfg.mailChimpURL,
    });

    // Mailchimp translation
    //
    //  Defaults:
    //	 'submit': 'Submitting...',
    //  0: 'We have sent you a confirmation email',
    //  1: 'Please enter a value',
    //  2: 'An email address must contain a single @',
    //  3: 'The domain portion of the email address is invalid (the portion after the @: )',
    //  4: 'The username portion of the email address is invalid (the portion before the @: )',
    //  5: 'This email address looks fake or invalid. Please enter a real email address'

    $.ajaxChimp.translations.es = {
      submit: "Submitting...",
      0: '<i class="fas fa-check"></i> Thank you for indicating interest. We will be in touch.',
      1: '<i class="fas fa-exclamation-triangle"></i> You must enter a valid e-mail address.',
      2: '<i class="fas fa-exclamation-triangle"></i> E-mail address is not valid.',
      3: '<i class="fas fa-exclamation-triangle"></i> E-mail address is not valid.',
      4: '<i class="fas fa-exclamation-triangle"></i> E-mail address is not valid.',
      5: '<i class="fas fa-exclamation-triangle"></i> E-mail address is not valid.',
    };
  };

  $("#mc-form").submit(function (event) {
    event.preventDefault();
    document.getElementById("subscribe-message").innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    var email = $("#mc-email").val();
    $.ajax({
      type: "POST",
      url: "/submit-email",
      data: { email: email },
      success: function (response) {
        console.log("Email submitted successfully");
        document.getElementById("subscribe-message").innerHTML =
          '<i class="fas fa-check"></i> Thank you for indicating interest. We will be in touch.';
        document.getElementById("mc-email").value = "";
      },
      error: function (error) {
        console.error("Error submitting email:", error);
        document.getElementById("subscribe-message").innerHTML =
          error.responseJSON
            ? '<i class="fas fa-exclamation-triangle"></i>' +
              error.responseJSON.msg
            : '<i class="fas fa-exclamation-triangle"></i> An error occurred. Please try again.';
        document.getElementById("mc-email").value = "";
      },
    });
  });

  /* initialize
   * ------------------------------------------------------ */
  (function ssInit() {
    ssPreloader();
    ssInfoToggle();
    ssSlickSlider();
    ssPlaceholder();
    ssFinalCountdown();
    // ssAjaxChimp();
  })();
})(jQuery);
