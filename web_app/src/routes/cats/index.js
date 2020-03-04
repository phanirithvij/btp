const express = require('express')
const router = express.Router()

router.get('/', (req, res) => {
    res.json('Welcome to Boilerplate Cats')
})

module.exports = router