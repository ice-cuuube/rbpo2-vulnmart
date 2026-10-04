const express = require("express");
const initSqlJs = require("sql.js");
const { exec } = require("child_process");

const app = express();

app.use(express.urlencoded({ extended: true }));

async function startServer() {
    const SQL = await initSqlJs();
    const db = new SQL.Database();

    db.run(`
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT
        )
    `);

    db.run(
        "INSERT INTO users (id, username) VALUES (1, 'alice')"
    );


    // CWE-89: SQL Injection
    app.get("/user", (req, res) => {

        const username = req.query.username || "";

        // УЯЗВИМОСТЬ: пользовательский ввод
        // напрямую попадает в SQL-запрос
        const query =
            `SELECT * FROM users WHERE username = '${username}'`;

        try {
            const result = db.exec(query);

            if (result.length === 0) {
                return res.json({});
            }

            const columns = result[0].columns;
            const values = result[0].values;

            const row = {};

            columns.forEach((column, index) => {
                row[column] = values[0][index];
            });

            res.json(row);

        } catch (error) {
            res.status(500).json({
                error: error.message
            });
        }
    });


    // CWE-79: XSS
    app.get("/hello", (req, res) => {

        const name = req.query.name || "";

        // УЯЗВИМОСТЬ: прямой вывод
        // пользовательского значения в HTML
        res.send(`<h1>Hello, ${name}!</h1>`);
    });


    // CWE-78: OS Command Injection
    app.get("/ping", (req, res) => {

        const host = req.query.host || "127.0.0.1";

        // УЯЗВИМОСТЬ: пользовательский ввод
        // передаётся непосредственно в exec()
        exec(`ping -c 1 ${host}`, (error, stdout, stderr) => {

            if (error) {
                return res.status(500).send(stderr);
            }

            res.send(stdout);
        });
    });


    app.get("/", (req, res) => {

        res.send(`
            <h1>VulnMart-Lab JavaScript</h1>

            <p>/user?username=alice</p>
            <p>/hello?name=Student</p>
            <p>/ping?host=127.0.0.1</p>
        `);
    });


    app.listen(3000, () => {
        console.log(
            "JavaScript-сервис запущен на http://127.0.0.1:3000"
        );
    });
}

startServer().catch((error) => {
    console.error("Ошибка запуска:", error);
    process.exit(1);
});
