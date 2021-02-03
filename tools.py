import re
from database import Database

AVAILABLE_ALGORITHMS = {
    'MD5': {
        'id': 0,
        'check': re.compile(r"^([a-fA-F\d]{32})$")
    },
    'bcrypt,blowfish(openbsd)': {
        'id': 3200,
        'check': re.compile(r"^(\$2[ayb]\$.{56})$")
    },
    'NTLM': {
        'id': 1000,
        'check': re.compile(r"^([a-fA-F\d]{32})$")
    },
    # 'WPA/WPA2': {
    #     'id': 2500,
    #     'check': re.compile(r"^(\$2[ayb]\$.{56})$")
    # },
    'Django (PBKDF2-SHA256)': {
        'id': 10000,
        'check': re.compile(r"^(pbkdf2_sha256\$\d{5}\$.{56}=)$")
    },
    'md5($salt.$pass)'.lower(): {
        'id': 20,
        'check': re.compile(r"^([a-fA-F\d]{32}):([a-zA-Z\d]{32})$")
        # 'check': re.compile(r"^([a-fA-F\d]{32}):([a-zA-Z\d]+)")   # попадает любое кол-во символов соли
    },
    'md5crypt, MD5(Unix), FreeBSD MD5, Cisco-IOS MD5 2'.lower(): {
        'id': 500,
        'check': re.compile(r"^(\$1\$\S{8}\$\S{22})$")
    },
    'IPB2+, MyBB1.2+'.lower(): {
        'id': 2811,
        'check': re.compile(r"^([a-zA-Z\d]{32}:[a-zA-Z\d]{8})$")
    },
    'MySQL4.1/MySQL5+'.lower(): {
        'id': 300,
        'check': re.compile(r"^([a-zA-Z\d]{40})$")
    },
    'SHA1'.lower(): {
        'id': 100,
        'check': re.compile(r"^([a-zA-Z\d]{40})$")
    },
    'phpass, MD5(Wordpress), MD5(Joomla), MD5(phpBB3)'.lower(): {
        'id': 400,
        'check': re.compile(r"^(\$H\$9\S{30})$")
    },
    'sha1($salt.$pass)'.lower(): {
        'id': 120,
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
    hashes = [
        '400f0137ec3b5fb090539602eeaz08e75',
        'bf4d6324ec93599bca1ec105f292es9b1',
        # '$2a$10$wtkgo8IBo/PXdjjIfgFppOUocYgulIkkhvDnJIiV0TggbfWs37Cqi',
        # '0e992b23adefdd5ecb7c1d6b1ea6ca8a:ksBW2po3Kvzq6GMYyVVTyGbeFrBdLlFh',
        # '$1$iftktojc$9TKAn0cc6bWx21tqjW7tA1',
        # 'c506d6ee045dd3da8e76fcaf7c1b3207',
        # 'pbkdf2_sha256$15000$vHlJnOilaSOi$P9PDjkgILXqFJbEfAl02WZ5BV16oO7vZWWzIcoSQizI='
    ]
    print(get_algorithms_from_hash_list(hashes))
