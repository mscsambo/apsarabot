import os
import asyncio
import edge_tts
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ទាញយក Token ពី .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
VOICE = "km-KH-SreymomNeural"

# ការកំណត់
MAX_TOTAL_CHARS = 4000
CHUNK_SIZE = 800

def split_khmer_text(text, max_size):
    sentences = re.split(r'(?<=។)\s*', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_size:
            current_chunk += sentence
        else:
            if current_chunk: chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk: chunks.append(current_chunk)
    return chunks

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សួស្តី! ខ្ញុំគឺ Apsara 🤖។ សូមផ្ញើអត្ថបទខ្មែរមក ខ្ញុំនឹងអានឱ្យអ្នកស្ដាប់។")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    if len(text) > MAX_TOTAL_CHARS:
        await update.message.reply_text(f"⚠️ អត្ថបទវែងពេក! សូមផ្ញើត្រឹម {MAX_TOTAL_CHARS} តួអក្សរ។")
        return

    wait_msg = await update.message.reply_text("កំពុងបំប្លែងទៅជាសំឡេង... ⏳")
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

    try:
        chunks = split_khmer_text(text, CHUNK_SIZE)
        for i, chunk in enumerate(chunks):
            filename = f"apsara_{chat_id}_{i}.mp3"
            communicate = edge_tts.Communicate(chunk, VOICE, rate="-15%", pitch="+2Hz")
            await communicate.save(filename)

            with open(filename, 'rb') as audio:
                caption = f"ផ្នែកទី {i+1}" if len(chunks) > 1 else ""
                await update.message.reply_voice(voice=audio, caption=caption)
            os.remove(filename)
        
        await wait_msg.delete()
    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហា៖ {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Apsara Bot is running...")
    app.run_polling()