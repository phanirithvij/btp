var dl = document.querySelector('button');
dl.onclick = () => {
    if (window.userId != null) {
        fetch('/download', {
            method: 'POST',
            headers: {

                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'asa': 'aaa',
                'userid': window.userId,
            }),
        }).then(d => console.log(d))
    } else {
        // no userid assigned by server yet
        console.error('No user id assigned by server yet')
        // either server is not reachable or
        // function called too fast
    }
}