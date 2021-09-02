from requests import get
from json import loads
from pprint import pprint

url = 'http://127.0.0.1:5700/'

api = lambda api_name,**data:loads(get(url+api_name+'?'+'&'.join(f"{k}={v}" for k,v in data.items())).content)


r = api("send_msg",
    user_id="527956285",
    message_type="private",
    message="你好啊",
    )
pprint(r)

##r = api("delete_msg",
##    message_id="-1794901080"
##    )
##pprint(r)


##r = api(".get_word_slices",
##        content="请输入以下参数")
##pprint(r)

##r = api("ocr_image",image="86eaebffee59cd51aca14c1e9ede46b1.image")
##pprint(r)


def get_members(group_id):
    r = api("get_group_member_list",group_id=group_id)["data"]
    return {(i["user_id"],i["nickname"]) for i in r}


