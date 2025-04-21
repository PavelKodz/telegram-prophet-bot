import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("TOKEN")

# Загружаем пророчества
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Загружаем карты Таро
with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)

# Храним временные лимиты
user_limits = {}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
    ]

    welcome = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Выбери, в какой главе искать знамение:\n"
        "_Одна пророческая глава или карта доступна раз в сутки._"
    )

    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Обработчик кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    topic = query.data.lower()
    now = datetime.now()

    # Проверка лимита
    if user_id in user_limits and topic in user_limits[user_id]:
        last_used = user_limits[user_id][topic]
        if now - last_used < timedelta(days=1):
            await query.edit_message_text(
                f"Сегодня ты уже получал знание из главы «{topic.title()}». Возвращайся завтра."
            )
            return

    # Обновляем лимит
    user_limits.setdefault(user_id, {})[topic] = now

    # Обработка Таро
    if topic == "таро":
        card = random.choice(tarot_cards)
        message = f"**{card['name']}**\n_{card['description']}_"
        await query.edit_message_text(message, parse_mode="Markdown")
    else:
        if topic in pages:
            phrase = random.choice(pages[topic])
            await query.edit_message_text(f"Оракул шепчет:\n\n_{phrase}_", parse_mode="Markdown")
        else:
            await query.edit_message_text("Такой главы нет. Попробуй снова.")

# Команда /resetme — сбрасывает лимиты для тестов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можно снова вызывать пророчества.")

# Команда /help — описание
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start, чтобы открыть главы.\n"
        "— Выбери одну из кнопок: _Философия_, _Вдохновение_, _Тьма_, _Булгаков_, _Карта Таро_.\n"
        "— Каждую из них можно нажимать *один раз в сутки*.\n"
        "— Для тестов используй команду /resetme.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()