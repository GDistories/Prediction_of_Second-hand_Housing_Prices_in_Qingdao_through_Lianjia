import requests
import time
from lxml import etree
import pandas as pd

# 设置列表页URL的固定部分
url = 'http://qd.lianjia.com'

# 设置页面页的可变部分
# 设置请求头部信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
area = []  ##地区
totalprice = []  ##房价
houseinfo = []  ##房源信息
followinfo = []  # 关注度
monovalent = []  # 单价
featureinfo = []  # 特色，优势
transactioninfo = []  # 交易属性
basicinfo = []  # 基本属性
# 循环抓取列表页信息
# 获取地区
durl = url + '/ershoufang'
dr = requests.get(url=durl, headers=headers)
dhtml = dr.content
dencoding = requests.get(durl, headers=headers).encoding
dlj = etree.HTML(dhtml, parser=etree.HTMLParser(encoding=dencoding))
dq = dlj.xpath('//div[@class="position"]/dl[2]/dd/div[1]/div/a/@href')

print(dq)
for d in dq:
    count_for_current_area = 0
    yurl = url + d
    yr = requests.get(url=yurl, headers=headers)
    yhtml = yr.content
    yencoding = requests.get(yurl, headers=headers).encoding
    ylj = etree.HTML(yhtml, parser=etree.HTMLParser(encoding=yencoding))
    page_data_results = ylj.xpath("//div[@class='contentBottom clear']/div[@class='page-box fr']//@page-data")
    if page_data_results:
        ysl = eval(page_data_results[0])
        ys = ysl['totalPage']
    else:
        print("该区域无二手房")
        continue

    for i in range(1, ys + 1):
        try:
            i = str(i)
            a = url + d + 'pg' + i + '/'
            r = requests.get(url=a, headers=headers)
            zhtml = r.content
            print('爬取的区域：', d)
            # 每次间隔1秒
            time.sleep(1)
            zencoding = requests.get(url, headers=headers).encoding
            lj = etree.HTML(zhtml, parser=etree.HTMLParser(encoding=zencoding))

            # 提取房源总价
            price = lj.xpath('//div[@class="priceInfo"]')
            for a in price:
                totalPrice = a.xpath('.//span/text()')[0]
                totalprice.append(totalPrice)

            # 提取房源每平单价
            danjia = lj.xpath('//div[@class="unitPrice"]')
            for a in danjia:
                unitprice = a.xpath('.//span/text()')[0]
                monovalent.append(unitprice)

            # 提取房源信息
            houseInfo = lj.xpath('//div[@class="info clear"]')
            for b in houseInfo:
                f = b.xpath('.//div[@class="tag"]')
                for fy in f:
                    feature = fy.xpath('.//span/text()')
                    featureinfo.append(feature)
                house = b.xpath('.//div[@class="positionInfo"]//a/text()')[0] + '|' + \
                        b.xpath('.//div[@class="positionInfo"]//a[2]/text()')[0] + '|' + \
                        b.xpath('.//div[@class="houseInfo"]//text()')[0]
                houseinfo.append(house)

            # 提取基本属性和交易属性
            murl = lj.xpath('//div[@class="info clear"]//div[@class="title"]/a/@href')
            for h in murl:
                mr = requests.get(url=h, headers=headers)
                mhtml = mr.content
                time.sleep(1)
                mencoding = requests.get(h, headers=headers).encoding
                mlj = etree.HTML(mhtml, parser=etree.HTMLParser(encoding=mencoding))
                mh = mlj.xpath('//div[@class="transaction"]//div[@class="content"]//ul//li//span[2]//text()')
                bi = mlj.xpath('//div[@class="base"]//div[@class="content"]//ul//li/text()')
                transactioninfo.append(mh)
                basicinfo.append(bi)
                area.append(d)
                count_for_current_area += 1
                if count_for_current_area % 10 == 0:
                    print(f"当前区域：{d}，该区域已爬取{count_for_current_area}条。")

            # 提取房源关注度
            followInfo = lj.xpath('//div[@class="followInfo"]')
            for c in followInfo:
                follow = c.xpath('./text()')[0]
                followinfo.append(follow)
        except Exception as e:
            print(f"Error on page {i} for area {d}: {str(e)}")
    print(f"当前区域：{d}爬取结束，该区域一共爬取{count_for_current_area}条。")

# 写入数据表
house = pd.DataFrame({
    'area': area,
    'houseinfo': houseinfo,
    'followinfo': followinfo,
    'totalprice': totalprice,
    'monovalent': monovalent,
    'featureinfo': featureinfo,
    'basicinfo': basicinfo,
    'transactioninfo': transactioninfo
})
house.to_csv("tst1.csv", mode='a', header=False, encoding='utf-8', index=False)