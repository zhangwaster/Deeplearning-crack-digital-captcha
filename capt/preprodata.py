import pymongo as pm
import time
import json

def read_data():
    start = 700000000
    end   = 702457118 + 1
    uri = "mongodb://root:yYGHv7XaxoXnpC9Uuilt@dds-uf65b2acb8df60541.mongodb.rds.aliyuncs.com:3717," \
          "dds-uf65b2acb8df60542.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-5185593"

    mongo = pm.MongoClient(uri)
    db = mongo.shixin


    page_size = 1000
    total = db.black_list.find({"_id":{"$gt":start,"$lt":end}}).count()
    print("total:%d" % total)
    begin = 0
    duplicate = 0
    while(begin < total):
        new_user = []
        for old_user in db.black_list.find({"_id":{"$gt":start,"$lt":end}}).skip(begin).limit(page_size):
            #new_user.append()
            old_value = json.loads(old_user['value'])
            card = old_value['cardNum']
            dict = {'idcard':card,'value':old_value}
            new_user.append(dict)
            #print(dict)
            pass

        try:
            # batch insert
            db.court_blacklist.insert(new_user)
        except pm.errors.DuplicateKeyError as e:
            duplicate += 1
            pass
        except pm.errors.AutoReconnect as e:
            continue

        if (begin % 100000 == 0):
            print("process:" + str(begin))

        begin += page_size
    pass


    '''
    while (start < end):
        try:
            
            pair = db.black_list.find_one({"_id": start})
            # 分割key,value
            if(pair is not None):
            # 插入新表 sx_blacklist
                pd = json.loads(pair['value'])
                if (pd.__contains__('cardNum') == False):
                    print("ignored of cardNum:%d" % (start))
                    pass
                else:
                    total += 1
                    pass
                    db.sx_blacklist.insert({'_id': pd['cardNum'], 'value': pair['value']})
                pass
            else:
                #print("ignored:%d" % start)
                pass
            pass
            start += 1
            if(start % 100000 == 0):
                print("process:" + str(start))
            

        except pm.errors.AutoReconnect as e:
            continue
        except pm.errors.DuplicateKeyError as e:
            # 重复主键
            start += 1
            continue
        finally:
            pass
    pass
    '''


    mongo.close()
    print("end, total:%d,duplicate:%d" % (total,duplicate))
    pass


if __name__ == '__main__':
    read_data()