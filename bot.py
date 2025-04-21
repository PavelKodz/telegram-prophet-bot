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
    ContextTypes
)

TOKEN = os.environ.get("TOKEN")

# Загружаем пророчества
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Загружаем карты таро
with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)["tarot"]

# Храним лимиты
user_limits = {}

# Кнопочное меню
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="Философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="Вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="Тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="Булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Выбери, в какой главе искать знание.\n"
        "Одна пророчество или карта из каждой категории доступна раз в сутки."
    )
    await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode="Markdown")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
        "— Пророчество доступно *раз в сутки* по каждой теме.\n"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
        "— Для сброса лимитов — /resetme.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=get_main_menu())

# /resetme
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.", reply_markup=get_main_menu())

# Пророчество
async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE, topic=None):
    user_id = update.effective_user.id
    now = datetime.now()
    if topic not in pages:
        await update.callback_query.message.reply_text("Такой главы нет. Попробуй: Философия, Вдохновение, Тьма, Булгаков.", reply_markup=get_main_menu())
        return

    if user_id not in user_limits:
        user_limits[user_id] = {}

    if topic in user_limits[user_id] and now - user_limits[user_id][topic] < timedelta(days=1):
        await update.callback_query.message.reply_text("Оракул молчит. Возвращайся завтра.", reply_markup=get_main_menu())
        return

    phrase = random.choice(pages[topic])
    user_limits[user_id][topic] = now
    await update.callback_query.message.reply_text(f"*Оракул шепчет:*\n\n_{phrase}_", parse_mode="Markdown", reply_markup=get_main_menu())

# Карта Таро
async def send_tarot_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now()
    if user_id not in user_limits:
        user_limits[user_id] = {}

    if "таро" in user_limits[user_id] and now - user_limits[user_id]["таро"] < timedelta(days=1):
        await update.callback_query.message.reply_text("Оракул молчит. Возвращайся завтра.", reply_markup=get_main_menu())
        return

    card = random.choice(tarot_cards)
    caption = f"*{card['name']}*\n{card['description']}"
    user_limits[user_id]["таро"] = now

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=card["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

# Обработка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "help":
        await help_command(update, context)
    elif data == "таро":
        await send_tarot_card(update, context)
    else:
        await prophecy(update, context, topic=data)

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Бот запущен.")
    app.run_polling()