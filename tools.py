import re
from api_hashtopolis import HashtopolisUserApi
from database import Database

ID_SALTED_ALGORITHM = [20, 2811, 120]


AVAILABLE_ALGORITHMS = {
    0: {
        'name': 'MD5',
        'check': re.compile(r"^([a-fA-F\d]{32})$")
    },
    3200: {
        'name': 'bcrypt,blowfish(openbsd)',
        'check': re.compile(r"^(\$2[ayb]\$.{56})$")
    },
    1000: {
        'name': 'NTLM',
        'check': re.compile(r"^([a-fA-F\d]{32})$")
    },
    2500: {
        'id': 'WPA/WPA2',
        'check': re.compile(r"^(\$2[ayb]\$.{56})$")
    },
    10000: {
        'name': 'Django (PBKDF2-SHA256)',
        'check': re.compile(r"^(pbkdf2_sha256\$\d{5}\$.{56}=)$")
    },
    20: {
        'name': 'md5($salt.$pass)',
        'check': re.compile(r"^([a-fA-F\d]{32}):([a-zA-Z\d]{32})$")
        # 'check': re.compile(r"^([a-fA-F\d]{32}):([a-zA-Z\d]+)")   # попадает любое кол-во символов соли
    },
    500: {
        'name': 'md5crypt, MD5(Unix), FreeBSD MD5, Cisco-IOS MD5 2',
        'check': re.compile(r"^(\$1\$\S{8}\$\S{22})$")
    },
    2811: {
        'name': 'IPB2+, MyBB1.2+',
        'check': re.compile(r"^([a-zA-Z\d]{32}:[a-zA-Z\d]{8})$")
    },
    300: {
        'name': 'MySQL4.1/MySQL5+',
        'check': re.compile(r"^([a-zA-Z\d]{40})$")
    },
    100: {
        'name': 'SHA1',
        'check': re.compile(r"^([a-zA-Z\d]{40})$")
    },
    400: {
        'name': 'phpass, MD5(Wordpress), MD5(Joomla), MD5(phpBB3)',
        'check': re.compile(r"^(\$H\$9\S{30})$")
    },
    120: {
        'name': 'sha1($salt.$pass)',
        'check': re.compile(r"^([a-zA-Z\d]{40}:[a-zA-Z\d]{32})$")
    },
}


def get_algorithms_from_hash_list(hash_list):
    algorithms = list()
    for hash in hash_list:
        algorithm = [algorithm for algorithm, value in AVAILABLE_ALGORITHMS.items() if value.get('check').search(hash)]
        if algorithm and algorithm not in algorithms:
            algorithms.append(algorithm)
            if len(algorithms) > 1:
                return None
    if algorithms:
        return algorithms[0]
    return None


def check_hashes_against_the_algorithm(hashes_list, algorithm_id):
    """
    Функция проверяет хэш на соответствие заданому алгоритму
    :param hashes_list:
    :param algorithm_id:
    :return:
    """
    re_compile = AVAILABLE_ALGORITHMS.get(algorithm_id).get('check')
    correct_hashes = list()
    incorrect_hashes = list()
    verified_hashes = dict()
    for _hash in hashes_list:
        if re_compile.search(_hash):
            correct_hashes.append(_hash)
        else:
            incorrect_hashes.append(_hash)
    verified_hashes['correct'] = correct_hashes
    verified_hashes['incorrect'] = incorrect_hashes
    return verified_hashes


def get_run_supertask_id(hash_list_id: int) -> int:
    htapi = HashtopolisUserApi()
    tasks = htapi.listTasks()
    for task in tasks.get('tasks'):
        if task.get('hashlistId') == hash_list_id:
            return task.get('supertaskId')


def create_task(hash_list_name: str, hash_type_id: int, hashes: list, format: int, super_task_id: int) -> bool:
    """
    Создание задачи в Hashtopolis
    :param hash_list_name: имя создаваемого хэшлиста
    :param hash_type_id: id алгоритма
    :param hashes: список хэшей
    :param format: 0 - если хэши в текстовом виде, 1 - если в бинарном (например WPA)
    :return: True or False
    """
    if hash_type_id in ID_SALTED_ALGORITHM:
        is_salted = True
    else:
        is_salted = False
    db = Database()
    htapi = HashtopolisUserApi()
    response = htapi.create_hash_list(hash_list_name=hash_list_name, is_salted=is_salted, format=format,
                                          hash_type_id=hash_type_id, hashes=bytes('\n'.join(hashes).encode('UTF-8')))
    if not response or response.get('response') == 'ERROR':
        return False
    hash_list_id = response.get('hashlistId')
    if not htapi.run_super_task(hash_list_id=hash_list_id, super_task_id=super_task_id):
        return False
    task_wrapper_id = get_run_supertask_id(hash_list_id=hash_list_id)
    if not task_wrapper_id:
        return False
    max_priority = db.get_last_priority()
    if not max_priority:
        # Если в таблице задач нет задачи с установленным приоритетом, берём максимальный приоритет среди активных задач
        max_priority = 0
        response = htapi.listTasks()
        for task in response.get('tasks'):
            if task.get('priority') > max_priority:
                max_priority = task.get('priority')
    response = htapi.set_supertask_priority(task_wrapper_id=task_wrapper_id, super_task_priority=max_priority - 1)
    if not response or response.get('response') == 'ERROR':
        return False
    db.add_task(chat_id=hash_list_name.split("_")[1], hash_list_id=hash_list_id, supertask_id=super_task_id,
                task_wrapper_id=task_wrapper_id, priority=max_priority - 1)
    return True





if __name__ == "__main__":
    hashes = {'b1e60db8facbe14181005d5a35bf9716',
                 'c506d6ee045dd3da8e76fcaf7c1b3207',
                 'c506d6ee045dd3da8e76fc',
                 '97128e8c1017c3927cec7ce2da24e67f'}
    # print(check_hashes_against_the_algorithm(hashes, 0))
    print(get_run_supertask_id(786))