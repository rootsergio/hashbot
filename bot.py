import logging
from aiogram import Bot, Dispatcher
from config.config import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


async def send_message(message, chat_id=None):
    await bot.send_message(chat_id=chat_id, text=message)