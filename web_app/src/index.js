const express = require('express')
const socket = require('socket.io')
const cors = require('cors')
const bodyParser = require('body-parser')
const app = express()
const server = require('http').Server(app)
const io = socket(server)

const port = process.env.PORT || 3000
const route = require('./routes')

app.use(cors())
app.use((req, res, next) => {
    req.io = io
    next()
})
app.use(bodyParser.json())
app.use(route)

server.listen(port, () => {
    console.log('Listening on ' + port)
})