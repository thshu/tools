import base64
import hashlib
import io
import os.path
import time

from tqdm import tqdm

from Fuction import request_data


class AliyundriveOpen(object):
    def __init__(self, client_id, client_secret):
        self.base_url = 'https://openapi.alipan.com'
        self.client_id = client_id
        self.client_secret = client_secret

        self.headers = {
            'Content-Type': 'application/json'
        }
        self.Authorization = None

    def get_qr_sid(self):
        """
        获取登录二维码
        """
        url = self.base_url + '/oauth/authorize/qrcode'
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": [
                "user:base",
                "file:all:read",
                "file:all:write"
            ],
            "width": 430,
            "height": 430
        }
        res = request_data('POST', url=url, headers=self.headers, json=data)
        return res.json()['sid']

    def sid_status(self, sid):
        """
        根据sid获取二维码扫码结果
        """
        url = self.base_url + f'/oauth/qrcode/{sid}/status'
        res = request_data('GET', url=url, headers=self.headers)
        res_json = res.json()
        if res_json['status'] == 'LoginSuccess':
            res_json['msg'] = '登录成功'
        elif res_json['status'] == 'WaitLogin':
            res_json['msg'] = '等待扫码'
        elif res_json['status'] == 'ScanSuccess':
            res_json['msg'] = '等待授权'
        elif res_json['status'] == 'QRCodeExpired':
            res_json['msg'] = '二维码已失效'

        return res_json

    def get_access_token(self, grant_type, value):
        """
        获取access_token
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type,
        }
        if grant_type == 'authorization_code':
            data['code'] = value
        elif grant_type == 'refresh_token':
            data['refresh_token'] = value
        url = self.base_url + '/oauth/access_token'
        res = request_data('POST', url=url, headers=self.headers, json=data)
        return res.json()

    def set_authorization(self, value):
        self.Authorization = value

    def second_transmission(self, drive_id, parent_file_id, path, name, _type='file', check_name_mode='auto_rename',
                            number_shards=0):

        url = self.base_url + '/adrive/v1.0/openFile/create'
        headers = self.headers.copy()
        part_info_list = [{'part_number': i} for i in range(1, number_shards + 1)]
        headers['Authorization'] = self.Authorization
        data = {
            "drive_id": drive_id,
            "part_info_list": part_info_list,
            "parent_file_id": parent_file_id,
            "name": name,
            "type": "file",
            "check_name_mode": "auto_rename",
            "content_hash_name": "sha1",
            "size": os.path.getsize(path),
            'proof_code': self.calculate_proof_code(path),
            'content_hash': self.get_content_hash(path).upper()
        }
        res = request_data('POST', url=url, headers=headers, json=data)
        return res

    def create_file(self, drive_id, parent_file_id, path, name, _type='file', check_name_mode='auto_rename',
                    number_shards=0):
        """
        创建文件
        """
        url = self.base_url + '/adrive/v1.0/openFile/create'
        headers = self.headers.copy()
        part_info_list = [{'part_number': i} for i in range(1, number_shards + 1)]
        headers['Authorization'] = self.Authorization
        data = {
            'check_name_mode': check_name_mode,
            "drive_id": drive_id,
            "parent_file_id": parent_file_id,
            "name": name,
            "type": _type,
            'part_info_list': part_info_list,
            'size': os.path.getsize(path)
        }
        with open(path, 'rb') as f:
            d = f.read(1024)
        sha1_hash = hashlib.sha1()
        sha1_hash.update(d)
        data["pre_hash"] = sha1_hash.hexdigest()
        res = request_data('POST', url=url, headers=headers, json=data)
        return res

    def get_upload_url(self, drive_id, file_id, upload_id):
        """
        刷新获取上传地址
        """
        url = self.base_url + '/adrive/v1.0/openFile/getUploadUrl'
        headers = self.headers.copy()
        headers['Authorization'] = self.Authorization
        data = {
            "drive_id": drive_id,
            "file_id": file_id,
            "upload_id": upload_id,
        }
        res = request_data('POST', url=url, headers=headers, json=data)
        return res.json()

    def complete_upload(self, drive_id, file_id, upload_id):
        """
        完成上传
        """
        url = self.base_url + '/adrive/v1.0/openFile/complete'
        headers = self.headers.copy()
        headers['Authorization'] = self.Authorization
        data = {
            "drive_id": drive_id,
            "file_id": file_id,
            "upload_id": upload_id,
        }
        res = request_data('POST', url=url, headers=headers, json=data)
        return res.json()

    def list_uploaded_parts(self, drive_id, file_id, upload_id):
        """
        列举已上传分片
        """
        url = self.base_url + '/adrive/v1.0/openFile/listUploadedParts'
        data = {
            'drive_id': drive_id,
            'file_id': file_id,
            'upload_id': upload_id,
        }
        headers = self.headers.copy()
        headers['Authorization'] = self.Authorization
        res = request_data('POST', url, json=data, headers=headers)
        return res

    def upload_file(self, url, data):
        """
        上传文件
        """
        res = request_data('PUT', url=url, data=data)
        time.sleep(1)
        return res

    def calculate_proof_code(self, path):
        """
        计算秒传需要的proof_code
        """
        file_size = os.path.getsize(path)
        # 如果文件大小为0，直接返回
        if file_size == 0:
            return None
        # 计算文件大小的模值
        access_token_md5 = hashlib.md5(self.Authorization[7:].encode()).hexdigest()
        truncated_md5 = access_token_md5[:16]
        tmp_int = int(truncated_md5, 16)
        index = tmp_int % file_size
        # 读取指定范围的文件数据
        with open(path, "rb") as file:
            file.seek(index)
            data_range = file.read(8)
        # 计算 proof_code
        proof_code = base64.b64encode(data_range).decode()
        return proof_code

    def get_content_hash(self, path, block_size=io.DEFAULT_BUFFER_SIZE):
        def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
            while True:
                chunk = file.read(size)
                if not chunk:
                    break
                yield chunk

        h = hashlib.sha1()
        with open(path, 'rb') as f:
            file_size = os.path.getsize(path)
            with tqdm(total=file_size, unit='B', unit_scale=True, desc='Hashing', leave=False) as pbar:
                for block in read_chunks(f, size=block_size):
                    h.update(block)
                    pbar.update(len(block))
        return h.hexdigest()

    def upload_file_main(self, drive_id, parent_file_id, file_path, authorization):
        """
        上传文件的主函数
        """
        self.set_authorization(authorization)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        byte_count = int(4 * (1024 ** 2))
        number_shards = (file_size // byte_count) + 1
        create_file_res = self.create_file(drive_id=drive_id, parent_file_id=parent_file_id, name=file_name,
                                           number_shards=number_shards, path=file_path, check_name_mode='refuse')
        if create_file_res.status_code == 400:
            create_file_res = self.second_transmission(drive_id=drive_id, parent_file_id=parent_file_id, name=file_name,
                                                       number_shards=number_shards, path=file_path)
            if create_file_res.json().get('rapid_upload'):
                return True
        create_file_res = create_file_res.json()
        file_id = create_file_res.get('file_id')
        part_info_list = create_file_res.get('part_info_list')
        upload_id = create_file_res.get('upload_id')
        upload_completed = True
        part_number_list = []
        while upload_completed:
            for part_info in part_info_list:
                put_url = part_info.get('upload_url')
                part_number = int(part_info.get('part_number'))
                if part_number in part_number_list:
                    continue
                with open(file_path, 'rb') as f:
                    f.seek((part_number - 1) * byte_count)
                    data = f.read(byte_count)
                self.upload_file(put_url, data)
            res = self.list_uploaded_parts(drive_id=drive_id, file_id=file_id,
                                           upload_id=upload_id)
            res_json = res.json()
            uploaded_parts = res_json.get('uploaded_parts')
            if len(uploaded_parts) == len(part_info_list):
                upload_completed = False
            else:
                part_number_list = [i.get('part_number') for i in uploaded_parts]
        res = self.complete_upload(drive_id, file_id, upload_id)
        return res.get('status') == 'available'
