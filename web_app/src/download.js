window._data = {
    pairs: {},
    nanobars: {},
    userId: undefined,
    gIdCounter: 0,
    progressData: {},
    done: [],
    generateID: undefined,
};

(() => {

    function generateID(baseStr) {
        var id =
            (baseStr + window._data.gIdCounter++);
        var progress = document.createElement('div');
        progress.id = id;
        // var parent = document.createElement('div');
        // parent
        console.log(document.querySelector(`#${baseStr}`));
        document.querySelector(`#${baseStr}`).appendChild(progress);
        return id;
    }
    window._data.generateID = generateID;

    var dl = document.querySelectorAll('.exportBtn');
    dl.forEach(f => f.onclick = (e) => {
        // TODO prevent spam
        console.log(e.target);
        if (window._data.userId != null) {
            var progressid = generateID(`progress-${e.target.dataset.username}`);
            var nanobar = new Nanobar({
                bg: '#44f',
                target: document.getElementById(progressid),
            });

            window._data.nanobars[progressid] = nanobar;

            fetch('/exports', {
                method: 'POST',
                headers: {

                    'Accept': 'application/json, text/plain, */*',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'userid': window._data.userId,
                    'elementid': progressid,
                    'username': e.target.dataset.username,
                }),
            }).then(d => d.json()).then(d => {
                console.log(d);
                window._data.pairs[d.taskid] = progressid;
                // window._data.update_progress(window._data.progressData);
            })
        } else {
            // no userid assigned by server yet
            console.error('No user id assigned by server yet')
            // either server is not reachable or
            // function called too fast
        }
    })
})()