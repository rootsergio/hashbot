from aiogram import executor
from bot import dp
from handlers import *


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
