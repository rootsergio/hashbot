import re

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


# def get_algorithms_from_hash_list(hash_list):
#     algorithms = dict()
#     for hash in hash_list:
#         algo = [algorithm for algorithm, value in AVAILABLE_ALGORITHMS.items() if value.get('check').search(hash)]
#         if len(algo) == 1:
#             algo = algo[0]
#         elif not algo:
#             algo = 'not algorithms'
#         else:
#             algo = '_|_|_'.join(algo)
#         hashes = algorithms.get(algo)
#         if hashes:
#             hashes.append(hash)
#             algorithms[algo] = hashes
#         else:
#             algorithms[algo] = [hash]
#     return algorithms


if __name__ == "__main__":
    hashes = {'b1e60db8facbe14181005d5a35bf9716',
                 'c506d6ee045dd3da8e76fcaf7c1b3207',
                 'c506d6ee045dd3da8e76fc',
                 '97128e8c1017c3927cec7ce2da24e67f'}
    print(check_hashes_against_the_algorithm(hashes, 0))
