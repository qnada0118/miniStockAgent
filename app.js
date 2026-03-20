const express = require("express");
const app = express();

app.get("/", (req, res) => {
    const given_value = requestAnimationFrame.query.value;
    const message = 'Given value is ${given_value}';
    res.send('Hello Elastic Beanstalk from 박규나 서버!<br><hr>' + message);
}).listen(8080);