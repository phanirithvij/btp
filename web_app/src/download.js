window._data = {
    pairs: {},
    nanobars: {},
    userId: undefined,
    gIdCounter: 0,
};

(() => {
    var userId = window._data.userId;
    var nanobars = window._data.nanobars;
    var pairs = window._data.pairs;

    function generateID(baseStr) {
        var id =
            (baseStr + window._data.gIdCounter++);
        var progress = document.createElement('div');
        progress.id = id;
        document.querySelector('#progress').appendChild(progress);
        return id;
    }

    var dl = document.querySelector('button');
    dl.onclick = () => {
        if (window._data.userId != null) {
            var progressid = generateID('progress')
            var nanobar = new Nanobar({
                bg: '#44f',
                target: document.getElementById(progressid),
            });

            window._data.nanobars[progressid] = nanobar;

            fetch('/download', {
                method: 'POST',
                headers: {

                    'Accept': 'application/json, text/plain, */*',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'userid': window._data.userId,
                    'elementid': progressid,
                }),
            }).then(d => d.json()).then(d => pairs[d.taskid] = progressid)
        } else {
            // no userid assigned by server yet
            console.error('No user id assigned by server yet')
            // either server is not reachable or
            // function called too fast
        }
    }
})()