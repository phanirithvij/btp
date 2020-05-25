(() => {

    function update__zipprogress(data) {
        window._data.progressData = data;
        let percent = (data.current * 100 / data.total);
        var elementid = window._data.pairs[data.taskid];
        if (elementid == undefined) {
            // refreshed page create new progress bar
            console.log(data.username)
            window._data.running.push(data.username);
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
            // console.log(data);
            if (data.status == "done") {
                const filename = data.filename;
                const el = document.getElementById(elementid);
                const par = el.parentElement;
                const a = document.createElement('a');
                a.href = `/exports/export/${filename}`;
                a.text = '\ndownload ';
                // a.text = filename.split('_')[0];
                par.parentElement.appendChild(a);
                fetch(`/exports/info/${filename}`)
                    .then(x => x.json())
                    .then(f => {
                        var span = document.createElement('span');
                        span.innerText = readableFileSize(f.size);
                        console.log(f);
                        par.parentElement.appendChild(span);
                        window._data.done.push(data.taskid);
                        // hide bar
                        window._data.nanobars[elementid].go(0);
                        toastr["success"](`export done for user [${data.username}]`, "Done")
                    });
            }
        } // console.log(data, 'updateprogess');
    }

    window._data.update_progress = update__zipprogress;

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
    socket.on('userid', (msg) => {
        window._data.userId = msg.userid;
        if (location.pathname == '/exports') {

            const params = (new URLSearchParams(location.search));
            for (var x of params) {
                if (x[0] == 'username') {
                    let div = document.querySelector(`#progress-${x[1]}`);
                    console.log(
                        div.parentElement.querySelector('button')
                    );
                    setTimeout(() => {
                        div.parentElement.querySelector('button').click();
                    }, 100);
                }
            }

        }
    });

    // event handler for server sent celery status
    // the data is displayed in the "Received" section of the page
    socket.on('celerystatus', (x) => {
        if (x.type == 'export_task') {
            update__zipprogress(x);
        } else
        if (x.type == 'delete_zip_task') {
            if (x.status == 'done') {
                // console.log()
                toastr.options = {
                    "closeButton": true,
                    "debug": false,
                    "newestOnTop": true,
                    "progressBar": true,
                    "positionClass": "toast-top-right",
                    "preventDuplicates": true,
                    "onclick": null,
                    "showDuration": "300",
                    "hideDuration": "400",
                    "timeOut": "3000",
                    "extendedTimeOut": "1000",
                    "showEasing": "swing",
                    "hideEasing": "linear",
                    "showMethod": "fadeIn",
                    "hideMethod": "fadeOut"
                }
                toastr['success']("Deleted successfully");
                setTimeout(() => {
                    location.replace('/exports');
                }, 2000)
            }
        }
        console.log(x);
    });

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