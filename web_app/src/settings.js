$(".dataset-gallery").flickity({
  // options
  // cellAlign: "left",
  contain: true,
  groupCells: true,
});

(() => {
  $("#minus").hide();
  $("#dragdrop").hide();
  var dropareaHidden = true;
  $(".plus_drop").click((e) => {
    if (dropareaHidden) {
      $("#dragdrop").show();
      $("#plus").hide();
      $("#minus").show();
      dropareaHidden = !dropareaHidden;
    } else {
      $(".cancel-btn").click();
    }
  });
  $(".cancel-btn").click((e) => {
    $("#dragdrop").hide();
    $("#minus").hide();
    $("#plus").show();
    dropareaHidden = true;
  });
})();

$('.sel-box').hide();