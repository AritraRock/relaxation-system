const express = require("express");
const bodyParser = require("body-parser");
const { client, createUsersTable } = require("./db");
const PORT = 3000;
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());
// app.use(require('./routes/SignUp'));
// app.use(require('./routes/Login'));

createUsersTable();

app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    let result;
    try {
        result = await client.query(`SELECT password from users WHERE email='${email}';`);
    } catch (error) {
        console.log(error);
        res.status(500).send("Server Error.");
    } finally {
        // client.release();
    }
    if(result.rows.length===0){
        res.status(201).send({message:"No such user found."});
        return;
    }
    else if(result.rows[0]['password']!==password){
        res.status(202).send({message:"Wrong password."});
        return;
    }
    else{
        res.status(200).json({ message: "Succesfull login" });
    }
})

app.post("/student_signup", async (req, res) => {
    const { name, email, password, age,gender } = req.body;
    try {
        const result = await client.query(`INSERT INTO users VAlUES ('${name}','${email}','${password}','${age}','${gender}')`);
    } catch (error) {
        console.log(error);
        res.status(500).send("Server Error.");
    } finally {
        //client.release();
    }
    res.status(200).json({ message: "Succesfully signed up." });
})


app.listen(PORT);