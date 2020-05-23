(() => {

    function update_progress(data) {
        window._data.progressData = data;
        let percent = (data.current * 100 / data.total);
        var elementid = window._data.pairs[data.taskid];
        if (elementid == undefined) {
            // refreshed page create new progress bar
            console.log(data.username)
            window._data.pairs[data.taskid] = window._data.generateID(`progress-${data.username}`);
            var elementid = window._data.pairs[data.taskid];
            var nanobar = new Nanobar({
                bg: '#44f',
                target: document.getElementById(elementid),
            });

            window._data.nanobars[elementid] = nanobar;
        }
        // console.log(window._data.nanobars, window._data.pairs, data.taskid)
        // TODO here error means a running task progress is recieved by this client
        // create new nanobar
        if (elementid != undefined && !(elementid in window._data.done)) {
            window._data.nanobars[elementid].go(percent);
            if (data.status == "done") {
                const filename = data.filename;
                const el = document.getElementById(elementid);
                const par = el.parentElement;
                const a = document.createElement('a');
                a.href = `/export/${filename}`;
                a.text = '\ndownload';
                // a.text = filename.split('_')[0];
                par.parentElement.appendChild(a);
                fetch(`/info/${filename}`)
                .then(x => x.json())
                .then(f => {
                    var span = document.createElement('span');
                    span.innerText = readableFileSize(f.size);
                    console.log(f);
                    par.parentElement.appendChild(span);
                    window._data.done.push(data.taskid);
                    par.remove();
                });
            }
        } // console.log(data, 'updateprogess');
    }

    window._data.update_progress = update_progress;

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