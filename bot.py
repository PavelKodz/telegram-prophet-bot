
import json
import os
import random
from datetime import datetime, timedelta

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# Загружаем токен
TOKEN = os.environ.get("TOKEN")

# Загружаем данные
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)["tarot"]

# Лимиты
user_limits = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="помощь")]
    ]
    welcome_text = (
        "*Шёпот сквозь века*

"
        "_Выбери главу или карту. Пророчество доступно раз в сутки._"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Команда /resetme
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_limits:
        del user_limits[user_id]
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*
"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.
"
        "— Пророчество доступно *раз в сутки* по каждой теме.
"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.
"
        "— Для сброса лимитов — /resetme.

"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Обработка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.lower()
    user_id = query.from_user.id
    now = datetime.now()

    if data == "помощь":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=(
                "*Как пользоваться Шёпотом сквозь века:*
"
                "— Нажми /start или кнопку снизу, чтобы выбрать главу.
"
                "— Пророчество доступно *раз в сутки* по каждой теме.
"
                "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.
"
                "— Для сброса лимитов — /resetme.

"
                "_Пусть слова откроют путь..._"
            ),
            parse_mode="Markdown"
        )
        return

    if data == "таро":
        if user_id in user_limits and "таро" in user_limits[user_id]:
            if now < user_limits[user_id]["таро"] + timedelta(days=1):
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Оракул молчит. Возвращайся завтра."
                )
                return
        card = random.choice(tarot_cards)
        user_limits.setdefault(user_id, {})["таро"] = now
        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=card["image"],
            caption=f"*{card['name']}*
{card['description']}",
            parse_mode="Markdown"
        )
        return

    if data not in pages:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Такой главы нет. Попробуй: Философия, Вдохновение, Тьма, Булгаков."
        )
        return

    if user_id in user_limits and data in user_limits[user_id]:
        if now < user_limits[user_id][data] + timedelta(days=1):
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text="Оракул молчит. Возвращайся завтра."
            )
            return

    user_limits.setdefault(user_id, {})[data] = now
    phrase = random.choice(pages[data])
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=f"_Оракул шепчет:_

{phrase}",
        parse_mode="Markdown"
    )

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Бот запущен.")
    app.run_polling()
