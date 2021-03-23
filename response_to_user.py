from database import DatabaseTlgBot, DatabaseHashtopolis
from aiogram import Bot
from config.config import settings
import asyncio

TOKEN = settings.BOT_TOKEN
bot = Bot(TOKEN)

db_hashtopolis = DatabaseHashtopolis()
db_tlg = DatabaseTlgBot()


def get_found_password():
    found_passwords = db_hashtopolis.get_cracked_hashes()
    chat_id_list = {rec.get('chat_id') for rec in found_passwords}
    # print(chat_id_list)
    passwords_for_transmission = {}
    for chat_id in chat_id_list:
        passwords_for_transmission[chat_id] = {rec.get('hash'): rec.get('plaintext') for rec in found_passwords
                                               if rec.get('chat_id') == chat_id}
    return passwords_for_transmission


async def sending_user_data():
    found_password = get_found_password()
    message = ''
    for chat_id, values in found_password.items():
        for hash, plaintext in values.items():
            message += f"{hash} {plaintext}\n"
        await bot.send_message(chat_id=chat_id, text=message)


if __name__ == '__main__':
    asyncio.run(sending_user_data())



