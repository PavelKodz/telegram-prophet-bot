import json
import os
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

# Загрузка данных
with open("prophecies.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

with open("tarot_cards_full.json", "r", encoding="utf-8") as f:
    tarot_cards = json.load(f)["tarot"]

user_limits = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="Философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="Вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="Тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="Булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="Таро")],
        [InlineKeyboardButton("Помощь", callback_data="Помощь")]
    ]
    welcome_text = (
        "*Шёпот сквозь века:*\n\n"
        "Выбери главу или карту. Пророчество доступно *раз в сутки*."
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# /resetme
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_limits:
        del user_limits[user_id]
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.")

# Обработка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    now = datetime.now()

    if data == "Помощь":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n"
            "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
            "— Пророчество доступно *раз в сутки* по каждой теме.\n"
            "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n\n"
            "_Пусть слова откроют путь..._"
        )
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=help_text,
            parse_mode="Markdown"
        )
        return

    elif data == "Таро":
        if user_id in user_limits and "Таро" in user_limits[user_id]:
            if now < user_limits[user_id]["Таро"] + timedelta(days=1):
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Оракул молчит. Возвращайся завтра."
                )
                return

        card = random.choice(tarot_cards)
        caption = f"*{card['name']}*\n{card['description']}"

        if user_id not in user_limits:
            user_limits[user_id] = {}
        user_limits[user_id]["Таро"] = now

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=card["file_id"],
            caption=caption,
            parse_mode="Markdown"
        )
        return

    elif data in pages:
        if user_id in user_limits and data in user_limits[user_id]:
            if now < user_limits[user_id][data] + timedelta(days=1):
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Оракул молчит. Возвращайся завтра."
                )
                return

        phrase = random.choice(pages[data])
        if user_id not in user_limits:
            user_limits[user_id] = {}
        user_limits[user_id][data] = now

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"*Оракул шепчет:*\n\n{phrase}",
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Такой главы нет. Попробуй другую кнопку."
        )

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Бот запущен.")
    app.run_polling()