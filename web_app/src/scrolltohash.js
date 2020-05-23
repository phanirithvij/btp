// Scroll to hash
$(document).ready(function () {
    // Handler for .ready() called.
    if (location.hash != "")
        $('html, body').animate({
            scrollTop: $(location.hash).offset().top
        }, 'slow');
});