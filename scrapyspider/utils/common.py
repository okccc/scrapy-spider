import hashlib
import random


def get_md5():
    m = hashlib.md5()
    m.update(str(random.random()).encode('utf-8'))
    return m.hexdigest()


if __name__ == '__main__':
    print(get_md5())  # 1c8f78b505c3059098f1202e88834290
