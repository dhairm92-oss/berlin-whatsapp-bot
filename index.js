const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const { GoogleGenAI } = require('@google/genai');
const pino = require('pino');
const express = require('express'); // أجبنا سيرفر وهمي لإرضاء Render

// إعداد سيرفر الويب الوهمي للبورت
const app = express();
const PORT = process.env.PORT || 10000;
app.get('/', (req, res) => res.send('Bot is running 24/7!'));
app.listen(PORT, () => console.log(`Web server running on port ${PORT}`));

// تهيئة Gemini باستخدام المتغير البيئي الآمن
const ai = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('whatsapp_session_v5');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        logger: pino({ level: 'silent' })
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('انقطع الاتصال، جاري إعادة المحاولة...', shouldReconnect);
            if (shouldReconnect) {
                startBot();
            }
        } else if (connection === 'open') {
            console.log('تم اتصال البوت بنجاح على الواتساب وجاهز للعمل!');
        }
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async (m) => {
        try {
            const msg = m.messages[0];
            if (!msg.message || msg.key.fromMe) return;

            const messageContent = msg.message.conversation || msg.message.extendedTextMessage?.text;
            const sender = msg.key.remoteJid;

            if (!messageContent) return;

            console.log(`رسالة واردة من ${sender}: ${messageContent}`);

            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: messageContent,
            });

            const replyText = response.text || "عذراً، لم أتمكن من معالجة الطلب.";
            await sock.sendMessage(sender, { text: replyText });

        } catch (error) {
            console.error('خطأ أثناء معالجة الرسالة:', error);
        }
    });
}

startBot();