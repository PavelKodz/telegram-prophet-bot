from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '7665896303:AAE8m7TaEvSf2stZ2_G0cbRnbG_CfZX2yFg'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    await message.reply(f"file_id:\n{file_id}")

@dp.message_handler(content_types=['document'])
async def handle_document(message: types.Message):
    file_id = message.document.file_id
    await message.reply(f"file_id:\n{file_id}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)