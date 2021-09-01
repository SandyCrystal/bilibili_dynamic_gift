import requests
import re
import time
import pymysql
import random
from tqdm import tqdm

class Bili():
    def __init__(self):
        self.sendurl = 'http://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost'
        self.followurl = 'http://api.bilibili.com/x/relation/modify'

        # 填你的b站uid
        self.uid = ''
        # 先找cookie，抓下来以后找里面的bili_jct，以前叫crsf，懒得改了
        self.crsf = ''
        # 不会抓百度
        self.cookie = {'Cookie': ''}
        # 网上随便找个好了
        self.header = {'User-Agent': ''}

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
            'uid': self.uid,
            'dynamic_id': item['dynamic_id'],
            'content' : str_list[random.randint(0, 4)],
            'ctrl': '[{"data":"5581898","location":2,"length":4,"type":1},{"data":"10462362","location":7,"length":5,"type":1},{"data":"1577804","location":13,"length":4,"type":1}]',
            'csrf_token': self.crsf
        }
        requests.post(self.sendurl, data=data, cookies=self.cookie, headers=self.header)

if __name__ == "__main__":
    # 这个是关键，你要去找一些b站上的抽奖号的uid，填进去就能转发他们的动态了
    host_uids = []
    geturl = 'http://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=%s&offset_dynamic_id=0'
    sum = 0
    str_list = ['来当分母= =', '让我中一次吧QAQ', '继续分母', '转发动态', '单纯想中次奖']
    bili = Bili()
    for host_uid in host_uids:
        i = 0
        j = 0
        geturl1 = geturl % (host_uid)
        for item in tqdm(bili.get()):
            time.sleep(random.randint(1,5))
            # 数据库配置一下,具体配置写别的地方了
            db = pymysql.connect(host="", port=3306, user="", password="", db="", charset='utf8')
            cursor = db.cursor()
            insert_sql = "insert into bili (content_id) values ('%s')" % item['dynamic_id']
            select_sql = "select * from bili where content_id = " + item['dynamic_id']
            select_follow_sql = "select * from follow where follow_id = " + item['uid']
            insert_follow_sql = "insert into follow (follow_id) values (%s)" % item['uid']
            try:
                cursor.execute(select_sql)
                results = cursor.fetchall()
                if(len(results)==0):
                    try:
                        cursor.execute(insert_sql)
                        try:
                            cursor.execute(select_follow_sql)
                            results1 = cursor.fetchall()
                            if(len(results1)==0):
                                bili.follow()
                                cursor.execute(insert_follow_sql)
                        except:
                            print("获取关注失败" + item['uid'])
                        bili.send()
                        j = j+1
                        db.commit()
                    except:
                        db.rollback()
                        print('插入失败, 当前id为：' + item['dynamic_id'])
            except:
                print("搜索失败, 当前id为：" + item['dynamic_id'])
            db.close()
            i = i + 1
            if i % 10 == 0:
                time.sleep(random.randint(5,15))
        time.sleep(random.randint(25,35))
        print("第" + str(i) + "个" + ":" + str(j))
        sum = sum+j
    print("sum:" + str(sum))