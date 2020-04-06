const fs = require('fs');
const path = require('path');
const express = require('express');
const router = express.Router();
const lsdir = fs.readdirSync(__dirname);

lsdir.forEach(function(fileOrDirectory) {
    console.log(fileOrDirectory)
    var mount,
        route,
        lstat,
        abspath = path.join(__dirname, fileOrDirectory);

    if (abspath == __filename) {
        return;
    }

    lstat = fs.lstatSync(abspath);

    if (lstat.isDirectory(abspath)) {
        route = path.join(abspath, 'index.js');
        console.log(`route is ${route}`)
        mount = `/${fileOrDirectory}`;
    } else if (lstat.isFile(abspath) && path.extname(abspath) == '.js') {
        route = abspath;
        console.log(`route is ${route}`)
    }

    if (route) {
        try {
            route = require(route);
            console.log(`required ${mount}`)
            if (mount) {
                console.log(`[*] Mounting ${mount}`);
                router.use(mount, route);
            } else {
                router.use(route);
                console.log(`[*] Mounting 2 ${route}`)
            }
        } catch (e) {
            console.error(e);
        }
    } else {
        console.log("No route for", route)
    }
});

module.exports = router;