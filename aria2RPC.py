import base64
import hashlib
import time
from typing import List, Any

import requests


class Aria2RPC(object):
    def __init__(self, url, token=""):
        self.url = url
        self.base_json = {
            "jsonrpc": "2.0",
        }
        self.params: List[Any] = [
            f"token:{token}",
        ]

    def request(self, data: dict):
        """
        请求
        """
        res = requests.post(self.url, json=data)
        return res

    def get_data(self, method: str, params: List[Any]):
        data = self.base_json.copy()
        data['method'] = method
        data['params'] = params
        md5_hash = hashlib.md5()
        md5_hash.update(base64.b64encode(f'{params}_{int(time.time())}'.encode('utf-8')))
        data['id'] = md5_hash.hexdigest()
        return data

    def add(self, url: list, headers: dict = None, path=None, *args, **kwargs):
        """
        添加任务
        """
        if headers is None:
            headers = {}
        params = self.params.copy()
        if kwargs.get('type') == "bt":
            params.append(base64.b64encode(kwargs.get('bt_data')).decode('utf-8'))
            params.append([])
            method = "aria2.addTorrent"
        else:
            params.append(url)
            method = 'aria2.addUri'
        parameter = {}
        if path:
            parameter['dir'] = path
        header = []
        for k, v in headers.items():
            header.append(f'{k}:{v}')
        if header:
            parameter['header'] = header
        params.append(parameter)
        data = self.get_data(method, params)
        return self.request(data)

    def modify_task(self, gid: str, _type="暂停"):
        """
        修改任务的状态：
            暂停、开始、停止
        """
        params = self.params.copy()
        params.append(gid)
        method = 'aria2.pause'  # 默认为暂停
        if _type == '开始':
            method = 'aria2.unpause'
        if _type == '停止':
            method = 'aria2.remove'
        if _type == '删除':
            method = "aria2.removeDownloadResult"
        data = self.get_data(method, params)
        res = self.request(data)
        if res.status_code != 200 and _type == '删除':
            method = 'aria2.forceRemove'
            data = self.get_data(method, params)
            res = self.request(data)
        return res

    def get_task(self, _type='Active'):
        """
        获取队列中的下载任务

        _type:
            Active：正在下载
            Waiting：等待下载
            Stopped：已完成、已停止

        """
        params = self.params.copy()
        if _type == 'Waiting':
            params.append(0)
            params.append(1000)
        if _type == 'Stopped':
            params.append(-1)
            params.append(1000)

        params.append([
            "gid",
            "dir",
            "totalLength",
            "completedLength",
            "uploadSpeed",
            "downloadSpeed",
            "connections",
            "numSeeders",
            "seeder",
            "status",
            "errorCode",
            "verifiedLength",
            "verifyIntegrityPending",
            "files",
            "bittorrent",
            "infoHash"
        ])
        data = self.get_data(f'aria2.tell{_type}', params)
        return self.request(data)

    def get_status(self):
        """
        获取服务器的下载状态
        """
        data = self.get_data('aria2.getGlobalStat', self.params)
        return self.request(data)

    def get_task_status(self, gid):
        """
        获取任务的状态
        """
        params = self.params.copy()
        params.append(gid)
        params.append([
            "gid",
            "status",
            "errorCode",
            "errorMessage",
            "totalLength",
            "completedLength",
            "downloadSpeed",
            "uploadLength",
            "uploadSpeed",
            "numSeeders",
            "numPeers",
            "connections",
            "numPieces",
            "pieceLength",
            "infoHash",
            "seeder",
            "dir",
            "files",
            "bittorrent"
        ])
        data = self.get_data('aria2.tellStatus', params)
        return self.request(data)
