# -*- coding: UTF-8 -*-
import json
import os
from urllib import parse

from Fuction import request_data

alist_host = ''  # alist域名
alist_token = ''  # alist令牌


def login(user_name, password):
    url = f"{alist_host}/api/auth/login"
    data = {
        "username": user_name,
        "password": password,
        "otp_code": ""
    }
    res = request_data("POST", url, json=data, )
    return res


# 搜索文件
def search(file_name, page: int = 1, per_page: int = 100):
    url = f'{alist_host}/api/fs/search'
    header = {"Authorization": alist_token, }
    body = {"parent": "/",
            "keywords": file_name,
            "page": page,
            "per_page": per_page
            }

    return request_data("post", url, json=body, headers=header, timeout=30)


# 获取下载信息
def fs_get(path):
    url = f'{alist_host}/api/fs/get'
    header = {"Authorization": alist_token,
              'Cache-Control': 'no-cache'
              }
    body = {"path": path}
    return request_data("post", url, json=body, headers=header, timeout=30)


# 查询指定存储信息
def storage_get(storage_id):
    url = f'{alist_host}/api/admin/storage/get?id={str(storage_id)}'
    header = {"Authorization": alist_token}

    return request_data("get", url, headers=header, timeout=30)


# 新建存储
def storage_create(body):
    url = f'{alist_host}/api/admin/storage/create'
    header = {'Authorization': alist_token}

    return request_data("post", url, json=body, headers=header, timeout=30)


# 更新存储
def storage_update(body):
    url = f'{alist_host}/api/admin/storage/update'
    header = {"Authorization": alist_token}

    return request_data("post", url, json=body, headers=header, timeout=30)


# 获取存储列表
def storage_list():
    url = f'{alist_host}/api/admin/storage/list'
    header = {"Authorization": alist_token, }

    return request_data("get", url, headers=header, timeout=30)


# 删除指定存储
def storage_delete(storage_id):
    url = f'{alist_host}/api/admin/storage/delete?id={str(storage_id)}'
    header = {"Authorization": alist_token}

    return request_data("post", url, headers=header, timeout=30)


# 开启存储
def storage_enable(storage_id):
    url = f'{alist_host}/api/admin/storage/enable?id={str(storage_id)}'
    header = {"Authorization": alist_token}

    return request_data("post", url, headers=header, timeout=30)


# 关闭存储
def storage_disable(storage_id):
    url = f'{alist_host}/api/admin/storage/disable?id={str(storage_id)}'
    header = {"Authorization": alist_token}

    return request_data("post", url, headers=header, timeout=30)


# 上传文件
# from https://github.com/lym12321/Alist-SDK/blob/dde4bcc74893f9e62281482a2395abe9a1dd8d15/alist.py#L67

def upload(local_path, remote_path, file_name):
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    url = f'{alist_host}/api/fs/put'
    header = {
        'UserAgent': useragent,
        'Authorization': alist_token,
        'File-Path': parse.quote(f'{remote_path}/{file_name}'),
        'Content-Length': f'{os.path.getsize(local_path)}'
    }

    return json.loads(
        request_data("put", url, headers=header, data=open(local_path, 'rb').read()).text)


# 获取列表，强制刷新列表

def refresh_list(path, per_page: int = 0):
    url = f'{alist_host}/api/fs/list'
    header = {"Authorization": alist_token}
    body = {"path": path, "page": 1, "per_page": per_page, "refresh": True}

    return request_data("post", url, json=body, headers=header, timeout=30)


def delete_file(path: str, names: list):
    url = f'{alist_host}/api/fs/remove'
    header = {"Authorization": alist_token}
    data = {
        'dir': path,
        'names': names
    }
    return request_data("post", url, headers=header, json=data)


def driver_info(driver):
    url = f'{alist_host}/api/admin/driver/info?driver={driver}'
    header = {"Authorization": alist_token}
    return request_data('GET', url=url, headers=header)


# 获取驱动列表

def get_driver():
    url = f'{alist_host}/api/admin/driver/list'
    header = {"Authorization": alist_token}

    return request_data("get", url, headers=header, timeout=30)


def alist_mkdir(path):
    url = f'{alist_host}/api/fs/mkdir'
    header = {"Authorization": alist_token}
    data = {
        "path": path
    }
    return request_data("POST", url, headers=header, json=data)


def put_file(data, path):
    url = f'{alist_host}/api/fs/put'
    header = {"Authorization": alist_token,
              'File-Path': parse.quote(path),
              'Content-Type': 'multipart/form-data',

              }
    files = {'files': (os.path.split(path)[-1], data)}
    return request_data("PUT", url, headers=header, files=files)
