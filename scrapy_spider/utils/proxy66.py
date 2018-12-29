import requests
from lxml import etree
from scrapyspider.utils.crud import insert
from scrapyspider.utils.crud import check


def crawl01():
    # 该站点1小时刷新一次(好)
    for i in range(1, 35):
        url = "http://www.66ip.cn/areaindex_" + str(i) + "/1.html"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        ips = html.xpath('//div[@align="center"]//tr')
        for each in ips[1:]:
            ip = each.xpath('./td[1]')[0].text
            port = each.xpath('./td[2]')[0].text
            boolean = check(ip, port)
            if boolean:
                insert((ip, port))


def crawl02():
    # 该站点2小时刷新一次(差)
    values = []
    for i in range(1, 10):
        url = "http://www.66ip.cn/" + str(i) + ".html"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        ips = html.xpath('//table[@width]//tr')
        for each in ips[1:]:
            ip = each.xpath('./td[1]')[0].text
            port = each.xpath('./td[2]')[0].text
            boolean = check(ip, port)
            if boolean:
                values.append((ip, port))
    insert(values)


if __name__ == "__main__":
    crawl01()
    # crawl02()