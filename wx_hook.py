"""
详细接口文档见：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/doc-1040329 密码：vHCAG7IM
"""
import os

from Fuction import request_data

wx_hook_url = ""
data_path = "./"


def get_state():
    """
    获取微信状态  Q0000
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-27678639
    """
    res = request_data('POST', url=wx_hook_url, json={
        "type": "Q0000",
        "data": {
        }
    })
    return res


def send_content(send_user, content, data=None):
    """
    发送文本消息  Q0001
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-27676096
    """
    if not data:
        data = {
            "type": "Q0001",
            "data": {
                "wxid": send_user,
                "msg": content
            }
        }
    headers = {"content-type": "application/json"}
    res = request_data('POST', url=wx_hook_url, json=data, headers=headers)
    return res


def get_personal_information():
    """
    获取个人信息  Q0003
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-27889656
    """
    res = request_data('POST', url=wx_hook_url, json={
        "type": "Q0003",
        "data": {
        }
    })
    return res


def obtain_user(xid):
    """
    查询对象信息  Q0004
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-28615818
    """
    res = request_data("POST", wx_hook_url, json={"type": "Q0004", "data": {"wxid": xid}})
    return res


def get_friend_list():
    """
    获取好友列表  Q0005
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-28612335
    """
    res = request_data('POST', url=wx_hook_url, json={"type": "Q0005", "data": {"type": "1"}})
    return res.json()['result']


def get_group_list():
    """
    获取群列表   Q0006
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-28617101
    """
    res = request_data('POST', url=wx_hook_url, json={"type": "Q0006", "data": {"type": "1"}})
    return res.json()['result']


def get_official_account_list():
    """
    获取公众号列表 Q0007
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-28617223
    """
    res = request_data('POST', url=wx_hook_url, json={"type": "Q0007", "data": {"type": "1"}})
    return res.json()['result']


def get_user_list_by_group(xid):
    """
    获取指定群聊的成员   Q0008
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-28626229
    """
    res = request_data('POST', url=wx_hook_url, json={"type": "Q0008", "data": {"wxid": xid}})
    return res.json()['result']


def send_img(send_user, path):
    """
    发送图片    Q0010
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29054153
    """
    if 'http' in path:
        res = request_data('GET', path)
        path = os.path.join(data_path, '文件/temp.png')
        with open(path, mode='wb') as f:
            f.write(res.content)
    data = {
        "type": "Q0010",
        "data": {
            "wxid": send_user,
            "path": path
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def send_file(send_user, path, _type=None):
    """
    发送文件    Q0011
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29054299
    """
    if _type:
        res = request_data('GET', path)
        path = os.path.join(data_path, '文件/temp.%s' % _type)
        with open(path, mode='wb') as f:
            f.write(res.content)
    data = {
        "type": "Q0011",
        "data": {
            "wxid": send_user,
            "path": path
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def send_data(data):
    """
    发送消息   Q0009、Q0012、Q0013、Q0014、Q00015
    发送聊天记录、分享链接、小程序、音乐分享、xml
    """
    res = request_data('POST', wx_hook_url, json=data)
    return res


def confirm_receipt(xid, transferid):
    """
    确定收款    Q0016
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29691607
    """
    data = {
        "type": "Q0016",
        "data": {
            "wxid": xid,
            "transferid": transferid
        }
    }
    res = request_data('post', wx_hook_url, json=data)
    return res


def agree_with_friends(scene, v3, v4):
    """
    同意好友    Q0017
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29722609
    """
    data = {
        "type": "Q0017",
        "data": {
            "scene": scene,
            "v3": v3,
            "v4": v4
        }
    }
    request_data('POST', wx_hook_url, json=data)


def add_friends_by_v3(v3, content, scene=30):
    """
    添加好友--v3    Q0018
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29739888
    """
    data = {
        "type": "Q0018",
        "data": {
            "v3": v3,
            "content": content,
            "scene": scene,
            "type": 1
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def add_friends_by_wxid(wxid, content, scene=30):
    """
    添加好友—-wxid  Q0019
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29739919
    """
    data = {
        "type": "Q0019",
        "data": {
            "wxid": wxid,
            "content": content,
            "scene": scene
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def query_strangers(pq):
    """
    查询陌生人   Q0020
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29739946
    pd可以是QQ号或者手机号
    """
    data = {
        "type": "Q0020",
        "data": {
            "pq": pq
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def invite_group_chat(group_xid, xid, _type=1):
    """
    邀请进群    Q0021
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29745022
    """
    data = {
        "type": "Q0021",
        "data": {
            "wxid": group_xid,
            "objWxid": xid,
            "type": _type
        }
    }
    res = request_data('post', wx_hook_url, json=data)
    return res


def del_friends(xid):
    """
    删除好友    Q0022
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29745067
    """
    data = {
        "type": "Q0022",
        "data": {
            "wxid": xid
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def modify_remarks(xid, remark):
    """
    修改备注    Q0023
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29745102
    """
    data = {
        "type": "Q0023",
        "data": {
            "wxid": xid,
            "remark": remark
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def modify_group_remarks(xid, content):
    """
    修改群聊备注  Q0024
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-29745126
    """

    data = {
        "type": "Q0024",
        "data": {
            "wxid": xid,
            "nick": content
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def send_business_card(xid, _xml):
    """
    发送名片    Q0025
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-30373859
    """
    data = {
        "type": "Q0025",
        "data": {
            "wxid": xid,
            "xml": _xml
        }
    }
    res = request_data('POST', wx_hook_url, json=data)
    return res


def login():
    """
    获取登录二维码 Q0026
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-30832986
    """
    res = request_data('POST', wx_hook_url, json={"type": "Q0026", "data": {}})
    return res


def accessing_pictures(name):
    """
    访问图片
    接口文档：https://apifox.com/apidoc/shared-af49a169-8b5c-4137-a5ea-723a10e8e794/api-34212216
    """
    res = request_data("GET", wx_hook_url, params={'name': name})
    return res
