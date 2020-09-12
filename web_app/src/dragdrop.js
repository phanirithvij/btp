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
    var dt = e.dataTransfer;

    handleFiles(dt.files);
  }

  let uploadProgress = [];
  let progressBars = [];
  let files = [];

  function initializeProgress(numFiles) {
    // clear any previous progress bars
    progressBars = [];
    for (let index = 0; index < numFiles; index++) {
      let pbar = document.querySelector(`#pb-file-${index}-${types[i]}`);
      progressBars.push(pbar);
    }
    window.pbars = progressBars;
    uploadProgress = [];

    for (let oindex = 0; oindex < numFiles; oindex++) {
      uploadProgress.push(0);
      progressBars[oindex].value = 0;
    }
  }

  let doneMap = [];

  function updateProgress(fileNumber, percent) {
    uploadProgress[fileNumber] = percent;
    let total =
      uploadProgress.reduce((tot, curr) => tot + curr, 0);
    console.debug("update", fileNumber, percent, total);
    // progressBar.value = total;
    progressBars[fileNumber].value = percent;
    if (percent == 100) {
      doneMap.push('done')
    }
    console.log(total, doneMap);

    if (doneMap.length == 2 * files.length) {
      window.location.reload();
    }
  }

  function handleFiles(xfiles) {
    console.log(files, xfiles);
    files = [...files, ...xfiles];
    document.querySelector(`.file-msg-${types[i]}`).innerHTML = `
    <div style="margin-bottom: 2.3rem;margin-top: 2rem;">
      <h4>Selected files</h4>
    </div>
    ${files.length > 0 ? `
    <div class="file row">
      <div class="col-4"></div>
      <div class="col-3"></div>
      <div class="col-4"></div>
      <div class="col-1">
        <span data-feather="x-square" class="remove-all-icon"></span>
      </div>
    </div>
    `: `
    No files selected
    `}

    ${files
        .map(
          (x, fileindex) =>
            `<div class="file row" data-filename="${x.name}">
            <div class="col-4">${x.name}</div>
            <div class="col-3 filesize--">${x.size}</div>
            <div class="col-4">
              <progress
                class="progressbar"
                id="pb-file-${fileindex}-${types[i]}"
                max="100"
                value="0">
              </progress>
            </div>
            <div
              class="col-1 remove-icon"
              data-file="${fileindex}"
            >
              <span
                data-feather="x-square"
              ></span>
            </div>
          </div>
          `
        )
        .join("\n")}
      
      ${files.length > 0 ? `<div class="upload-btn-wrapper">
          <button class="btn btn-primary upload-btn upload-btn-${
        types[i]
        }"> Upload </button> ${files.length} files
      </div>`: ''}
      `;

    feather.replace();

    $(".remove-all-icon").click(function () {
      files = [];
      handleFiles([]);
    });

    $(".remove-icon").click(function () {
      let fileindex = parseInt($(this).data().file);
      files.splice(fileindex, 1);
      handleFiles([]);
    });

    tippy('.remove-all-icon', {
      placement: 'left',
      content: 'Remove all the following files from the upload queue',
    });

    $(".upload-btn").click(function () {
      files.forEach(uploadFile);
    });
    $(".progressbar").css("visibility", "hidden");
    initializeProgress(files.length);

    document.querySelectorAll(".filesize--").forEach((f) => {
      f.innerHTML = readableFileSize(parseInt(f.innerHTML));
    });

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

  function uploadFile(file, fileindex) {
    var url = "/manage/upload";
    var xhr = new XMLHttpRequest();
    var formData = new FormData();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

    // Update progress (can be used to show progress indicator)
    xhr.upload.addEventListener("progress", function (e) {
      // progressBars.forEach(p => $(p).show());
      $(`#pb-file-${fileindex}-${types[i]}`).css("visibility", "visible");
      updateProgress(fileindex, (e.loaded * 100.0) / e.total || 100);
    });

    xhr.addEventListener("readystatechange", function (e) {
      if (xhr.readyState == 4 && xhr.status == 200) {
        updateProgress(fileindex, 100); // <- Add this
      } else if (xhr.readyState == 4 && xhr.status != 200) {
        // Error. Inform the user
      }
    });

    formData.append("file", file);
    formData.append("langcode", types[i]);
    xhr.send(formData);
  }
});

function readableFileSize(size) {
  var units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  var i = 0;
  while (size >= 1024) {
    size /= 1024;
    ++i;
  }
  return size.toFixed(1) + " " + units[i];
}
