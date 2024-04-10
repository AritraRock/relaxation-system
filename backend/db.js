const { Client } = require("pg");

const client = new Client({
  connectionString:
    "postgresql://test_owner:1aLbZsOBJH9F@ep-falling-limit-a5lnriep.us-east-2.aws.neon.tech/test?sslmode=require",
});

async function createUsersTable() {
  await client.connect();
  try {
    const result = await client.query(`CREATE TABLE IF NOT EXISTS users(
        name varchar(50),
        email varchar(50),
        password varchar(50),
        age varchar(50),
        gender varchar(15),
        primary key(email));
    `);
    // console.log(result);
  } catch (err) {
    console.error("Error creating table:", err);
  }
}

module.exports = { client, createUsersTable };
