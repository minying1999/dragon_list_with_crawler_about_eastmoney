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
from selenium import  webdriver #��selenium���е���webdriverģ��
from selenium.webdriver.chrome.options import Options # ��optionsģ���е���Options��

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
#�����޸�dataframe��ʽ
chrome_options = Options()  # ʵ����Option����
chrome_options.add_argument('--headless')  # ��Chrome���������Ϊ��Ĭģʽ



def get_detailed_info(aim_url, aim_name):

    #����url�����֣����һ��DF
    institutes = []
    amounts = []
    #ÿ���������Ʊ��url
    driver = webdriver.Chrome(options=chrome_options)  # ��������ΪChrome���ں�̨ĬĬ����
    driver.get(
    aim_url)
    time.sleep(3)
    # ���·��������Դ���ҳ����ȡ��'��ã�֩������'�������
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, features='lxml')
    #������soup

    try:
        aim_div = soup.find('div', {'class': 'content main-content'})
        rows_for_institutes = aim_div.find_all('div', class_= 'sc-name')
        print(rows_for_institutes)
    except:
        print("������ҳ���ִ��󣬹�Ʊ����", aim_name)
    else:
        if len(rows_for_institutes) < 10:
            print("�����������ݻ�ȡ��Ϊ%d��������10��" % len(rows_for_institutes))
        for row in rows_for_institutes:
            institute = row.find_all('a')
            print("������������������������������������")
            print(type(institute))
            print(institute[0])
            print(institute)
            print("������������������������������������")
            institutes.append(institute[0].get_text())
#������������ĸ����Ӫҵ��һ��ʮ��������institutes�б���
        try:
            trs = aim_div.find_all('tr')
        except:
            print("���������ִ��󣬹�Ʊ����", aim_name)
        else:
            for tr in trs[2:7]:
                tds = tr.find_all('td')
                amounts.append(tds[2].get_text())
            for tr in trs[9:14]:
                tds = tr.find_all('td')
                amounts.append(tds[4].get_text())
#���ˣ��������Ҳ����һ���б��У�����10����������Ӫҵ��ƥ��
    mid = []
    for ist in institutes[:]:
        ist = ist.replace("�ɷ����޹�˾", "")
        ist = ist.replace("�������ι�˾", "")
        ist = ist.replace("��̩����֤ȯ", "��̩����")
        ist = ist.replace("���޹�˾", "")
        ist = ist.replace("֤ȯӪҵ��", "")
        mid.append(ist)
    test_dict = {
        "��Ʊ����": [aim_name] * 10,
        'Ӫҵ��': mid,
        "��/��": ['��', '��', '��', '��', '��', '��', '��', '��', '��', '��'],
        "��λ": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        '���': amounts
    }
    print(amounts,mid)
    df = pd.DataFrame(test_dict)
    time.sleep(2)
    return df


#����ɸѡ������͵Ĺ�Ʊ
#����ɸѡ������͵Ĺ�Ʊ
def get_huaxin(data):
	for idx,row in enumerate(data['Ӫҵ��']):
		if row.find("���") <0:
			data.drop([idx],inplace=True)
		else:
			pass
			data.loc[idx,'Ӫҵ��']=row.replace("���֤ȯ","")
	total=data.shape[0]
	buy=0
	sell=0
	data=data.reset_index()
	for i in range(total):
		if data.loc[i,'��λ']==1 and data.loc[i,'��/��']=='��':
			buy += 1
		if data.loc[i,'��λ']==1 and data.loc[i,'��/��']=='��':
			sell += 1

	other=total-buy-sell
	return data,total,buy,sell,other


def get_hot_money(data,hot_money_name):
	
	hm_df=pd.DataFrame(columns=['��Ʊ����','Ӫҵ��','��/��','��λ','���'])
	for idx,row in enumerate(data['Ӫҵ��']):
		if row in hot_money_name:
			hm_df=hm_df.append(data[idx:idx+1])
	hm_df=hm_df.reset_index()
	total=hm_df.shape[0]
	buy=0
	sell=0
	for i in range(total):
		if hm_df.loc[i,'��λ']==1 and hm_df.loc[i,'��/��']=='��':
			buy += 1
		if hm_df.loc[i,'��λ']==1 and hm_df.loc[i,'��/��']=='��':
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
#�����ʽ

def change_excel(): #�޸ı���ʽ��������
	today=time.strftime("%Y-%m-%d")
	filename=today + ".xls"
	old_excel=xlrd.open_workbook(filename,formatting_info=True)
	old_sheet=old_excel.sheet_by_index(0)
	new_excel=copy(old_excel)
	new_sheet=new_excel.get_sheet(0)
	new_sheet.write_merge(0,0,0,9,today+'������',set_style('����',320,bold=True,align=True))
	#���ñ���
	max_width=[]
	for j in range(old_sheet.ncols):
		max_width.append(0)
		for i in range(old_sheet.nrows):
			if (len(str(old_sheet.cell_value(i,j)))*580)>max_width[j]:
				max_width[j]=len(str(old_sheet.cell_value(i,j))*580)
			#�õ�ÿһ������п�
	for j in range(old_sheet.ncols): #���ñ�ͷ
		new_sheet.write(1,j,old_sheet.cell_value(0,j),
			set_style('����',220,bold=True,border=True,align=True))
	
	for i in range(1,old_sheet.nrows):
		for j in [0,5,6]:
			new_sheet.write(i+1,j,old_sheet.cell_value(i,j),
					set_style('����',200))
		for j in [1,2,3,4,7,8,9]:
			new_sheet.write(i+1,j,old_sheet.cell_value(i,j),
					set_style('����',200,align=True))

	for j in range(len(max_width)):
		new_sheet.col(j).width=max_width[j]
	new_sheet.col(9).width=2200
	new_excel.save(filename)
	

