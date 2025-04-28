import logging
import json
import random
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated

# --- Configuration ---
API_TOKEN = os.getenv("BOT_TOKEN")
DATA_DIR = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- Data Loading ---
def load_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        if filename == 'users_data.json':
            return {}
        else:
            return []
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {filename}")
        if filename == 'users_data.json':
            return {}
        else:
            return []

tarot_data = load_data('tarot_cards_full_multilang_FINAL.json')
dark_data = load_data('dark_prophecies.json')
bulgakov_data = load_data('bulgakov_prophecies.json')
seneca_data = load_data('seneca_prophecies.json')
users_data = load_data('users_data.json')
if not isinstance(users_data, dict):
    users_data = {}

user_languages = {}

# Фотографии для категорий
category_images = {
    'dark': 'AgACAgIAAxkBAAIHMmgNUq24h7c5Ef1NI3a0Gtu6vUJ-AAJc-jEbcI9pSFAAAVHyINr1_AEAAwIAA3gAAzYE',  # file_id темной фотографии
    'bulgakov': 'AgACAgIAAxkBAAIHNGgNU0T3ZHm7BplgW1Ii6-IqawW_AAJe-jEbcI9pSAgRNGcHEtWBAQADAgADeQADNgQ',  # file_id Булгакова
    'seneca': 'AgACAgIAAxkBAAIHNmgNU5pQbgVTg9n34h1OR7yBToUuAAJf-jEbcI9pSKuWsRCUebWNAQADAgADeAADNgQ'   # file_id Сенек
}# --- UI Elements ---
button_names = {
    'menu': {'ru': "Меню", 'en': "Menu", 'de': "Menü", 'pl': "Menu"},
    'tarot': {'ru': "Карта Таро", 'en': "Tarot Card", 'de': "Tarotkarte", 'pl': "Karta Tarota"},
    'prophecy': {'ru': "Шёпот Судьбы", 'en': "Whisper of Fate", 'de': "Flüstern des Schicksals", 'pl': "Szept Przeznaczenia"},
    'help': {'ru': "Помощь", 'en': "Help", 'de': "Hilfe", 'pl': "Pomoc"},
    'choose_lang': {'ru': "Выбрать язык", 'en': "Choose Language", 'de': "Sprache wählen", 'pl': "Wybierz język"},
    'reset': {'ru': "ResetMe", 'en': "ResetMe", 'de': "ResetMe", 'pl': "ResetMe"}
}

language_codes = {
    "Русский": "ru",
    "English": "en",
    "Deutsch": "de",
    "Polski": "pl"
}

def get_main_menu(lang):
    kb = InlineKeyboardMarkup(resize_keyboard=True)
    kb.add(InlineKeyboardButton(button_names['menu'][lang], callback_data='open_menu'))
    return kb

def get_inline_options(lang):
    kb = InlineKeyboardMarkup(resize_keyboard=True)
    kb.add(InlineKeyboardButton(button_names['tarot'][lang], callback_data='tarot'))
    kb.add(InlineKeyboardButton(button_names['prophecy'][lang], callback_data='prophecy'))
    kb.add(InlineKeyboardButton(button_names['help'][lang], callback_data='help'))
    kb.add(InlineKeyboardButton(button_names['choose_lang'][lang], callback_data='choose_lang'))
    kb.add(InlineKeyboardButton(button_names['reset'][lang], callback_data='reset'))
    return kb

# --- Data Persistence ---
def save_users_data():
    with open(os.path.join(DATA_DIR, 'users_data.json'), 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def can_press_button(user_id, button_name):
    today = datetime.now().date().isoformat()
    last_pressed = users_data.get(str(user_id), {}).get(button_name)
    return last_pressed != today

def mark_button_pressed(user_id, button_name):
    today = datetime.now().date().isoformat()
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {}
    users_data[str(user_id)][button_name] = today
    save_users_data()# --- Handlers ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_languages[user_id] = message.from_user.language_code if message.from_user.language_code in ('en', 'de', 'pl') else 'ru'

    greetings = {
        "ru": "Добро пожаловать в «Шёпот сквозь века»! Выберите своё действие.",
        "en": "Welcome to 'Whisper of the Ages'! Choose your action.",
        "de": "Willkommen beim 'Flüstern der Zeitalter'! Wählen Sie Ihre Aktion.",
        "pl": "Witamy w 'Szept Wieczności'! Wybierz swoją akcję."
    }

    try:
        await message.answer(greetings.get(user_languages[user_id], greetings["ru"]), reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите действие:", reply_markup=get_main_menu(user_languages[user_id]))
    except (BotBlocked, ChatNotFound, UserDeactivated) as e:
        logging.error(f"Error sending message to user {user_id}: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
@dp.callback_query_handler(lambda c: True)
async def menu_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_language = user_languages.get(user_id, 'ru')
    data = callback_query.data

    
    if data == "open_menu":
            await bot.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=get_inline_options(user_language)
            )

    elif data == "tarot":
            if can_press_button(user_id, "tarot"):
                card = random.choice(tarot_data["tarot"])
                title = card["name"].get(user_language, card["name"]["ru"])
                description = card["description"].get(user_language, card["description"]["ru"])
                file_id = card["file_id"]
                await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=file_id,
                    caption=f"<b>{title}</b>\n\n{description}",
                    parse_mode="HTML"
                )
                mark_button_pressed(user_id, "tarot")
            else:
                await bot.send_message(callback_query.from_user.id, "Вы уже получали карту сегодня.")
            await bot.send_message(callback_query.from_user.id, "Выберите действие:", reply_markup=get_main_menu(user_language))
    elif data == "prophecy":
            if can_press_button(user_id, "prophecy"):
                categories = ['dark', 'bulgakov', 'seneca']
                category = random.choice(categories)

                prefixes = {
                    'dark': {
                        'ru': "С тобой говорят из тьмы...",
                        'en': "The darkness speaks to you...",
                        'de': "Die Dunkelheit spricht zu dir...",
                        'pl': "Ciemność przemawia do Ciebie..."
                    },
                    'bulgakov': {
                        'ru': "Шёпот Булгакова звучит в тебе...",
                        'en': "The whisper of Bulgakov resonates within you...",
                        'de': "Das Flüstern von Bulgakow erklingt in dir...",
                        'pl': "Szept Bułhakowa rozbrzmiewa w Tobie..."
                    },
                    'seneca': {
                        'ru': "Тебя предупреждает философ Сенека...",
                        'en': "The philosopher Seneca warns you...",
                        'de': "Der Philosoph Seneca warnt dich...",
                        'pl': "Filozof Seneka ostrzega cię..."
                    }
                }

                images = {
                    'dark': 'AgACAgIAAxkBAAIHMmgNUq24h7c5Ef1NI3a0Gtu6vUJ-AAJc-jEbcI9pSFAAAVHyINr1_AEAAwIAA3gAAzYE',  # file_id темной фотографии
                    'bulgakov': 'AgACAgIAAxkBAAIHNGgNU0T3ZHm7BplgW1Ii6-IqawW_AAJe-jEbcI9pSAgRNGcHEtWBAQADAgADeQADNgQ',  # file_id Булгакова
                    'seneca': 'AgACAgIAAxkBAAIHNmgNU5pQbgVTg9n34h1OR7yBToUuAAJf-jEbcI9pSKuWsRCUebWNAQADAgADeAADNgQ'   # file_id Сенека
                }

                prefix_text = prefixes[category].get(user_language, prefixes[category]['ru'])

                if category == 'standard':
                    prophecy = random.choice(standard_data)
                    await bot.send_message(
                        callback_query.from_user.id,
                        f"{prefix_text}\n\n{prophecy.get(user_language, prophecy['ru'])}"
                    )
                else:
                    if category == 'dark':
                        prophecy = random.choice(dark_data)
                    elif category == 'bulgakov':
                        prophecy = random.choice(bulgakov_data)
                    elif category == 'seneca':
                        prophecy = random.choice(seneca_data)

                    await bot.send_photo(
                        chat_id=callback_query.message.chat.id,
                        photo=images[category],
                        caption=f"{prefix_text}\n\n{prophecy.get(user_language, prophecy['ru'])}",
                        parse_mode="HTML"
                    )

                mark_button_pressed(user_id, "prophecy")
            else:
                await bot.send_message(callback_query.from_user.id, "Вы уже получали шёпот судьбы сегодня.")
            await bot.send_message(callback_query.from_user.id, "Выберите действие:", reply_markup=get_main_menu(user_language))
    elif data == "help":
            help_texts = {
                "ru": "Этот бот предсказывает с помощью карт Таро и мистических цитат. Каждую кнопку можно использовать один раз в день.",
                "en": "This bot predicts using Tarot cards and mystical quotes. Each button can be used once per day.",
                "de": "Dieser Bot prophezeit mit Tarotkarten und mystischen Zitaten. Jede Taste kann einmal täglich verwendet werden.",
                "pl": "Ten bot przepowiada za pomocą kart Tarota i mistycznych cytatów. Każdą funkcję można użyć raz dziennie."
            }
            await bot.send_message(
                callback_query.from_user.id,
                help_texts.get(user_language, help_texts["ru"])
            )
            await bot.send_message(
                callback_query.from_user.id,
                "Выберите действие:",
                reply_markup=get_main_menu(user_language)
            )

    elif data == "choose_lang":
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton("Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("English", callback_data="set_lang_en")
            )
            kb.add(
                InlineKeyboardButton("Deutsch", callback_data="set_lang_de"),
                InlineKeyboardButton("Polski", callback_data="set_lang_pl")
            )
            await bot.send_message(
                callback_query.from_user.id,
                "Выберите язык:",
                reply_markup=kb
            )

    elif data.startswith("set_lang_"):
            lang = data.split("_")[-1]
            user_languages[user_id] = lang
            await bot.send_message(
                callback_query.from_user.id,
                f"Язык успешно установлен: {lang.upper()}.",
                reply_markup=get_main_menu(lang)
            )

    elif data == "reset":
            if str(user_id) in users_data:
                users_data[str(user_id)] = {}
                save_users_data()
            reset_texts = {
    "ru": "Ограничения сброшены! Теперь вы можете снова использовать кнопки.",
    "en": "Restrictions have been reset! Now you can use the buttons again.",
    "de": "Einschränkungen wurden zurückgesetzt! Jetzt können Sie die Tasten erneut verwenden.",
    "pl": "Ograniczenia zostały zresetowane! Teraz możesz ponownie używać przycisków."
}

            await bot.send_message(
    callback_query.from_user.id,
    reset_texts.get(user_languages.get(user_id, 'ru'), reset_texts["ru"]),
    reply_markup=get_main_menu(user_languages.get(user_id, 'ru'))
)
if __name__ == '__main__':
                executor.start_polling(dp, skip_updates=True)