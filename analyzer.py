import requests
import json
import operator
import datetime
import time
from skimage import io # 미니맵 처리
#from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib import style
import numpy as np
import pathlib
import smtplib # 메일을 보내기 위한 라이브러리 모듈
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 
import smtplib
import imaplib
import poplib
import email
from email.mime.text import MIMEText
import random
import pandas as pd
#import seaborn as sns
from openpyxl import Workbook
def phase1():
	print('롤 기본 데이터 수집')
	#챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
	#dict_keys(['type', 'format', 'version', 'data'])
	global keytochamp
	keytochamp={}
	whole_champions=requests.get("http://ddragon.leagueoflegends.com/cdn/11.3.1/data/ko_KR/champion.json").json()
	for champ in list(whole_champions['data'].keys()):
		keytochamp[whole_champions['data'][champ]['key']]=whole_champions['data'][champ]['name']

	#시즌정보 / [{}]
	season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()

	#큐타입정보[{}]
	#{'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
	queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()

	###################여기까지기본정보받아오는곳

def write_json(filename,data):
	with open(str(filename)+'.json','w',encoding='UTF-8-sig') as file:
		file.write(json.dumps(data,ensure_ascii=False))
def load_json(filename):
	file = pathlib.Path(str(filename)+'.json')
	file_text = file.read_text(encoding='utf-8-sig')
	return json.loads(file_text)

def remove_joong_bok():
	danil = load_json('danil')
	del_liset = []
	for i in danil:
		champs = list(i.values())
		set_champs = set(champs)

		if len(champs)!=len(set_champs):
			del_liset.append(i)

	for i in del_liset:
		danil.remove(i)

	write_json('danil',danil)

def danilwha():
	dan_il = []
	for i in data:
		if i['winteam']=='red':
			i['team_red']['win']=1
			dan_il.append(i['team_red'])

			i['team_blue']['win']=0
			dan_il.append(i['team_blue'])
		else:
			i['team_red']['win']=0
			dan_il.append(i['team_red'])

			i['team_blue']['win']=1
			dan_il.append(i['team_blue'])
	write_json('danil',dan_il)

#phase1()
#champs = list(keytochamp.values())



def make_table():
	new_before = load_json('new_before')

	table = {}
	for data in new_before:
		if data['winteam'] =='red':
			win_team = 'team_red'
			lose_team = 'team_blue'
		elif data['winteam'] == 'blue':
			win_team = 'team_blue'
			lose_team = 'team_red'



		#이긴팀 테이블에 반영
		win_champ = str(data[win_team]['adc'])+'+'+str(data[win_team]['sup'])
		lose_champ = str(data[lose_team]['adc'])+'+'+str(data[lose_team]['sup'])

		if win_champ not in table.keys():
			table[win_champ]={}

		if lose_champ not in table[win_champ].keys():
			table[win_champ][lose_champ]=['100%',1,1,0]
		
		else:
			table[win_champ][lose_champ][1]+=1
			table[win_champ][lose_champ][2]+=1
			table[win_champ][lose_champ][0]=str(round((table[win_champ][lose_champ][2]/table[win_champ][lose_champ][1]*100),2))+"%"
		if '총합' in table[win_champ].keys():
			table[win_champ]['총합'][1]+=1
			table[win_champ]['총합'][2]+=1
			table[win_champ]['총합'][0]=str(round((table[win_champ]['총합'][2]/table[win_champ]['총합'][1]*100),2))+"%"
		else:
			table[win_champ]['총합']=['100%',1,1,0]
		


		#####lose,win champ 바꿔서 진쪽팀 반영
	#	lose_champ = (data[win_team]['adc'],data[win_team]['sup'])
	#	win_champ = (data[lose_team]['adc'],data[lose_team]['sup'])
		lose_champ = str(data[win_team]['adc'])+'+'+str(data[win_team]['sup'])
		win_champ = str(data[lose_team]['adc'])+'+'+str(data[lose_team]['sup'])

		if win_champ not in table.keys():
			table[win_champ]={}

		if lose_champ not in table[win_champ].keys():
			table[win_champ][lose_champ]=['0%',1,0,1]

		else:
			table[win_champ][lose_champ][1]+=1
			table[win_champ][lose_champ][3]+=1
			table[win_champ][lose_champ][0]=str(round((table[win_champ][lose_champ][2]/table[win_champ][lose_champ][1]*100),2))+"%"
		if '총합' in table[win_champ].keys():
			table[win_champ]['총합'][1]+=1
			table[win_champ]['총합'][3]+=1
			table[win_champ]['총합'][0]=str(round((table[win_champ]['총합'][2]/table[win_champ]['총합'][1]*100),2))+"%"
		else:
			table[win_champ]['총합']=['0%',1,0,1]
	for i in table.keys():
		temp = table[i]['총합']
		del(table[i]['총합'])
		table[i]['총합']=temp

	write_json('table',table)


#봇조합별 상성승률 table.json 생성
#인자는 포지션a, 포지션b
def make_table_choose_posi(posa,posb):
	new_before = load_json('new_before')

	table = {}
	for data in new_before:
		if data['winteam'] =='red':
			win_team = 'team_red'
			lose_team = 'team_blue'
		elif data['winteam'] == 'blue':
			win_team = 'team_blue'
			lose_team = 'team_red'



		#이긴팀 테이블에 반영
		win_champ = str(data[win_team][posa])+'+'+str(data[win_team][posb])
		lose_champ = str(data[lose_team][posa])+'+'+str(data[lose_team][posb])

		if win_champ not in table.keys():
			table[win_champ]={}

		if lose_champ not in table[win_champ].keys():
			table[win_champ][lose_champ]=['100%',1,1,0]
		
		else:
			table[win_champ][lose_champ][1]+=1
			table[win_champ][lose_champ][2]+=1
			table[win_champ][lose_champ][0]=str(round((table[win_champ][lose_champ][2]/table[win_champ][lose_champ][1]*100),2))+"%"
		if '총합' in table[win_champ].keys():
			table[win_champ]['총합'][1]+=1
			table[win_champ]['총합'][2]+=1
			table[win_champ]['총합'][0]=str(round((table[win_champ]['총합'][2]/table[win_champ]['총합'][1]*100),2))+"%"
		else:
			table[win_champ]['총합']=['100%',1,1,0]
		


		#####lose,win champ 바꿔서 진쪽팀 반영
	#	lose_champ = (data[win_team]['adc'],data[win_team]['sup'])
	#	win_champ = (data[lose_team]['adc'],data[lose_team]['sup'])
		lose_champ = str(data[win_team][posa])+'+'+str(data[win_team][posb])
		win_champ = str(data[lose_team][posa])+'+'+str(data[lose_team][posb])

		if win_champ not in table.keys():
			table[win_champ]={}

		if lose_champ not in table[win_champ].keys():
			table[win_champ][lose_champ]=['0%',1,0,1]

		else:
			table[win_champ][lose_champ][1]+=1
			table[win_champ][lose_champ][3]+=1
			table[win_champ][lose_champ][0]=str(round((table[win_champ][lose_champ][2]/table[win_champ][lose_champ][1]*100),2))+"%"
		if '총합' in table[win_champ].keys():
			table[win_champ]['총합'][1]+=1
			table[win_champ]['총합'][3]+=1
			table[win_champ]['총합'][0]=str(round((table[win_champ]['총합'][2]/table[win_champ]['총합'][1]*100),2))+"%"
		else:
			table[win_champ]['총합']=['0%',1,0,1]
	for i in table.keys():
		temp = table[i]['총합']
		del(table[i]['총합'])
		table[i]['총합']=temp

	write_json('table',table)





#딕셔너리정렬
def dicsort(dict):
	sdict= sorted(dict.items(), key=operator.itemgetter(1))
	return sdict







#시각화 할때 중요한부분
#조합 총합 n판 이상인거 출력
def print_table(n):
	table = load_json("table")
	newdict = {}
	for i in table.keys():
		if table[i]['총합'][1]>=n:
			newdict[i]= table[i]['총합']
	result = dicsort(newdict)
	result.reverse()
	return result


#이부분으로 시각화하자
#[(조합,[승률,몇전,몇승,몇패]), ....]
'''
pr_list = print_table(30)

for i in pr_list:
	print(i)
'''




'''
###여기부터 그래프 그리는 부분인데 망함
#pr_lsit =[(조합,[승률,몇전,몇승,몇패]), ....]
def make_horizon(pr_list):
	font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
	rc('font', family=font_name)
	style.use('ggplot')

	combis = []
	winrate = []
	for i in pr_list:
		combis.append(i[0])
		winrate.append(float(i[1][0][:-1]))


	industry = combis
	fluctuations = winrate

	fig = plt.figure(figsize=(12, 8))
	ax = fig.add_subplot(111)

	ypos = np.arange(len(combis))
	rects = plt.barh(ypos, fluctuations, align='center', height=0.5)
	plt.yticks(ypos, industry)

	for i, rect in enumerate(rects):
	    ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(fluctuations[i]) + '%', ha='right', va='center')

	plt.xlabel('승률')
	plt.show()
pr_list = print_table(300)

#pr_lsit =[(조합,[승률,몇전,몇승,몇패]), ....]
def make_vertical(pr_list):
	font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
	rc('font', family=font_name)
	style.use('ggplot')

	combis = []
	winrate = []
	for i in pr_list:
		combis.append(i[0])
		winrate.append(float(i[1][0][:-1]))


	industry = combis
	fluctuations = winrate

	fig = plt.figure(figsize=(12, 8))
	ax = fig.add_subplot(111)

	pos = np.arange(len(combis))
	rects = plt.bar(pos, fluctuations, align='center', width=0.5)
	plt.xticks(pos, industry)

	for i, rect in enumerate(rects):
	    ax.text(rect.get_x() + rect.get_width() / 2.0, 0.95 * rect.get_height(), str(fluctuations[i]) + '%', ha='center')

	plt.xlabel('승률')
	plt.show()
#make_vertical(pr_list)


def make_pie_chart(pr_list):
	font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
	rc('font', family=font_name)
	style.use('ggplot')
	colors = ['yellowgreen', 'red']
	for i in pr_list:
		labels = ['승','패']
		ratio = [float(i[1][0][:-1]),100-float(i[1][0][:-1])]
		explode = (0.0, 0.1)
		plt.title(i[0]+' - '+str(i[1][1])+'전 '+str(i[1][2])+'승 '+str(i[1][3])+'패')
		plt.pie(ratio, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
		plt.show()

def make_pie_chart_two(pr_list):
	font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
	rc('font', family=font_name)
	style.use('ggplot')
	colors = ['yellowgreen', 'red']
	for i in pr_list:
		labels = ['승','패']
		ratio = [float(i[1][0][:-1]),100-float(i[1][0][:-1])]

		explode = (0.0, 0.1)
		plt.title(i[0]+'\n'+str(i[1][1])+'게임 ('+str(i[1][0])+')')
		plt.pie(ratio, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
		plt.show()
		
make_pie_chart_two(pr_list)
###여기까지 그래프 그리는 부분인데 망함
'''
def write_excel(filename,pr_list):
	write_wb = Workbook()
	write_ws = write_wb.create_sheet('생성시트')

	write_ws = write_wb.active
	write_ws.append(['조합','등장','승률'])
	for i in pr_list:
		temp = [i[0],i[1][1],float(i[1][0][:-1])]
		write_ws.append(temp)
	write_wb.save(str(filename)+'.xlsx')

#write_excel('test',pr_list)



#champ가 미포일때 , 미스포츈이 포함된 모든 조합 vs 모든 서폿과의 전적 엑셀화 저장
def sup_take(champ,excel_name):
	p = load_json('table')
	pkey = list(p.keys())

	final_dict = {}
	for i in pkey:
		#미포가 들어있는 조합이라면
		if i[:5]==str(champ):
			#테이블에서 꺼내서 상대전적 모으자
			pikey = list(p[i].keys())

			for key in pikey:
				rekey=key
				if '총합' not in key:
					key=key.split('+')[1]
				if key not in list(final_dict.keys()):
					final_dict[key]=p[i][rekey]
				else:
					final_dict[key][1]+=p[i][rekey][1]
					final_dict[key][2]+=p[i][rekey][2]
					final_dict[key][3]+=p[i][rekey][3]
					final_dict[key][0]=str(round(final_dict[key][2]/final_dict[key][1]*100,2))+"%"
	final_dict =dicsort(final_dict)
	write_excel(str(excel_name),final_dict)



#champ가 미포일때 , 미스포츈이 포함된 모든 조합 vs 모든 원딜과의 전적 엑셀화 저장
def adc_take(champ,excel_name):
	p = load_json('table')
	pkey = list(p.keys())

	final_dict = {}
	for i in pkey:
		#미포가 들어있는 조합이라면
		if i[:5]==str(champ):
			#테이블에서 꺼내서 상대전적 모으자
			pikey = list(p[i].keys())

			for key in pikey:
				rekey=key
				if '총합' not in key:
					key=key.split('+')[0]
				if key not in list(final_dict.keys()):
					final_dict[key]=p[i][rekey]
				else:
					final_dict[key][1]+=p[i][rekey][1]
					final_dict[key][2]+=p[i][rekey][2]
					final_dict[key][3]+=p[i][rekey][3]
					final_dict[key][0]=str(round(final_dict[key][2]/final_dict[key][1]*100,2))+"%"
	final_dict =dicsort(final_dict)

	for i in final_dict:
		print(i)
	return
	write_excel(str(excel_name),final_dict)

#champ가 미포일때 , 미스포츈이 포함된 모든 조합 vs 모든 다른 조합과의 전적 엑셀화 저장
def comb_take(champ,excel_name):
	p = load_json('table')
	pkey = list(p.keys())

	final_dict = {}
	for i in pkey:
		#미포가 들어있는 조합이라면
		if i[:5]==str(champ):
			#테이블에서 꺼내서 상대전적 모으자
			pikey = list(p[i].keys())

			for key in pikey:
				rekey=key
				if '총합' not in key:
					key=key.split('+')[1]
				key =rekey
				if key not in list(final_dict.keys()):
					final_dict[key]=p[i][rekey]
				else:
					final_dict[key][1]+=p[i][rekey][1]
					final_dict[key][2]+=p[i][rekey][2]
					final_dict[key][3]+=p[i][rekey][3]
					final_dict[key][0]=str(round(final_dict[key][2]/final_dict[key][1]*100,2))+"%"
	final_dict =dicsort(final_dict)


	write_excel(str(excel_name),final_dict)

def summary(n,m):
	make_table()
	#sup_take('미스 포츈','gaet_sup')

	print(str(n)+'판 이상 등장한 조합의 승률')
	for i in print_table(300):
		print(i)


	print('\n\n')
	print("조합별 상성("+str(m)+"판 이상 등장)")
	table = load_json('table')
	for key in table.keys():
		on=0
		for val in table[key].keys():
			if table[key][val][1]>=m and val!='총합':
				if on==0:
					print(key)
					on=1
				
				print('\t',val,table[key][val])

summary(100,15)