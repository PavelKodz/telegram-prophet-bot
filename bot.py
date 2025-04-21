import json
import os
import asyncio
import random
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)["tarot"]

user_limits = {}

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Шёпот сквозь века*\n\nВыбери, в какой главе искать знамение.\n_Каждая глава и карта доступны раз в сутки._"
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
        "— Пророчество доступно *раз в сутки* по каждой теме.\n"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
        "— Для сброса лимитов — /resetme.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.", reply_markup=get_main_menu())

async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    now = datetime.now()

    if user_id not in user_limits:
        user_limits[user_id] = {}

    if topic in user_limits[user_id] and now - user_limits[user_id][topic] < timedelta(days=1):
        await query.message.reply_text("Оракул молчит. Возвращайся завтра.", reply_markup=get_main_menu())
        return

    message = random.choice(pages.get(topic, ["Знамение не найдено."]))
    user_limits[user_id][topic] = now
    await query.message.reply_text(f"*Оракул шепчет:*\n\n_{message}_", parse_mode="Markdown", reply_markup=get_main_menu())

async def send_tarot_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    now = datetime.now()

    if user_id not in user_limits:
        user_limits[user_id] = {}

    if "таро" in user_limits[user_id] and now - user_limits[user_id]["таро"] < timedelta(days=1):
        await query.message.reply_text("Оракул молчит. Возвращайся завтра.", reply_markup=get_main_menu())
        return

    card = random.choice(tarot_cards)
    caption = f"*{card['name']}*\n{card['description']}"
    user_limits[user_id]["таро"] = now
    await context.bot.send_photo(chat_id=query.message.chat.id, photo=card["image"], caption=caption, parse_mode="Markdown")
    await context.bot.send_message(chat_id=query.message.chat.id, text="Выбери следующую карту или пророчество:", reply_markup=get_main_menu())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    now = datetime.now()
    data = query.data

    if data == "help":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n"
            "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
            "— Пророчество доступно *раз в сутки* по каждой теме.\n"
            "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n\n"
            "_Пусть слова откроют путь..._"
        )
        await context.bot.send_message(chat_id=query.message.chat_id, text=help_text, parse_mode="Markdown")
        return

    elif data == "таро":
        if "таро" in user_limits.get(user_id, {}) and now - user_limits[user_id]["таро"] < timedelta(days=1):
            await context.bot.send_message(chat_id=query.message.chat_id, text="Оракул молчит. Возвращайся завтра.")
            return

        card = random.choice(tarot_cards)
        caption = f"*{card['name']}*\n{card['description']}"
        user_limits.setdefault(user_id, {})["таро"] = now
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=card["image"])
        await context.bot.send_message(chat_id=query.message.chat_id, text=caption, parse_mode="Markdown")
        return

    # Остальные кнопки — темы пророчеств
    await prophecy(update, context, topic=data)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Бот запущен.")
    app.run_polling()