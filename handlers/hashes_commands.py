from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from tools import *
from bot import dp
from database import Database


class OrderHashDecryption(StatesGroup):
    waiting_for_hashes = State()
    waiting_for_algorithm = State()
    waiting_for_supertask = State()
    start_task = State()
    waiting_for_essid = State()


db = Database()
db.connect()


# rh = recovery hashes
@dp.message_handler(commands="rh", state="*")
async def request_hashes(message: types.Message):
    if not db.check_user(message.chat.id):
        db.create_user(chat_id=message.chat.id, first_name=message.chat.first_name, last_name=message.chat.last_name,
                       username=message.chat.username, language_code=message.from_user.language_code)
    if not db.allowed_accept_tasks(message.chat.id):
        await message.answer("На текущий момент вы достигли лимита доступных заданий, дождитесь окончания предыдущих")
        return
    await message.reply("Отправьте хэши одного типа, каждый с новой строки")
    await OrderHashDecryption.waiting_for_hashes.set()
    db.close()


@dp.message_handler(state=OrderHashDecryption.waiting_for_hashes, content_types=types.ContentTypes.TEXT)
async def get_hashes(message: types.Message, state: FSMContext):
    algorithms = get_algorithms_from_hash_list(message.text.split('\n'))
    if not algorithms:
        await message.answer("Переданные хэши относятся к разным типам алгоритмов или не определён их алгоритм.\n"
                             "Отправьте хеши одного типа")
        return
    elif len(algorithms) == 1:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(algorithms[0])
        keyboard.add("Я не знаю")
        await message.answer(f"Алгоритм переданных хешей определён как {algorithms[0]}."
                             f"\nЕсли алгоритм определён верно, подтвердите это.", reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for algorithm in algorithms:
            print(algorithm)
            keyboard.add(algorithm)
        keyboard.add("Я не знаю")
        await message.answer(f"Переданные хеши могут быть следующих алгоритмов. Выберите корректный",
                             reply_markup=keyboard)
    await OrderHashDecryption.waiting_for_algorithm.set()
    await state.update_data(algorithms=algorithms)


@dp.message_handler(state=OrderHashDecryption.waiting_for_algorithm, content_types=types.ContentTypes.TEXT)
async def get_algorithm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'я не знаю':
        await message.answer("Обратитесь в техническую поддержу")
        return
    user_data = await state.get_data()
    algorithms = user_data.get('algorithms')
    if message.text not in algorithms:
        await message.answer("Пожалуйста, укажите алгоритм, используя клавиатуру ниже")
        return
    selected_algorithm = message.text
    await state.update_data(algorithms=selected_algorithm)
    await message.answer(f"Выбран алгоритм: {selected_algorithm}")
    supertasks_id = list()
    supertasks_info = db.get_supertasks()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for supertask in supertasks_info:
        keyboard.add(str(supertask.id))
        supertasks_id.append(str(supertask.id))
    await message.answer(f"Выберите шаблон для восстановления пароля", reply_markup=keyboard)
    await OrderHashDecryption.waiting_for_supertask.set()
    await state.update_data(supertasks=supertasks_id)


@dp.message_handler(state=OrderHashDecryption.waiting_for_supertask, content_types=types.ContentTypes.TEXT)
async def get_supertask(message: types.Message, state: FSMContext):
    supertask = message.text
    user_data = await state.get_data()
    supertasks = user_data.get('supertasks')
    if supertask not in supertasks:
        await message.answer("Пожалуйста, укажите шаблон, используя клавиатуру ниже")
        return

    # create_hashlist()

    hashlist = 123
    task_wrapper = 321
    db.add_task(chat_id=message.chat.id, hash_list_id=hashlist, supertask_id=int(supertask), task_wrapper_id=task_wrapper)
    await message.answer(f"Выбран шаблон: {supertask}\nЗадание принято.")




