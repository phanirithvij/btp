// // no global pollution
// (() => {
//     const div = document.querySelector('div');
//     const socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

//     socket.on('my response', (msg) => {
//         const p = document.createElement("p");
//         p.innerHTML = 'Received: ' + msg.data;
//         div.appendChild(p);
//     });

//     var mediaConstraints = {
//         audio: true
//     };

//     var mediaRecorder;
//     var blobdata;
//     var streamHandle;

//     function onMediaSuccess(stream) {
//         streamHandle = stream;
//         mediaRecorder = new MediaStreamRecorder(stream);

//         mediaRecorder.mimeType = 'audio/wav'; // audio/webm or audio/ogg or audio/wav
//         mediaRecorder.ondataavailable = (blob) => {
//             // POST/PUT "Blob" using FormData/XHR2
//             var blobURL = URL.createObjectURL(blob);
//             console.log(blobURL);
//             div.innerHTML += '<a href="' + blobURL + '">' + blobURL + '</a>\n';
//             blobdata = blob;
//         };
//         const secs = 1000;
//         mediaRecorder.start(20 * secs);

//         // stop after 10 secs
//         setTimeout(mediaRecorder.stop, 10 * secs);

//     }


//     function onMediaError(e) {
//         console.error('media error', e);
//     }

//     // https://github.com/streamproc/MediaStreamRecorder#upload-to-php-server

//     function uploadBlobToServer(blob) {
//         var file = new File([blob], 'msr-' + (new Date).toISOString().replace(/:|\./g, '-') + '.wav', {
//             type: 'audio/wav'
//         });

//         // create FormData
//         var formData = new FormData();
//         formData.append('filename', file.name);
//         formData.append('file', file);
//         var server_url = 'http://' + document.domain + ':' + location.port;
//         makeXMLHttpRequest(`${server_url}/upload`, formData, (response) => {
//             console.log(response);
//             var downloadURL = `${server_url}/files/` + file.name;
//             console.log('File uploaded to this path:', downloadURL);
//             div.innerHTML += '<audio controls src="' + downloadURL + '">' + file.name + '</audio>\n';
//         });
//     }

//     function makeXMLHttpRequest(url, data, callback) {
//         var request = new XMLHttpRequest();
//         request.onreadystatechange = function () {
//             if (request.readyState == 4 && request.status == 200) {
//                 callback(request.response);
//             }
//         };
//         request.open('POST', url);
//         request.send(data);
//     }

//     // Should be done only on home page
//     const startbtn = document.querySelector('#start');
//     if (startbtn != undefined)
//         startbtn.onclick = () => {
//             navigator.getUserMedia(mediaConstraints, onMediaSuccess, onMediaError);
//         }

//     const stopbtn = document.querySelector('#stop');
//     if (stopbtn != undefined) stopbtn.onclick = () => {
//         mediaRecorder.stop();
//         streamHandle.stop();
//         streamHandle.getTracks().forEach((track) => {
//             track.stop();
//         });
//         clearTimeout(mediaRecorder.stop);
//     }

//     const saveBtn = document.querySelector('#save');
//     if (saveBtn) saveBtn.onclick = () => {
//         // mediaRecorder.save();
//         stopbtn.click();
//         uploadBlobToServer(blobdata);
//     }
// })();

(() => {

    var pairs = window._data.pairs;

    function readableFileSize(size) {
        var units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = 0;
        while (size >= 1024) {
            size /= 1024;
            ++i;
        }
        return size.toFixed(1) + ' ' + units[i];
    }

    function update_progress(data) {
        let percent = (data.current * 100 / data.total);
        var elementid = pairs[data.taskid];
        // TODO here error means a running task progress is recieved by this client
        // create new nanobar
        window._data.nanobars[elementid].go(percent);
        // console.log(data, 'updateprogess');
        if (data.status == "done") {
            const filename = data.filename;
            const el = document.getElementById(elementid);
            const par = el.parentElement;
            const a = document.createElement('a');
            a.href = `/export/${filename}`;
            a.text = "Download file";
            par.appendChild(a);
            fetch(`/info/${filename}`)
                .then(x => x.json())
                .then(f => {
                    var span = document.createElement('span');
                    span.innerText = readableFileSize(f.size);
                    console.log(f);
                    par.appendChild(span);
                });
        }
    }

    var namespace = '/events'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function () {
        socket.emit('status', {
            status: "I'm connected!"
        });
    });

    // event handler for userid.  On initial connection, the server
    // sends back a unique userid
    socket.on('userid', function (msg) {
        window._data.userId = msg.userid;
    });

    // event handler for server sent celery status
    // the data is displayed in the "Received" section of the page
    socket.on('celerystatus', update_progress);

    // event handler for server sent general status
    // the data is displayed in the "Received" section of the page
    socket.on('status', function (msg) {
        // $('#status').text(msg.status);
        console.log(msg, 'status')
    });

    socket.on('disconnect', function (da) {
        // $('#status').text('Lost server connection')
        console.log(da, 'dead server')
    });

})()