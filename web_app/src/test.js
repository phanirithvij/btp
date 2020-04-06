const div = document.querySelector('div');
const socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

socket.on('my response', (msg) => {
    const p = document.createElement("p");
    p.innerHTML = 'Received: ' + msg.data;
    div.appendChild(p);
});

var mediaConstraints = {
    audio: true
};

var mediaRecorder;
var blobdata;
navigator.getUserMedia(mediaConstraints, onMediaSuccess, onMediaError);

function onMediaSuccess(stream) {
    mediaRecorder = new MediaStreamRecorder(stream);
    mediaRecorder.mimeType = 'audio/wav'; // audio/webm or audio/ogg or audio/wav
    mediaRecorder.ondataavailable = (blob) => {
        // POST/PUT "Blob" using FormData/XHR2
        var blobURL = URL.createObjectURL(blob);
        console.log(blobURL);
        div.innerHTML += '<a href="' + blobURL + '">' + blobURL + '</a>\n';
        blobdata = blob;
    };
}


function onMediaError(e) {
    console.error('media error', e);
}

// https://github.com/streamproc/MediaStreamRecorder#upload-to-php-server

function uploadBlobToServer(blob) {
    var file = new File([blob], 'msr-' + (new Date).toISOString().replace(/:|\./g, '-') + '.wav', {
        type: 'audio/wav'
    });

    // create FormData
    var formData = new FormData();
    formData.append('filename', file.name);
    formData.append('file', file);
    var server_url = 'http://' + document.domain + ':' + location.port;
    makeXMLHttpRequest(`${server_url}/upload`, formData, (response) => {
        console.log(response);
        var downloadURL = `${server_url}/files/` + file.name;
        console.log('File uploaded to this path:', downloadURL);
    });
}

function makeXMLHttpRequest(url, data, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            callback(request.response);
        }
    };
    request.open('POST', url);
    request.send(data);
}

document.querySelector('#start').onclick = () => {
    const secs = 1000;
    mediaRecorder.start(20 * secs);

    // stop after 10 secs
    setTimeout(() => {
        mediaRecorder.stop();
    }, 10 * secs);
}

document.querySelector('#stop').onclick = () => {
    mediaRecorder.stop();
}

document.querySelector('#save').onclick = () => {
    // mediaRecorder.save();
    uploadBlobToServer(blobdata);
}