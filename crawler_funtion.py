#coding:gbk
import tushare as ts
import pandas as pd
import requests
import re
import time
import xlrd
import xlwt
from xlutils.copy import copy
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import  webdriver #从selenium库中调用webdriver模块
from selenium.webdriver.chrome.options import Options # 从options模块中调用Options类

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
#用来修改dataframe格式
chrome_options = Options()  # 实例化Option对象
chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式



def get_detailed_info(aim_url, aim_name):

    #输入url和名字，输出一个DF
    institutes = []
    amounts = []
    #每个龙虎榜股票的url
    driver = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
    driver.get(
    aim_url)
    time.sleep(3)
    # 以下方法都可以从网页中提取出'你好，蜘蛛侠！'这段文字
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, features='lxml')
    #解析出soup

    try:
        aim_div = soup.find('div', {'class': 'content main-content'})
        rows_for_institutes = aim_div.find_all('div', class_= 'sc-name')
        print(rows_for_institutes)
    except:
        print("解析网页出现错误，股票名：", aim_name)
    else:
        if len(rows_for_institutes) < 10:
            print("个股龙虎数据获取量为%d个，不足10个" % len(rows_for_institutes))
        for row in rows_for_institutes:
            institute = row.find_all('a')
            print("——————————————————")
            print(type(institute))
            print(institute[0])
            print(institute)
            print("——————————————————")
            institutes.append(institute[0].get_text())
#将买入和卖出的各五个营业部一共十个，放在institutes列表中
        try:
            trs = aim_div.find_all('tr')
        except:
            print("解析表格出现错误，股票名：", aim_name)
        else:
            for tr in trs[2:7]:
                tds = tr.find_all('td')
                amounts.append(tds[2].get_text())
            for tr in trs[9:14]:
                tds = tr.find_all('td')
                amounts.append(tds[4].get_text())
#至此，买卖金额也放在一个列表中，共计10个，正好与营业部匹配
    mid = []
    for ist in institutes[:]:
        ist = ist.replace("股份有限公司", "")
        ist = ist.replace("有限责任公司", "")
        ist = ist.replace("国泰君安证券", "国泰君安")
        ist = ist.replace("有限公司", "")
        ist = ist.replace("证券营业部", "")
        mid.append(ist)
    test_dict = {
        "股票名称": [aim_name] * 10,
        '营业部': mid,
        "买/卖": ['买', '买', '买', '买', '买', '卖', '卖', '卖', '卖', '卖'],
        "榜位": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        '金额': amounts
    }
    print(amounts,mid)
    df = pd.DataFrame(test_dict)
    time.sleep(2)
    return df


#以下筛选含有万和的股票
#以下筛选含有万和的股票
def get_huaxin(data):
	for idx,row in enumerate(data['营业部']):
		if row.find("万和") <0:
			data.drop([idx],inplace=True)
		else:
			pass
			data.loc[idx,'营业部']=row.replace("万和证券","")
	total=data.shape[0]
	buy=0
	sell=0
	data=data.reset_index()
	for i in range(total):
		if data.loc[i,'榜位']==1 and data.loc[i,'买/卖']=='买':
			buy += 1
		if data.loc[i,'榜位']==1 and data.loc[i,'买/卖']=='卖':
			sell += 1

	other=total-buy-sell
	return data,total,buy,sell,other


def get_hot_money(data,hot_money_name):
	
	hm_df=pd.DataFrame(columns=['股票名称','营业部','买/卖','榜位','金额'])
	for idx,row in enumerate(data['营业部']):
		if row in hot_money_name:
			hm_df=hm_df.append(data[idx:idx+1])
	hm_df=hm_df.reset_index()
	total=hm_df.shape[0]
	buy=0
	sell=0
	for i in range(total):
		if hm_df.loc[i,'榜位']==1 and hm_df.loc[i,'买/卖']=='买':
			buy += 1
		if hm_df.loc[i,'榜位']==1 and hm_df.loc[i,'买/卖']=='卖':
			sell += 1
	other=total-buy-sell
	return hm_df,total,buy,sell,other

	
def set_style(name,height,bold=False,border=False,align=False):
	style=xlwt.XFStyle()
	font=xlwt.Font()
	font.name=name
	font.height=height
	font.bold=bold
	style.font=font
	if border:
		borders=xlwt.Borders()
		borders.top=xlwt.Borders.THIN
		borders.bottom=xlwt.Borders.THIN
		borders.left=xlwt.Borders.THIN
		borders.right=xlwt.Borders.THIN
		style.borders=borders
	if align:
		alignment=xlwt.Alignment()
		alignment.horz=xlwt.Alignment.HORZ_CENTER
		style.alignment=alignment
	return style
#定义格式

def change_excel(): #修改表格格式的主函数
	today=time.strftime("%Y-%m-%d")
	filename=today + ".xls"
	old_excel=xlrd.open_workbook(filename,formatting_info=True)
	old_sheet=old_excel.sheet_by_index(0)
	new_excel=copy(old_excel)
	new_sheet=new_excel.get_sheet(0)
	new_sheet.write_merge(0,0,0,9,today+'龙虎榜',set_style('宋体',320,bold=True,align=True))
	#设置标题
	max_width=[]
	for j in range(old_sheet.ncols):
		max_width.append(0)
		for i in range(old_sheet.nrows):
			if (len(str(old_sheet.cell_value(i,j)))*580)>max_width[j]:
				max_width[j]=len(str(old_sheet.cell_value(i,j))*580)
			#得到每一列最大列宽
	for j in range(old_sheet.ncols): #设置表头
		new_sheet.write(1,j,old_sheet.cell_value(0,j),
			set_style('宋体',220,bold=True,border=True,align=True))
	
	for i in range(1,old_sheet.nrows):
		for j in [0,5,6]:
			new_sheet.write(i+1,j,old_sheet.cell_value(i,j),
					set_style('宋体',200))
		for j in [1,2,3,4,7,8,9]:
			new_sheet.write(i+1,j,old_sheet.cell_value(i,j),
					set_style('宋体',200,align=True))

	for j in range(len(max_width)):
		new_sheet.col(j).width=max_width[j]
	new_sheet.col(9).width=2200
	new_excel.save(filename)
	

