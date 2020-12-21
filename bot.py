import logging
from aiogram import Bot, Dispatcher
from config.config import settings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)
