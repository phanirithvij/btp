$(".dataset-gallery").flickity({
  // options
  cellAlign: "left",
  contain: true,
  groupCells: true,
});

window.onload = (x) => {
  $(".minus").hide();
  $(".dragdrop").hide();
  var dropAreaMap = {};
  types.forEach((type) => {
    dropAreaMap[type] = true;
    $(`.plus_drop-${type}`).click((e) => {
      if (dropAreaMap[type]) {
        $(`.dragdrop-${type}`).show();
        $(`.plus-${type}`).hide();
        $(`.minus-${type}`).show();
        dropAreaMap[type] = false;
        $(`.gallery-${type}`).toggleClass("margin-bott");
      } else {
        $(`.cancel-btn-${type}`).click();
      }
    });
    $(`.cancel-btn-${type}`).click((e) => {
      $(`.dragdrop-${type}`).hide();
      $(`.minus-${type}`).hide();
      $(`.plus-${type}`).show();
      dropAreaMap[type] = true;
      $(`.gallery-${type}`).toggleClass("margin-bott");
    });
  });

  $(".sel-box").hide();
  $(".dataset-gallery").flickity("reposition");
  console.log("done");
};
// setInterval(() => {
//   $(".dataset-gallery").flickity("reposition");
// }, 1000);
