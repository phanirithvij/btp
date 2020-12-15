(function () {
  "use strict";

  feather.replace();
})();

$(".add-form").hide();
$("#cancel-btn").hide();
$("#save-cat-btn").hide();

$("#cancel-btn").click(function () {
  $(".add-form").hide();
  $("#add-btn").show();
  $("#cancel-btn").hide();
  $("#save-cat-btn").hide();
  $(".error").hide();
});

$("#add-btn").click(function () {
  $("#cancel-btn").show();
  $("#save-cat-btn").show();
  $(".add-form").show();
  $("#add-btn").hide();
});

$(".error").hide();

$("#save-cat-btn").click(function () {
  fetch("/manage/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      langs: document.querySelector("#langs").value,
      langname: document.querySelector("#langname").value,
      type: document.querySelector("#select-type").value,
    }),
  })
    .then((x) => {
      return x.json();
    })
    .then((x) => {
      console.log(x);
      if (x.success) {
        window.location.reload();
      } else {
        console.error(x);
        $(".error").show();
        $(".error").text("Error: " + x.error);
      }
    })
    .catch((x) => {
      console.error(x);
      $(".error").show();
      $(".error").text(x);
    });
});

tippy(".check-box", {
  placement: "left",
  content: "Currently selected public dataset for this category",
});

tippy("#add-btn", {
  placement: "right",
  content: "Add a new language Category",
});

let values = ["mixed", "single"];
let placeholders = {
  mixed: {
    langname: "eg. Mixed English Hindi",
    langs: "eg. eng, hin",
  },
  single: {
    langname: "eg. English",
    langs: "eg. eng",
  },
};

function selectchange(x) {
  document.querySelector("#langs").placeholder = placeholders[x.value]["langs"];
  document.querySelector("#langname").placeholder =
    placeholders[x.value]["langname"];
}
document.querySelector("#langs").placeholder =
  placeholders[document.querySelector("#select-type").value]["langs"];
document.querySelector("#langname").placeholder =
  placeholders[document.querySelector("#select-type").value]["langname"];
