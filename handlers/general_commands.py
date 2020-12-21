from aiogram import types
from bot import dp


@dp.message_handler(commands=['test'])
async def cmd_start(message: types.Message):
    await message.answer(f"Информация о пользователе{message.chat.values}")


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Для начала работы используйте команду /decrypt")


@dp.message_handler(commands=['help'])
async def cmd_start(message: types.Message):
    await message.answer("Для начала работы используйте команду /decrypt")