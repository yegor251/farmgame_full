var bodyParser = require('body-parser');
var express = require('express');
var TelegramBot = require('node-telegram-bot-api');

const TOKEN = '7106833924:AAHUplflybYnlTaizULr4HDmQtRbEy5k6pY';

var bot = new TelegramBot(TOKEN, { polling: true });
var app = express();

app.use(bodyParser.json());

// Обработка команды /start
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const options = {
        reply_markup: {
            inline_keyboard: [
                [{ text: 'Open Web App', web_app: { url: 'https://farmgame-rclc.onrender.com' } }]
            ]
        }
    };
    bot.sendMessage(chatId, 'Please choose an option:', options);
});

// Обработка данных, полученных из веб-приложения
bot.on('message', (msg) => {
    if (msg.web_app_data) {
        const data = msg.web_app_data.data;
        bot.sendMessage(msg.chat.id, `You selected option: ${data}`);
    }
});

// Обработка данных из веб-приложения
app.post('/webapp-data', (req, res) => {
    const chatId = req.body.chat_id;
    const tgData = req.body.tg_data;

    // Отправка данных пользователю в чат
    bot.sendMessage(chatId, `Telegram WebApp Data: ${JSON.stringify(tgData, null, 2)}`);
    
    res.sendStatus(200);
});

// Запуск сервера
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
