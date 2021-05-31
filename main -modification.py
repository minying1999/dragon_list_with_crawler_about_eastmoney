#!/usr/bin/env python
# coding: utf-8

import pachong_funtion as pf
import pandas as pd
import time
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from selenium import webdriver  # 从selenium库中调用webdriver模块
from selenium.webdriver.chrome.options import Options  # 从options模块中调用Options类

chrome_options = Options()  # 实例化Option对象
chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式


# <font color=red size= 6 face=雅黑>使用selenium改编</font>

# In[ ]:


def get_dragon_list():
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(
        'http://data.eastmoney.com/stock/lhb.html')
    time.sleep(5)
    # 以下方法都可以从网页中提取出'你好，蜘蛛侠！'这段文字
    html = driver.page_source
    driver.close()
    # print(type(html))
    # print(html)
    base = "http://data.eastmoney.com"
    soup = BeautifulSoup(html, features='lxml')
    # print(soup)
    stock_urls = soup.find_all('span', {'class': "wname"})
    urls_for_base = []
    urls_for_name = []
    for t in stock_urls:
        urls = t.find('a')
        current = base + urls['href']
        urls_for_base.append(current)
        urls_for_name.append(urls['title'])
    print(urls_for_base)
    print(urls_for_name)
    # return urls_for_base[1:10], urls_for_name[1:10]
    return urls_for_base, urls_for_name


# return urls_for_base[1:13], urls_for_name[1:13]


# In[ ]:


# get_dragon_list()


# In[ ]:


def repalce_str(str):
    str2 = str1.replace("股份有限公司", "")
    str3 = str2.replace("有限责任公司", "")
    str4 = str3.replace("国泰君安证券", "国泰君安")
    str5 = str4.replace("有限公司", "")
    str = str5.replace("证券营业部", "")
    return str


# In[ ]:


def compare_len(urls_for_base, urls_for_name):
    if len(urls_for_base) == len(urls_for_name):
        print("共计{}个,预计耗时{}分钟".format(len(urls_for_base), len(urls_for_base) * 0.25))
    else:
        print("获取的股票地址和名字数量不匹配")
    # 检查获取的两个列表是否匹配


# In[ ]:


def get_every_stock(urls_for_base, urls_for_name):
    count = 0
    data = pd.DataFrame(columns=['股票名称', '营业部', '买/卖', '榜位', '金额'])
    wrong_list = []
    for i in range(len(urls_for_base)):
        count += 1
        print('当前正在尝试获取{}的股票信息'.format(urls_for_name[i]))
        print('当前进度为{:.3%}'.format(count / len(urls_for_base)))
        try:
            df = pf.get_detailed_info(urls_for_base[i], urls_for_name[i])

        except:
            print("获取个股龙虎数据出错！ " + str(urls_for_name[i]) +
                  str(urls_for_base[i]))
            wrong_list.append(str(urls_for_name[i]))
            print("无法成功获取的股票有")
            print(wrong_list)
        else:
            data = data.append(df, ignore_index=True)
            print("已经完成%d个" % (i + 1))
        if i != 0 and i % 30 == 0:
            print("喝杯茶，休息一下，已保留备份")
            time.sleep(5)
            # 每30个休息十秒钟,备份一次
            today = time.strftime("%Y-%m-%d")
            today = "basic_data" + today + ".csv"
            data.to_csv(
                today,
                encoding="utf_8_sig",
            )
        print("——————————————————————————")
    return data


# In[ ]:


def output_data(data):
    today = time.strftime("%Y-%m-%d")
    today = "basic_data" + today + ".csv"
    data.to_csv(
        today,
        encoding="utf_8_sig",
    )


# In[ ]:


def sort_the_info():
    today = time.strftime("%Y-%m-%d")
    today = "basic_data" + today + ".csv"
    data = pd.read_csv(today, index_col=0)
    final = pd.DataFrame(columns=[
        '游资名称', '上榜次数', '买榜一次数', '卖榜一次数', '其他', '股票名称', '营业部', '买/卖', '榜位',
        '金额'
    ])
    hot_money = {
        '赵老哥': [
            '中国银河证券绍兴',
            '浙商证券绍兴分公司',
            '中国银河证券北京阜成路',
            '银泰证券上海嘉善路',
        ],
        '章盟主': ['国泰君安宁波彩虹北路', '海通证券上海建国西路', '国泰君安上海江苏路', '中信证券杭州四季路'],
        '作手新一': ['国泰君安南京太平南路'],
        '欢乐海岸': [
            '中信证券深圳总部',
            '中信证券深圳后海',
            '国金证券深圳海南大道',
            '中金公司云浮新兴东堤北路',
            '广发证券深圳民田路',
            '华泰证券深圳分公司',
            '中天证券深圳民田路',
            '中泰证券深圳欢乐海岸',
            '华泰证券深圳益田路荣超商务中心',
            '华泰证券深圳海德三道',
        ],
        '炒股养家': [
            '华鑫证券上海宛平南路', '华鑫证券上海红宝石路', '华鑫证券南昌红谷中大道', '华鑫证券上海淞滨路',
            '华鑫证券上海茅台路', '华鑫证券宁波沧海路', '华鑫证券上海松江路', '华鑫证券西安西大街'
        ],
        '著名刺客': [
            '海通证券北京阜外大街',
            '东莞证券北京分公司',
            '',
            '',
            '',
        ],
        '东北猛男': [
            '中信证券上海淮海中路',
            '中信证券上海分公司',
            '广发证券辽阳民主路',
            '',
            '',
        ],
        '方新侠': ['兴业证券陕西分公司'],
        '职业抄手': [
            '国泰君安成都北一环路',
            '华泰成都南一环路第二',
            '国信证券成都二环路',
            '',
            '',
        ],
        '一花一残忆': [
            '华泰证券上海普陀区江宁路',
            '华泰证券上海武定路',
            '华泰证券无锡解放西路',
            '',
            '',
        ],
        '徐晓': ['国元证券上海虹桥路'],
        '北京帮': ['光大证券北京东中街', '海通证券北京知春路',
                '中国银河证券北京朝阳门北大街', '广发证券潮州潮枫路'],
        '佛山系': ['光大证券佛山绿景路', '华泰证券广州天河东路',
                '新时代证券佛山南海大道'],
        '流沙河': [
            '招商证券北京车公庄西路',
            '中信证券北京远大路',
            '',
            '',
        ]
    }
    for key, value in hot_money.items():  # 遍历游资营业部，排序
        hm_df, total, buy, sell, other = pf.get_hot_money(data, value)
        final = final.append(
            {
                '游资名称': key,
                '上榜次数': total,
                '买榜一次数': buy,
                '卖榜一次数': sell,
                '其他': other
            },
            ignore_index=True)
        final = final.append(hm_df, ignore_index=True)

    data_hx, total, buy, sell, other = pf.get_huaxin(data)
    final = final.append(
        {
            '游资名称': "万和证券",
            '上榜次数': total,
            '买榜一次数': buy,
            '卖榜一次数': sell,
            '其他': other
        },
        ignore_index=True)
    final = final.append(data_hx, ignore_index=True)
    # 对万和数据排序

    # 以下进行输出
    today = time.strftime("%Y-%m-%d")
    result = today + ".xls"

    del final['index']
    final.to_excel(result,
                   sheet_name="dragon list",
                   columns=[
                       '游资名称', '上榜次数', '买榜一次数', '卖榜一次数', '其他', '股票名称', '营业部',
                       '买/卖', '榜位', '金额'
                   ],
                   encoding='utf_8_sig',
                   index=False)
    print("排序已完成，生成以日期命名的文件")
    print('---------------------------------------------------')


# In[ ]:
#


while True:
    time_initial = time.time()
    key = input(
        "功能选择：\n1.一键完成龙虎榜\n2.获取龙虎榜数据生成csv \n3从本地导入csv文件进行排序\n--------------------\n"
    )
    if key == '1':

        urls_for_base, urls_for_name = get_dragon_list()
        compare_len(urls_for_base, urls_for_name)
        data = get_every_stock(urls_for_base, urls_for_name)
        output_data(data)
        sort_the_info()
        pf.change_excel()
        time_final = time.time()
        print("——————————————————————————————————————")
        print("功能1总共的运行时间是:{:.5}秒".format(-(time_initial - time_final)))
        print('写入完成，路径为当前目录')
    elif key == '2':
        urls_for_base, urls_for_name = get_dragon_list()
        compare_len(urls_for_base, urls_for_name)
        data = get_every_stock(urls_for_base, urls_for_name)
        output_data(data)
    elif key == '3':
        sort_the_info()
        pf.change_excel()

    else:
        break

# In[ ]:




