var express = require('express');
const axios = require('axios');
var mysql = require('mysql');
const schedule = require('node-schedule');

//const env = require('dotenv').config({ path: "./.env" });

const path = require('path');
const { log } = require('console');
const app = express();
// post 방식 사용 시 JSON 본문을 파싱할 수 있게 하는 처리
app.use(express.json());

const PORT1 = process.env.PORT1;
const PORT2 = process.env.PORT2;

const FASTAPI_URL1 = process.env.FASTAPI_URL1;
const FASTAPI_URL2 = process.env.FASTAPI_URL2;

const DB_HOST = process.env.DB_HOST;
const DB_USER = process.env.DB_USER;
const DB_PASSWORD = process.env.DB_PASSWORD;
const DB_NAME = process.env.DB_NAME;

// DB CONNECT
const connection = mysql.createConnection({
    host: DB_HOST,
    user: DB_USER,
    password: DB_PASSWORD,
    database: DB_NAME
  });

connection.connect(error => {
if (error) {
    console.error('Database connection failed: ' + error.stack);
    return;
}
console.log('Connected to database.');
});

// ejs 폴더 위치 지정
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'public'));

// public folder 연결을 통한 frontend 접근
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

// 검색을 눌렀을 시 이벤트 (키워드, 구어체 구분)
app.get('/search', async (req, res) => {
    const searchType = req.query.type;
    const searchWord = req.query.searchword;

    // 키워드 기반 검색
    if (searchType === 'keyword') {
        try {
            const response = await axios.get(`http://localhost:8500/searchKeyword?type=${searchType}&searchword=${searchWord}`);
            res.render('search.ejs', response.data);
        } catch (error) {
            console.error(error);
            if (!res.headersSent) {
                res.status(500).send('Error fetching data');
            }
        }
    }
    // 구어체 기반 검색
    else if (searchType === 'sentence') {
        try {
            const response = await axios.get(`http://localhost:8000/searchColl?type=${searchType}&searchword=${searchWord}`);
            res.render('search.ejs', response.data);
        } catch (error) {
            console.error(error);
            if (!res.headersSent) {
                res.status(500).send('Error fetching data');
            }
        }
    }
    // 오류 처리
    else {
        console.log('Invalid search type');
        res.render('index.html');
    }
});


app.get('/searchColl', async (req, res) => {
    try {
        const searchWord = req.query.searchword;
        const getColaResponse = await axios.get(`${FASTAPI_URL2}/getColl?searchword=${searchWord}`);
        const collData = getColaResponse.data;

        // 결과 렌더링
        res.json(collData);
        // res.json(searchKeywordData.data);
    } catch (error) {
        console.error('Error fetching data from FastAPI:', error);
        res.status(500).json({ resultCode: 500, message: "Failed to fetch data from FastAPI" });
    }
});


app.get('/savePopularKeyword', async (req, res) => {
    try {
        const response = await axios.get(`${FASTAPI_URL2}/searchPopularkeyord`);
        const data = response.data.data; 

        const keywords = data.map(item => item.keyword);
        
        // saveRDS를 호출하여 데이터 저장
        await axios.post('http://localhost:8000/saveRDS', { data });

        res.json({"resultCode" : 200, keywords });
    } catch (error) {
        console.error('Error fetching popular keywords:', error);
        res.status(500).send({ message: 'Error fetching popular keywords', error });
    }
});

// 인기 검색어 RDS에 저장하는 api
app.post('/saveRDS', async (req, res) => {
    try {

        const { data } = req.body;
        console.log('Request body:', req.body);
        const currentDate = new Date(); 

        for (const item of data) {
            const checkQuery = 'SELECT 1 FROM Collection WHERE searchword = ? LIMIT 1';
            connection.query(checkQuery, [item.keyword], (error, results) => {
                if (error) {
                    console.error('Error checking existence:', error);
                    return;
                }

                if (results.length === 0) {
                    const insertQuery = 'INSERT INTO Collection (searchword, date) VALUES (?, ?)';
                    connection.query(insertQuery, [item.keyword, currentDate], (error, results) => {
                        if (error) {
                            console.error('Error inserting data:', error);
                            return;
                        }
                        console.log(`Keyword ${item.keyword} inserted`);
                    });
                }
            });
        }

        console.log('Data processed');
        res.status(200).send({ resultCode: 200, message: 'Data processed successfully' });
    } catch (error) {
        console.error('Error saving data to RDS:', error);
        res.status(500).send({ resultCode: 500, message: 'Error saving data to RDS', error });
    }
});

// RDS에서 keyword를 검색하는 api
app.get('/selectRDS', async (req, res) => {
    try {
        // console.log('Request body:', req.body);
        const searchWord = req.query.searchword;

        const checkQuery = 'SELECT 1 FROM Collection WHERE searchword = ? LIMIT 1';
        connection.query(checkQuery, searchWord, (error, results) => {
            if (results.length > 0) {
                res.status(200).send({ resultCode: 200, keyword: searchWord });
            }
            else if (results.length === 0) {
                res.status(201).send({ resultCode: 404, keyword: searchWord });
            }
            else {
                console.error('Error checking existence:', error);
                res.status(500).send({ message: 'Error checking existence', error });
            }
        });
    } catch (error) {
        console.error('Error saving data to RDS:', error);
        res.status(500).send({ message: 'Error saving data to RDS', error });
    }
});

// 하루마다 갱신하기
schedule.scheduleJob('0 0 * * *', async () => {
    try {
        await axios.get('http://localhost:8000/savePopularKeyword');
        console.log('Scheduled task executed successfully');
    } catch (error) {
        console.error('Error executing scheduled task:', error);
    }
});

app.listen(PORT2, () => {
console.log(`Server is running on port ${PORT2}`);
});


