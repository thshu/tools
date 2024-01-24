import json
import re
import time
import zlib
from urllib.parse import urljoin

import parsel
import xmltodict
from tqdm import tqdm

from Fuction import request_data


class GetDanmuBase(object):
    base_xml = '''<?xml version="1.0" encoding="utf-8"?>
<i>
{}
</i>'''
    data_list = []
    name = ""
    domain = ""

    def error(self, msg):
        return {
            "msg": msg,
            "start": 500,
            "data": None,
            "name": self.name
        }

    def success(self, data):
        return {
            "msg": "success",
            "start": 0,
            "data": data,
            "name": self.name
        }

    def get_data_dict(self):
        return dict(
            timepoint=0,  # 弹幕发送时间（秒）
            ct=1,  # 弹幕类型，1-3 为滚动弹幕、4 为底部、5 为顶端、6 为逆向、7 为精确、8 为高级
            size=25,  # 字体大小，25 为中，18 为小
            color=16777215,  # 弹幕颜色，RGB 颜色转为十进制后的值，16777215 为白色
            unixtime=int(time.time()),  # Unix 时间戳格式
            uid=0,  # 发送人的 id
            content=""
        )

    def main(self, url, _type):
        """
        获取弹幕的主逻辑
        """
        pass

    def parse(self, _type):
        """
        解析返回的原始数据
        :param _type: 数据类型，xml 或 list
        """
        pass

    def get(self, url, _type='xml'):
        self.data_list = []
        try:
            return self.main(url, _type)
        except Exception as e:
            return self.error("程序出现错误:" + e)

    def list2xml(self, data):
        xml_str = f'    <d p="{data.get("timepoint")},{data.get("ct")},{data.get("size")},{data.get("color")},{data.get("unixtime")},0,{data.get("uid")},26732601000067074,1">{data.get("content")}</d>'
        return xml_str

    def time_to_second(self, _time: list):
        s = 0
        m = 1
        for d in _time[::-1]:
            s += m * int(d)
            m *= 60
        return s


class GetDanmuTencent(GetDanmuBase):
    name = "腾讯视频"
    domain = "v.qq.com"

    def __init__(self):
        self.api_danmaku_base = "https://dm.video.qq.com/barrage/base/"
        self.api_danmaku_segment = "https://dm.video.qq.com/barrage/segment/"

    def parse(self, _type):
        data_list = []
        for data in tqdm(self.data_list):
            for item in data.get("barrage_list", []):
                _d = self.get_data_dict()
                _d['timepoint'] = int(item.get("time_offset", 0)) / 1000
                _d["content"] = item.get("content", "")
                _d['unixtime'] = item.get('create_time')
                if item.get("content_style") != "":
                    content_style = json.loads(item.get("content_style"))
                    if content_style.get("color") != "ffffff":
                        _d['color'] = int(content_style.get("color", "ffffff"), 16)
                if _type == "xml":
                    data_list.append(self.list2xml(_d))
                else:
                    data_list.append(_d)
        return data_list

    def main(self, url, _type):
        self.data_list = []
        res = request_data("GET", url)
        sel = parsel.Selector(res.text)
        title = sel.xpath('//title/text()').get()
        vid = re.findall(f'"title":"{title}","vid":"(.*?)"', res.text)[-1]
        if not vid:
            vid = re.search("/([a-zA-Z0-9]+)\.html", url)
            if vid:
                vid = vid.group(1)
        if not vid:
            return self.error("解析vid失败，请检查链接是否正确")
        res = request_data("GET", urljoin(self.api_danmaku_base, vid))
        if res.status_code != 200:
            return self.error("获取弹幕详情失败")

        for k, segment_index in res.json().get("segment_index", {}).items():
            self.data_list.append(
                request_data("GET",
                             urljoin(self.api_danmaku_segment,
                                     vid + "/" + segment_index.get("segment_name", "/"))).json())
        parse_data = self.parse(_type)
        if _type == 'xml':
            return self.base_xml.format('\n'.join(parse_data))
        return parse_data


class GetDanmuBilibili(GetDanmuBase):
    name = "B站"
    domain = "bilibili.com"

    def __init__(self):
        self.api_video_info = "https://api.bilibili.com/x/web-interface/view"
        self.api_epid_cid = "https://api.bilibili.com/pgc/view/web/season"

    def parsel(self, xml_data):
        data_list = re.findall('<d p="(.*?)">(.*?)<\/d>', xml_data)
        for data in tqdm(data_list):
            _d = self.get_data_dict()
            _d['content'] = data[1]
            data_time = data[0].split(",")
            _d["timepoint"] = float(data_time[0])
            _d['ct'] = data_time[1]
            _d['size'] = data_time[2]
            _d['color'] = data_time[3]
            _d['unixtime'] = data_time[4]
            _d['uid'] = data_time[6]
            self.data_list.append(_d)
        return self.data_list

    def main(self, url: str, _type):
        # 番剧
        if url.find("bangumi/") != -1 and url.find("ep") != -1:
            epid = url.split('?')[0].split('/')[-1]
            params = {
                "ep_id": epid[2:]
            }
            res = request_data("GET", url=self.api_epid_cid, params=params, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            res_json = res.json()
            if res_json.get("code") != 0:
                return self.error("获取番剧信息失败")
            for episode in res_json.get("result", {}).get("episodes", []):
                if episode.get("id", 0) == int(epid[2:]):
                    xml_data = request_data("GET", f'https://comment.bilibili.com/{episode.get("cid")}.xml').text
                    if _type == 'xml':
                        return xml_data
                    else:
                        return self.parsel(xml_data)


class GetDanmuIqiyi(GetDanmuBase):
    name = "爱奇艺"
    domain = "iqiyi.com"

    def parse(self, _type):
        data_list = []
        for data in tqdm(self.data_list):
            # 解压缩数据
            decompressed_data = zlib.decompress(data)
            data = decompressed_data.decode('utf-8')
            for d in re.findall('<bulletInfo>.*?</bulletInfo>', data, re.S):
                d_dict = xmltodict.parse(d).get("bulletInfo")
                _d = self.get_data_dict()
                _d["timepoint"] = int(d_dict.get("showTime"))
                _d["content"] = d_dict.get("content")
                _d["color"] = int(d_dict.get("color"), 16)
                _d["size"] = int(d_dict.get("font"))
                if _type == "xml":
                    data_list.append(self.list2xml(_d))
                else:
                    data_list.append(_d)
        return data_list

    def main(self, url, _type):
        res = request_data("GET", url=url, headers={
            "Accept-Encoding": "gzip,deflate,compress"
        })
        tv_id = re.findall('"tvId":([0-9]+)', res.text)[0]
        album_id = int(re.findall('"albumId":([0-9]+)', res.text)[0])
        category_id = re.findall('"cid":([0-9]+)', res.text)[0]
        duration = re.findall('"duration":"([0-9]+):([0-9]+)"', res.text)[0]
        s = self.time_to_second(duration)
        page = round(s / (60 * 5))

        for i in range(0, page):
            url = f"https://cmts.iqiyi.com/bullet/{tv_id[-4:-2]}/{tv_id[-2:]}/{tv_id}_300_{i + 1}.z"
            params = {
                'rn': "0.0123456789123456",
                'business': "danmu",
                'is_iqiyi': "true",
                'is_video_page': "true",
                'tvid': tv_id,
                'albumid': album_id,
                'categoryid': category_id,
                'qypid': '01010021010000000000',
            }
            r = request_data("GET", url=url, params=params,
                             headers={'Content-Type': 'application/octet-stream'}).content
            self.data_list.append(r)
        parse_data = self.parse(_type)
        if _type == "xml":
            return self.base_xml.format('\n'.join(parse_data))
        return parse_data


class GetDanmuMgtv(GetDanmuBase):
    name = "芒果TV"
    domain = "mgtv.com"

    def __init__(self):
        self.api_video_info = "https://pcweb.api.mgtv.com/video/info"
        self.api_danmaku = "https://galaxy.bz.mgtv.com/rdbarrage"

    def parse(self, _type):
        data_list = []
        for data in tqdm(self.data_list):
            if data.get("data", {}).get("items", []) is None:
                continue
            for d in data.get("data", {}).get("items", []):
                _d = self.get_data_dict()
                _d['timepoint'] = d.get('time', 0) / 1000
                _d['content'] = d.get('content', '')
                _d['uid'] = d.get('uid', '')
                if _type == "xml":
                    data_list.append(self.list2xml(_d))
                else:
                    data_list.append(_d)
        return data_list

    def main(self, url, _type):
        _u = url.split(".")[-2].split("/")
        cid = _u[-2]
        vid = _u[-1]
        params = {
            'cid': cid,
            'vid': vid,
        }
        res = request_data("GET", url=self.api_video_info, params=params)
        _time = res.json().get("data", {}).get("info", {}).get("time")
        end_time = self.time_to_second(_time.split(":")) * 1000
        for _t in range(0, end_time, 60 * 1000):
            self.data_list.append(
                request_data("GET", self.api_danmaku, params={
                    'vid': vid,
                    "cid": cid,
                    "time": _t
                }).json()
            )
        parse_data = self.parse(_type)
        if _type == "xml":
            return self.base_xml.format('\n'.join(parse_data))
        return parse_data
