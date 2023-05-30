import requests
import re
import time
import random
from tqdm import tqdm

class Bili():
    def __init__(self):

        # 填你的b站uid
        self.uid = ''
        # 先找cookie，抓下来以后找里面的bili_jct
        self.crsf = ''
        self.cookie = {'Cookie': ''}
        self.header = {'User-Agent': ''}

        # 转发时候自己输入的那句话，可以不填
        self.str_list = ['来当分母= =', '让我中一次吧QAQ', '继续分母', '转发动态', '单纯想中次奖']
        self.len_strlist = len(self.str_list) - 1

        self.sendurl = 'https://api.bilibili.com/x/dynamic/feed/create/dyn?csrf={}'.format(self.crsf)
        self.followurl = 'http://api.bilibili.com/x/relation/modify'

    def get(self):
        res = requests.get(geturl1, cookies=self.cookie, headers=self.header)
        cards = res.json().get('data').get('cards')
        for card in cards:
            card1 = card.get('card')
            pattern = re.compile('"orig_dy_id": (.*?), "pre_dy_id.*?uid": (.*?), "uname', re.S)
            items = re.findall(pattern, card1)
            for item in items:
                yield {
                    'dynamic_id': item[0],
                    'uid': item[1]
                }

    def follow(self):
        data = {
            'fid': item['uid'],
            'act': 1,
            're_src': 11,
            'jsonp': 'jsonp',
            'csrf': self.crsf
        }
        requests.post(self.followurl, data=data, cookies=self.cookie, headers=self.header)

    def send(self):
        data = {
            "dyn_req": {
                "content": {
                    "contents": [
                        {
                            # 转发时候自己输入的那句话
                            "raw_text": self.str_list[random.randint(0, self.len_strlist)],
                            "type": 1,
                            "biz_id": ""
                        }
                    ]
                },
                "scene": 4,
                "meta": {
                    "app_meta": {
                        "from": "create.dynamic.web",
                        "mobi_app": "web"
                    }
                }
            },
            "web_repost_src": {
                "dyn_id_str": item['dynamic_id']
            }
        }
        requests.post(self.sendurl, json=data, cookies=self.cookie, headers=self.header)

if __name__ == "__main__":
    # 这个是关键，你要去找一些b站上的抽奖号的uid，填进去就能转发他们的动态了
    host_uids = []
    geturl = 'http://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=%s&offset_dynamic_id=0'
    sum = 0
    bili = Bili()
    for host_uid in host_uids:
        i = 0
        j = 0
        geturl1 = geturl % (host_uid)
        for item in tqdm(bili.get()):
            time.sleep(random.randint(5, 10))
            try:
                with open("data/dynamic_id.txt", "r", encoding="utf-8") as f:
                    data = f.read()
                    dynamic_ids = list(data.split(','))
                f.close()
                if item['dynamic_id'] not in dynamic_ids:
                    try:
                        with open("data/dynamic_id.txt", "a", encoding="utf-8") as f1:
                            f1.write(',' + item['dynamic_id'])
                        f1.close()
                        try:
                            with open("data/follow_id.txt", "r", encoding="utf-8") as f:
                                data = f.read()
                                follow_ids = list(data.split(','))
                            f.close()
                            if item['uid'] not in follow_ids:
                                bili.follow()
                                try:
                                    with open("data/follow_id.txt", "a", encoding="utf-8") as f2:
                                        f2.write(',' + item['uid'])
                                    f2.close()
                                except:
                                    print("写入关注失败，当前id为：" + item['dynamic_id'])
                        except:
                            print("获取关注失败" + item['uid'])
                        bili.send()
                        time.sleep(random.randint(5, 10))
                        j += 1
                    except:
                        print('写入动态失败, 当前id为：' + item['dynamic_id'])
            except:
                print("搜索失败, 当前id为：" + item['dynamic_id'])
            i += 1
            if i % 10 == 0:
                time.sleep(random.randint(10, 25))
        time.sleep(random.randint(25, 35))
        sum += j
    print("sum:" + str(sum))