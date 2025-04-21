import json
import os
import asyncio
import random
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Загрузка переменной окружения
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Загрузка карт Таро
with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)["tarot"]

# Храним лимиты
user_limits = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")],
    ]
    welcome = (
        "*Шёпот сквозь века:*\n\n"
        "Выбери главу, чтобы услышать пророчество или вытянуть карту.\n"
        "_Каждую кнопку можно нажимать раз в сутки._"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Пророчество
async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    user_id = update.callback_query.from_user.id
    now = datetime.now()

    if topic in user_limits.get(user_id, {}) and now - user_limits[user_id][topic] < timedelta(days=1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Оракул молчит. Возвращайся завтра.")
        return

    text = random.choice(pages.get(topic, ["Нет пророчеств по этой теме."]))
    user_limits.setdefault(user_id, {})[topic] = now

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Оракул шепчет:*\n\n{text}", parse_mode="Markdown")

# Карта Таро
async def send_tarot_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    now = datetime.now()

    if "таро" in user_limits.get(user_id, {}) and now - user_limits[user_id]["таро"] < timedelta(days=1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Оракул молчит. Возвращайся завтра.")
        return

    card = random.choice(tarot_cards)
    caption = f"*{card['name']}*\n{card['description']}"
    user_limits.setdefault(user_id, {})["таро"] = now

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=card["image"])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=caption, parse_mode="Markdown")

# Сброс лимитов
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.")

# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
        "— Пророчество доступно *раз в сутки* по каждой теме.\n"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
        "— Для сброса лимитов — /resetme.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Обработка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    now = datetime.now()
    data = query.data

    if data == "help":
        await help_command(update, context)
    elif data == "таро":
        await send_tarot_card(update, context)
    else:await prophecy(update, context, topic=data)

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Бот запущен.")
    app.run_polling()