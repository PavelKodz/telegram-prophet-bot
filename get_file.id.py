import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN")  # или вставь токен напрямую в кавычках

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        largest = update.message.photo[-1]
        await update.message.reply_text(f"file_id: {largest.file_id}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, get_file_id))
    print("Бот готов. Отправь фото.")
    app.run_polling()