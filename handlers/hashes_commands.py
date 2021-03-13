from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from tools import *
from bot import dp
from database import DatabaseTlgBot
from datetime import datetime


class OrderHashDecryption(StatesGroup):
    waiting_for_algorithm = State()
    waiting_for_hashes = State()
    waiting_for_supertask = State()
    start_task = State()
    waiting_for_essid = State()


db = DatabaseTlgBot()


# rh = recovery hashes
@dp.message_handler(commands="recovery", state="*")
async def algorithm_request(message: types.Message):
    chat_id = message.chat.id
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    username = message.chat.username
    language_code = message.from_user.language_code
    db.create_user(chat_id=chat_id, first_name=first_name, last_name=last_name, username=username,
                   language_code=language_code)
    template_message = ''
    for key, value in AVAILABLE_ALGORITHMS.items():
        template_message = template_message + f"*{key}*     {value.get('name')}\n"
    await message.answer(f"{template_message}\n\nВыберите алгоритм, указав его номер", parse_mode="Markdown")
    await OrderHashDecryption.waiting_for_algorithm.set()


@dp.message_handler(state=OrderHashDecryption.waiting_for_algorithm, content_types=types.ContentTypes.TEXT)
async def get_hashes(message: types.Message, state: FSMContext):
    try:
        chosen_algorithm = int(message.text)
    except ValueError as err:
        chosen_algorithm = None
    if chosen_algorithm not in AVAILABLE_ALGORITHMS.keys():
        await message.answer("Указан некорректный номер алгоритма, попробуйте снова")
        return
    await state.update_data(chosen_algorithm=chosen_algorithm)
    await OrderHashDecryption.waiting_for_hashes.set()
    await message.answer("Укажите в сообщении хэши, соответствующие выбранному алгоритму. "
                         "Каждый хэш должен быть с новой строки")


@dp.message_handler(state=OrderHashDecryption.waiting_for_hashes, content_types=types.ContentTypes.TEXT)
async def get_supertask(message: types.Message, state: FSMContext):
    # Блок обработки полученных от пользователя хэшей
    hashes = set(message.text.split("\n"))
    user_data = await state.get_data()
    algorithm_id = user_data.get('chosen_algorithm')
    verified_hashes = check_hashes_against_the_algorithm(hashes, algorithm_id)
    correct_hashes = verified_hashes.get('correct')
    incorrect_hashes = verified_hashes.get('incorrect')
    if not correct_hashes:
        await message.answer(f"Переданные хэши не соответствуют выбранному алгоритму:\n{incorrect_hashes}."
                             f"\nПроверьте их корректность или обратитесь к разработчику.")
        return
    # if incorrect_hashes:
    #     incorrect_hashes_str = ', '.join(incorrect_hashes)
    #     await message.answer(f"Следующие хэши не соответствуют выбранному алгоритму:\n{incorrect_hashes_str}."
    #                          f"\nПроверьте их корректность")
    # Вывод списка супертасков
    supertasks_info = db.get_supertasks_info()
    supertask_id = list()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for supertask in supertasks_info:
        keyboard.add(f"{str(supertask.id)}: Стоимость за хэш: {supertask.price}")
        supertask_id.append(supertask.id)
    await message.answer(f"Выберите шаблон для восстановления пароля", reply_markup=keyboard)
    await OrderHashDecryption.waiting_for_supertask.set()
    await state.update_data(list_supertask_id=supertask_id, hashes=verified_hashes.get('correct'))


@dp.message_handler(state=OrderHashDecryption.waiting_for_supertask, content_types=types.ContentTypes.TEXT)
async def create_task_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    supertask_id = user_data.get('list_supertask_id')
    try:
        chosen_supertask = int(message.text.split(":")[0].rstrip())
    except ValueError as err:
        chosen_supertask = None
    if chosen_supertask not in supertask_id:
        await message.answer("Пожалуйста, укажите шаблон, используя клавиатуру ниже")
        return
    hash_type_id = user_data.get('chosen_algorithm')
    hashes = user_data.get('hashes')
    if create_task(hash_list_name=f"tbot_{message.chat.id}_{datetime.now().strftime('%Y%m%d_%H%m%S')}",
                   hash_type_id=hash_type_id, hashes=hashes, super_task_id=chosen_supertask, chat_id=message.chat.id):
        await state.finish()
        await message.answer(f"Задание принято.")
        return
    else:
        await message.answer(f"Ошибка при назначении задания. Обратитесь в ТП.")
