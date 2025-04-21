import json
import random
import asyncio
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)

# Получение токена
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств из JSON-файла
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Словарь для хранения времени последнего обращения
user_last_usage = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "Я — *Шёпот сквозь века*.\n"
        "Выбери, в какой главе искать знамение:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data.lower()
    user_id = str(query.from_user.id)

    # Обработка кнопки help
    if topic == "help":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n"
            "— Нажми /start, чтобы открыть главы.\n"
            "— Нажми на одну из кнопок: _Философия_, _Вдохновение_, _Тьма_, _Булгаков_.\n"
            "— Ты получишь пророчество из выбранной главы.\n"
            "⚠️ *Ограничение:* каждую из глав можно выбрать только раз в сутки.\n"
            "Для сброса лимитов временно доступна команда /resetme.\n"
            "_Пусть слова откроют путь..._"
        )
        await query.message.reply_text(help_text, parse_mode="Markdown")
        return

    # Проверка лимита по времени
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    last_used = user_last_usage.get(user_id, {}).get(topic)

    if last_used and now - last_used < timedelta(days=1):
        await query.message.reply_text("Ты уже обращался к этой главе. Возвратись завтра...")
        return

    # Сохраняем время последнего использования
    user_last_usage.setdefault(user_id, {})[topic] = now

    # Отправка пророчества
    await query.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(1.5)
    await query.message.reply_text(random.choice(pages[topic]))

# Сброс лимитов /resetme
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in user_last_usage:
        user_last_usage[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можно снова обращаться к главам.")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()