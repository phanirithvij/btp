// ************************ Drag and drop ***************** //
let dropAreas = document.querySelectorAll(".drop-area");

let handleFileMap = {};

dropAreas.forEach((dropArea, i) => {
  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, highlight, false);
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  // Handle dropped files
  dropArea.addEventListener("drop", handleDrop, false);

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight(e) {
    dropArea.classList.add("highlight");
  }

  function unhighlight(e) {
    dropArea.classList.remove("active");
  }

  function handleDrop(e) {
    console.log(e.target);
    var dt = e.dataTransfer;

    handleFiles(dt.files);
  }

  let uploadProgress = [];
  let progressBar = document.getElementById("progress-bar");
  let files = [];

  function initializeProgress(numFiles) {
    progressBar.value = 0;
    uploadProgress = [];

    for (let i = numFiles; i > 0; i--) {
      uploadProgress.push(0);
    }
  }

  function updateProgress(fileNumber, percent) {
    uploadProgress[fileNumber] = percent;
    let total =
      uploadProgress.reduce((tot, curr) => tot + curr, 0) /
      uploadProgress.length;
    console.debug("update", fileNumber, percent, total);
    progressBar.value = total;
  }

  function handleFiles(xfiles) {
    console.log(files, xfiles);
    files = [...files, ...xfiles];
    initializeProgress(files.length);
    document.querySelector(`.file-msg-${types[i]}`).innerHTML = `
    <div style="margin-bottom: 2.3rem;margin-top: 2rem;">
      <h4>Selected files</h4>
    </div>
    ${files
      .map(
        (x, i) =>
          `<div class="file row" data-filename="${x.name}">
            <div class="col-4">${x.name}</div>
            <div class="col-3">${x.size}</div>
            <progress
              class="col-4 progressbar"
              id="pb-file-${i}"
              max="100"
              value="0">
            </progress>
            <span
              class="col-1 remove-icon"
              data-feather="x-square"
            ></span>
          </div>`
      )
      .join("\n")}`;
    feather.replace();
    $(".progressbar").css("visibility", "hidden");
    // files.forEach(uploadFile)
    // files.forEach(previewFile)
  }

  function previewFile(file) {
    console.log(file);
    //   let reader = new FileReader()
    //   reader.readAsDataURL(file)
    //   reader.onloadend = function() {
    //     let img = document.createElement('img')
    //     img.src = reader.result
    //     document.getElementById('gallery').appendChild(img)
    //   }
  }
  handleFileMap[types[i]] = handleFiles;
});

function uploadFile(file, i) {
  var url = "/settings";
  var xhr = new XMLHttpRequest();
  var formData = new FormData();
  xhr.open("POST", url, true);
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

  // Update progress (can be used to show progress indicator)
  xhr.upload.addEventListener("progress", function (e) {
    updateProgress(i, (e.loaded * 100.0) / e.total || 100);
  });

  xhr.addEventListener("readystatechange", function (e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      updateProgress(i, 100); // <- Add this
    } else if (xhr.readyState == 4 && xhr.status != 200) {
      // Error. Inform the user
    }
  });

  formData.append("file", file);
  xhr.send(formData);
}
