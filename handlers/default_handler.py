from aiogram import types
from bot import dp


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def all_other_messages(message: types.Message):
    await message.answer("Бот используется для восстановления пароля из хэш суммы.\n"
                         "Данный бот предназначен исключительно для восстановления собственных забытых и утерянных "
                         "паролей. Для начала работы можете использовать команды\n/start\n/help\n/decrypt")
