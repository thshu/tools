import datetime
import hashlib
import os
import re

import requests
from filelock import FileLock
from retrying import retry


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
def request_data(method, url, status_code=None, **kwargs):
    """
    发送请求
    :param method: 请求方式
    :param url: 请求URL
    :param status_code: 成功的状态码
    :param kwargs:
    :return:
    """
    res = requests.request(method, url, **kwargs)
    res.encoding = res.apparent_encoding
    if status_code:
        if res.status_code == status_code:
            return res
        else:
            return
    return res


def get_file_size(file_size):
    file_size = file_size / 1024
    if file_size < 1024:
        return f'{file_size:.2f}KB'
    elif file_size < 1048576:
        return f'{(file_size / 1024):.2f}MB'
    else:
        return f'{(file_size / 1048576):.2f}GB'


def processing_time(seconds):
    if seconds < 60:
        return f'{seconds:.2f}秒'
    elif seconds < 3600:
        return f'{seconds // 60}分{seconds % 60}秒'
    elif seconds < 86400:
        return f'{seconds // 3600}小时{seconds % 3600 // 60}分{seconds % 3600 % 60}秒'
    else:
        return f'{seconds // 86400}天{seconds % 86400 // 3600}小时{seconds % 86400 % 3600 // 60}分{seconds % 86400 % 3600 % 60}秒'


def file_operation(_path, data=None, **kwargs):
    """
    操作文件
    :param _path:
    :param data:
    :param kwargs:
    :return:
    """
    lock = FileLock(_path + ".lock")
    with lock:
        with open(_path, **kwargs) as f:
            if data:
                f.write(data)
            else:
                data = f.read()
    lock.release()
    return data


# 生成盐值
def generate_salt():
    return os.urandom(16).hex()


def analyzing_info(info) -> list:
    """
    按照一定的规则解析字符串
    字符串示例：
    {% code %}
    def name():
        return "你好呀"
    {% codeend %}
    {% text %}
    书小白，{{ name }}
    {% text %}
    """
    code_value = {}
    value = ''
    for code in re.findall('\{% code %\}(.*?)\{% codeend %\}', info, re.S):
        code = code.strip()
        fun_name = re.findall('def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\):', code)[0]
        exec(code, globals(), locals())
        result = locals()[fun_name]()
        code_value[fun_name] = result
    for v in re.findall('\{% text %\}(.*?)\{% textend %\}', info, re.S):
        v = v.strip()
        code_names = re.findall('\{\{ (.*?) \}\}', v)
        for code_name in code_names:
            v = v.replace('{{ %s }}' % code_name, code_value.get(code_name, ''))
        value += "，" + v
    return value[1:] if value else info.strip()


if __name__ == '__main__':
    a = """
    {% code %}
    def name():
        return "你好呀"
    {% codeend %}
    {% text %}
    书小白，{{ name }}
    {% textend %}
    """
    print(analyzing_info(a))
