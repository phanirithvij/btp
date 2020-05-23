// Scroll to hash
$(document).ready(function () {
    // Handler for .ready() called.
    $('html, body').animate({
        scrollTop: $(location.hash).offset().top
    }, 'slow');
});