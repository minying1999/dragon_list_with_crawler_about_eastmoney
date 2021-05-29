#coding=utf-8
import crawler_funtion as pf
import pandas as pd
import time
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from selenium import  webdriver #从selenium库中调用webdriver模块
from selenium.webdriver.chrome.options import Options # 从options模块中调用Options类

chrome_options = Options()  # 实例化Option对象
chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式




def get_dragon_list():
	driver = webdriver.Chrome()
	#driver = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
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
	return urls_for_base, urls_for_name


def compare_len(urls_for_base,urls_for_name):
	if len(urls_for_base)==len(urls_for_name):
		print("共计%d个,预计耗时5分钟"%len(urls_for_base))
	else:
		print("获取的股票地址和名字数量不匹配")
		#检查获取的两个列表是否匹配
def get_every_stock(urls_for_base,urls_for_name):
	data=pd.DataFrame(columns=['股票名称','营业部','买/卖','榜位','金额'])
	for i in range(len(urls_for_base)):
		try:
			df=pf.get_detailed_info(urls_for_base[i],urls_for_name[i])

		except:
			print("获取个股龙虎数据出错！ "+str(urls_for_name[i])+str(urls_for_base[i]))
		else:
			data=data.append(df,ignore_index=True)
			print("已经完成%d个"%(i+1))
		if i!=0 and i%30==0:
			print("喝杯茶，休息一下，已保留备份")
			time.sleep(5)
			#每30个休息十秒钟,备份一次
			today=time.strftime("%Y-%m-%d")
			today="basic_data"+today+".csv"
			data.to_csv(today,encoding="utf_8_sig",)
	return data
def output_data(data):
	today=time.strftime("%Y-%m-%d")
	today="basic_data"+today+".csv"
	data.to_csv(today,encoding="utf_8_sig",)

def sort_the_info():
	today=time.strftime("%Y-%m-%d")
	today="basic_data"+today+".csv"
	data=pd.read_csv(today,index_col=0)
	final=pd.DataFrame(columns=['游资名称','上榜次数','买榜一次数','卖榜一次数','其他','股票名称','营业部','买/卖','榜位','金额'])
	hot_money={'赵老哥':['中国银河证券绍兴','中国银河证券浙江分公司','湘财证券上海陆家嘴','华泰证券浙江分公司','浙商证券绍兴分公司','浙商证券绍兴解放北路','中国银河证券北京阜成路','中国银河证券北京阜成门','华鑫证券西安科技路','银泰证券上海嘉善路',],
			'章盟主':['国泰君安宁波彩虹北路','国泰君安上海福山路','海通证券上海建国西路','东吴证券杭州文晖路','中泰证券上海建国中路','国泰君安上海江苏路','中信证券杭州四季路','方正证券杭州延安路'],
			'作手新一':['国泰君安南京太平南路'],
			'欢乐海岸':['中信证券深圳总部','中信证券深圳后海','国金证券深圳海南大道','中金公司云浮新兴东堤北路','广发证券深圳民田路','华泰证券深圳分公司','中天证券深圳民田路','中泰证券深圳欢乐海岸','华泰证券深圳益田路荣超商务中心','华泰证券深圳海德三道',],
			'炒股养家':['华鑫证券上海宛平南路','华鑫证券上海红宝石路','华鑫证券南昌红谷中大道','华鑫证券上海淞滨路','华鑫证券上海茅台路','华鑫证券宁波沧海路','华鑫证券上海松江路','华鑫证券西安西大街'],
			'著名刺客':['海通证券北京阜外大街','东莞证券北京分公司','','','',],
			'东北猛男':['中信证券上海淮海中路','中信证券上海分公司','广发证券辽阳民主路','','',],
			'方新侠':['兴业证券股份有限公司陕西分公司'],
			'职业抄手': ['国泰君安成都北一环路', '华泰成都南一环路第二证券营业部', '国信证券成都二环路证券营业部','','',],
			'一花一残忆': ['华泰证券上海普陀区江宁路', '华泰证券上海武定路', '华泰证券无锡解放西路','','',],
			'徐晓': ['国元证券上海虹桥路'],
			'流沙河':['招商证券北京车公庄西路','中信证券北京远大路','','',]
			}
	for key,value in hot_money.items():#遍历游资营业部，排序
		hm_df,total,buy,sell,other=pf.get_hot_money(data,value)
		final=final.append({'游资名称':key,'上榜次数':total,'买榜一次数':buy,'卖榜一次数':sell,'其他':other},ignore_index=True)
		final=final.append(hm_df,ignore_index=True)

	data_hx,total,buy,sell,other=pf.get_huaxin(data)
	final=final.append({'游资名称':"万和证券",'上榜次数':total,'买榜一次数':buy,'卖榜一次数':sell,'其他':other},ignore_index=True)
	final=final.append(data_hx,ignore_index=True)
	#对万和数据排序

	#以下进行输出
	today=time.strftime("%Y-%m-%d")
	result=today+".xls"

	del final['index']
	final.to_excel(result,sheet_name="dragon list",columns=['游资名称','上榜次数','买榜一次数','卖榜一次数','其他','股票名称','营业部','买/卖','榜位','金额'],encoding='utf_8_sig',index=False)
	print("排序已完成，生成以日期命名的文件")
	print('---------------------------------------------------')

while True:
	key=input("功能选择：\n1.一键完成龙虎榜\n2.获取龙虎榜数据生成csv \n3从本地导入csv文件进行排序\n--------------------\n")
	if key == '1':
		urls_for_base,urls_for_name=get_dragon_list()
		compare_len(urls_for_base,urls_for_name)
		data=get_every_stock(urls_for_base,urls_for_name)
		output_data(data)
		sort_the_info()
		pf.change_excel()
	elif key=='2':
		urls_for_base,urls_for_name=get_dragon_list()
		compare_len(urls_for_base,urls_for_name)
		data=get_every_stock(urls_for_base,urls_for_name)
		output_data(data)
	elif key == '3':
		sort_the_info()
		pf.change_excel()

	else:
		exit()
