const express = require('express')
const router = express.Router()

router.get('/', (req, res) => {
    res.json('Welcome to Boilerplate Lick lick')
})

module.exports = router