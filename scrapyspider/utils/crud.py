import pymysql
import requests

config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "db": "test",
    "charset": "utf8",
}

# config = {
#     "host": "10.9.157.245",
#     "port": 3306,
#     "user": "root",
#     "password": "ldaI00Uivwp",
#     "db": "test",
#     "charset": "utf8"
# }


def insert(values):
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        sql = "replace into ips values(%s,%s)"
        cur.execute(sql, values)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


def delete(ip):
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        sql = "delete from ips where ip=%s"
        cur.execute(sql, ip)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


def check(ip, port):
    url = "http://www.fang.com/SoufunFamily.htm"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1"}
    proxies = {"http": "http://%s:%s" % (ip, port)}
    print(proxies["http"])
    try:
        response = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=1)
        code = response.status_code
        if code == 200:
            print("该ip可用！")
            return True
        else:
            return False
    except Exception as e:
        print(e)


def random():
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        sql = "select ip,port from ips order by rand() limit 1;"
        cur.execute(sql)
        for each in cur.fetchall():
            ip = each[0]
            port = each[1]
            boolean = check(ip, port)
            if boolean:
                return "http://%s:%s" % (ip, port)
            else:
                delete(ip)
                return random()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    random()