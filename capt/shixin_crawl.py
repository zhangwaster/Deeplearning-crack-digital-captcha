from urllib import request
from urllib.parse import quote_plus
from capt.predict import cl_captcha
import uuid
from capt.cfg import captcha_cache
import os
import shutil
import pymongo as pm
import time
import json

# 700010758
id_min = 700000000
id_max = 700000100

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
}


form_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
    'Content-Type':'application/x-www-form-urlencoded'
}

h__c = cl_captcha()

# 破解验证码
def hack_captcha():
    url = "http://shixin.court.gov.cn/captchaNew.do?captchaId=2ec8eb6e46b642929cefc6c1879d9371"
    req = request.Request(url, headers=headers)

    try:
        # 正常情况下，这是个图片，在访问特别平凡的情况下，是个html,可能引发异常
        # 可能发生 http.client.IncompleteRead 错误
        image = request.urlopen(req,timeout=20).read()
        # 保存随机文件
        file_name = os.path.join(captcha_cache, str(uuid.uuid1()) + '.jpg')
        f = open(file_name, "wb")
        f.write(image)
        f.close()
        text = h__c.hack_capt(file_name)
        # 保存预测结果,重新命名文件
        new_file = os.path.join(captcha_cache, text + '_' + str(uuid.uuid1()) + '.jpg')
        shutil.move(file_name, new_file)
        return text
    except:
        print("hack_captcha() 发生异常！！！")
        # 发生异常，一般是获取太频繁
        return ""


# 检查验证码是否破解正确
def check_captcha(capt):
    if capt == "":
        return False
    url = "http://shixin.court.gov.cn/findDisNew"
    err_msg = "验证码错误或验证码已过期"
    form_data_base = "pName=朱军&pCardNum=&pProvince=0&pCode=%s&captchaId=2ec8eb6e46b642929cefc6c1879d9371"
    form_data = form_data_base % capt
    try:
        req = request.Request(url, headers=form_headers, data=bytes(form_data, encoding = "utf8"))
        page = request.urlopen(req, timeout=20).read()
    except:
        # 超时
        return False
    html = page.decode('utf-8')
    if html.find(err_msg) == -1:
        # 没有找到错误信息
        return True
    else:
        return False


# 存储json到数据库mongo
def store_data(html,index):
    uri = "mongodb://root:yYGHv7XaxoXnpC9Uuilt@dds-uf65b2acb8df60541.mongodb.rds.aliyuncs.com:3717," \
          "dds-uf65b2acb8df60542.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-5185593"

    mongo = pm.MongoClient(uri)
    db = mongo.shixin
    i = str(index)
    if(html.find(i)==-1):
        print("warning: 数据有问题！ %s" % i)
    pass
    while True:
        try:
            db.black_list.insert({'_id': index, 'value':html})
        except pm.errors.DuplicateKeyError as e:
            # 重复主键
            break
        except pm.errors.ServerSelectionTimeoutError as e:
            # 链接超时
            print("error: mongo链接超时，请恢复")
            time.sleep(10)
            # 无限重试
            continue
        finally:
            break
    pass
    mongo.close()
    pass



# 获取当前开始的索引
def start_index():
    return id_min


# 存储索引
def store_index():
    pass


# 输入：索引，输出：json
def crawl_by_index(index, capt):
    # 拼接url, 获取数据
    base_url = "http://shixin.court.gov.cn/disDetailNew?captchaId=2ec8eb6e46b642929cefc6c1879d9371&id=%s&pCode=%s"
    hack_url = base_url % (index, capt)
    print("info: begin crawl_by_index() %s" % hack_url)
    req = request.Request(hack_url, headers=headers)
    # 如果超时，重试
    html = "{网站访问超时}"
    try:
        page = request.urlopen(req, timeout=20).read()
        html = page.decode('utf-8')
    except:
        #超时
        pass
    print("info: end crawl_by_index() %s" % html)
    return html


def hack_and_check_captcha():
    while True:
        text = hack_captcha()
        if text == "": # 验证码获取失败
            print("error:获取验证码失败,等待30秒")
            time.sleep(30)
            continue

        if(check_captcha(text) == True):
            print("info:成功破解验证码：%s" % text)
            return text
        else:
            # 验证码破解失败，继续获取新的验证码，间隔0.2秒
            print("info:验证码破解失败")
            time.sleep(0.2)
            continue
    pass

# 爬虫入口函数，暂时不用scrapy
def shixin_crawl():
    start = start_index()

    # 获取一个可用的capt
    capt = hack_and_check_captcha()
    while start < id_max:
        # 每次爬去数据等待0.5秒
        time.sleep(0.5)
        print("info:开始爬取用户，%d" % start)
        html = crawl_by_index(start, capt)
        if(html == "{}"): #无效数据
            # 可能是不存在的id，也可能是capt过期
            if(check_captcha(capt) == True):
                # 如果验证码有效，那么该用户不存在，跳过这个用户
                print("info:用户%d不存在" % start)
                start += 1
                continue
            else:
                # 验证码失效,直接继续，从新获取验证码
                print("info:验证码失效在第%d个用户" % start)
                capt = hack_and_check_captcha()
                continue
            pass
        elif (html.find("网站当前访问量较大") > 0):
            # 访问量太大，需要等待30秒
            print("info:网站当前访问量较大, 等待30秒")
            time.sleep(30)
            pass
        elif (html.find("网站访问超时") > 0):
            # 访问量太大，需要等待30秒
            print("info:网站当前访问量较大, 等待1秒")
            time.sleep(1)
            pass
        elif (html.find("请开启JavaScript并刷新该页") > 0):
            print("info:请开启JavaScript并刷新该页, 等待30秒")
            # 访问量太大，需要等待30秒
            time.sleep(30)
            pass
        else: #有效数据，存储到数据库
            print("info:有效用户数据%d" % start)
            store_data(html, start)
            start += 1
    pass

if __name__ == '__main__':
    #ret = check_captcha("jvhw")
    #print(ret)
    #print(hack_captcha())
    #print(hack_captcha())
    shixin_crawl()
    print("end")