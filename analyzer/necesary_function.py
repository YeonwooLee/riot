import requests
import json
import operator
import datetime
import time
from skimage import io # 미니맵 처리
from sklearn.preprocessing import MinMaxScaler
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
import seaborn as sns
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




#아래 두개는 자료형 그대로 데이터를 저장, 불러오기 할 수 있는 함수들입니다.
def write_json(filename,data):
	with open(str(filename)+'.json','w',encoding='UTF-8-sig') as file:
		file.write(json.dumps(data,ensure_ascii=False))
def load_json(filename):
	file = pathlib.Path(str(filename)+'.json')
	file_text = file.read_text(encoding='utf-8-sig')
	return json.loads(file_text)




#데이터 수집기에서 수집한 데이터인 new_before.json을 조합간 상대전적표로
#{조합1:{조합2[승률,몇전,몇승,몇패],조합2[승률,몇전,몇승,몇패]}, 조합2:{}} 이런식
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




#총합이 num 이상인 조합의 총 승률 출력
def print_sum(num):
	table = load_json('table')

	for i in list(table.keys()):
		if table[i]['총합'][1]>num:
			print(i,table[i]['총합'])

#아무것도 모를 때 - type - 1
#등장 n번 이상 한 원딜
#밴카드 반영 필요 - 승률 높은 것 픽하면 됨
def t_one():
	table=load_json('table')
	temp_dict = {}
	for comb in table.keys():
		#조합에서 원딜 추출
		adc=comb.split('+')[0]

		if adc in temp_dict.keys():
			temp_dict[adc][1]+=table[comb]['총합'][1]
			temp_dict[adc][2]+=table[comb]['총합'][2]
			temp_dict[adc][3]+=table[comb]['총합'][3]
			temp_dict[adc][0]=str(round(temp_dict[adc][2]/temp_dict[adc][1]*100,2))+"%"
		else:
			temp_dict[adc]=table[comb]['총합']
	result = dicsort(temp_dict)
	result.reverse()
	for i in result:
		if i[1][1]<30:
			continue
		print(i)

#type-2
#e_adc: 상대 원딜 - 승률 낮은 것 픽하면 됨
def t_two(e_adc):
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
		win_champ = str(data[win_team]['adc'])
		lose_champ = str(data[lose_team]['adc'])
		#찾는원딜없으면 다음게임으로
		if win_champ!=e_adc and lose_champ!=e_adc:
			continue

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
		lose_champ = str(data[win_team]['adc'])
		win_champ = str(data[lose_team]['adc'])

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

	#상대원딜의 원딜 상대전적
	enemy = table[e_adc]
	del(enemy['총합'])
	k=dicsort(enemy)
	print("출력된 승률은 둘이 싸웠을 때 "+str(e_adc)+"의 승률입니다")
	for i in k:
		if i[1][1]>100:
			print(i)
	
#type-3 상대 서폿만 알 때 - 승률 낮은 것 픽하면 됨
#e_sup: 상대 서폿
def t_three(e_sup):
	table = load_json('table')
	t_keys = table.keys()

	newdict = {}
	for key in t_keys:
		if e_sup not in key:
			continue
		#서폿이 내가 찾는 서폿이라면
		else:
			for real_key in table[key].keys():
				if real_key.split('+')[0] not in newdict.keys():
					newdict[real_key.split('+')[0]]=table[key][real_key]
				else:
					newdict[real_key.split('+')[0]][1]+=table[key][real_key][1]
					newdict[real_key.split('+')[0]][2]+=table[key][real_key][2]
					newdict[real_key.split('+')[0]][3]+=table[key][real_key][3]
					newdict[real_key.split('+')[0]][0]=str(round((newdict[real_key.split('+')[0]][2]/newdict[real_key.split('+')[0]][1]*100),2))+"%"
	result = dicsort(newdict)
	print("출력된 승률은 둘이 싸웠을 때 "+str(e_sup)+"의 승률입니다")
	for i in result:
		if i[0]=='총합':
			continue
		if i[1][1]>100:
			print(i)



#type-4 상대 서폿, 원딜 알 때 - 승률 낮은 것 픽하면 됨
def t_four(e_adc, e_sup):
	table = load_json('table')
	t_keys = table.keys()

	newdict = {}
	for key in t_keys:
		if e_sup and e_adc not in key:
			continue
		#서폿이 내가 찾는 서폿이라면
		else:
			for real_key in table[key].keys():
				if real_key.split('+')[0] not in newdict.keys():
					newdict[real_key.split('+')[0]]=table[key][real_key]
				else:
					newdict[real_key.split('+')[0]][1]+=table[key][real_key][1]
					newdict[real_key.split('+')[0]][2]+=table[key][real_key][2]
					newdict[real_key.split('+')[0]][3]+=table[key][real_key][3]
					newdict[real_key.split('+')[0]][0]=str(round((newdict[real_key.split('+')[0]][2]/newdict[real_key.split('+')[0]][1]*100),2))+"%"
	result = dicsort(newdict)
	print("출력된 승률은 둘이 싸웠을 때 "+str(e_adc)+str(e_sup)+"의 승률입니다")
	for i in result:
		if i[0]=='총합':
			continue
		if i[1][1]>100:
			print(i)








#내 서폿이 뭔지만 알 때, type - 5
#조합 총합 n판 이상인거 출력, 내 서폿은 my_sup
#밴카드 반영 필요
def t_five(my_sup):
	table = load_json("table")
	newdict = {}
	for i in table.keys():
		test = i.split('+')[1]
		if my_sup not in test:
			continue
		if table[i]['총합'][1]>=100:
			newdict[i]= table[i]['총합']
	result = dicsort(newdict)
	result.reverse()
	print("출력된 승률은 둘이 싸웠을 때 "+str(my_sup)+"의 승률입니다")
	#return result
	for i in result:
		print(i)


#내 서폿,상대원딜이 뭔지만 알 때, type - 6
#조합 총합 n판 이상인거 출력, 내 서폿은 my_sup 
#밴카드 반영 필요
#승률 높은거 픽하면 됨
def t_six(my_sup,e_adc):
	table = load_json("table")
	new_dict = {}
	for i in list(table.keys()):
		if my_sup not in i.split('+')[1]:
			del(table[i])
		else:
			for j in list(table[i].keys()):
				if e_adc not in j:
					del(table[i][j])
	for i in list(table.keys()):
		if len(table[i])==0:
			del(table[i])
		
		else:
			new_dict[i]=[0,0,0,0]
			for j in table[i].keys():
				new_dict[i][1]+=table[i][j][1]
				new_dict[i][2]+=table[i][j][2]
				new_dict[i][3]+=table[i][j][3]
				new_dict[i][0] = str(round(new_dict[i][2]/new_dict[i][1]*100,2))+"%"

	k=dicsort(new_dict)
	k.reverse()
	print("출력된 승률은 둘이 싸웠을 때 "+str(my_sup)+"의 승률입니다")
	for i in k:
		if i[1][1]>1:
			print(i)



#내 서폿이 뭔지만 알 때, type - 7
#조합 총합 n판 이상인거 출력, 내 서폿은 my_sup 
#밴카드 반영 필요
#승률 높은거 픽하면 됨
def t_seven(my_sup,e_sup):
	table = load_json("table")
	e_adc = e_sup
	new_dict = {}
	for i in list(table.keys()):
		if my_sup not in i.split('+')[1]:
			del(table[i])
		else:
			for j in list(table[i].keys()):
				if e_adc not in j:
					del(table[i][j])
	for i in list(table.keys()):
		if len(table[i])==0:
			del(table[i])
		
		else:
			new_dict[i]=[0,0,0,0]
			for j in table[i].keys():
				new_dict[i][1]+=table[i][j][1]
				new_dict[i][2]+=table[i][j][2]
				new_dict[i][3]+=table[i][j][3]
				new_dict[i][0] = str(round(new_dict[i][2]/new_dict[i][1]*100,2))+"%"

	k=dicsort(new_dict)
	k.reverse()
	print("출력된 승률은 둘이 싸웠을 때 "+str(my_sup)+"의 승률입니다")
	for i in k:
		if i[1][1]>10:
			print(i)

	


#내 서폿이 뭔지만 알 때, type - 8
#조합 총합 n판 이상인거 출력, 내 서폿은 my_sup 
#밴카드 반영 필요
#승률 높은거 픽하면 됨
def t_eight(my_sup,e_sup,e_adc):
	table = load_json("table")
	new_dict = {}
	for i in list(table.keys()):
		if my_sup not in i.split('+')[1]:
			del(table[i])
		else:
			for j in list(table[i].keys()):
				if e_adc not in j or e_sup not in j:
					del(table[i][j])
	for i in list(table.keys()):
		if len(table[i])==0:
			del(table[i])
		
		else:
			new_dict[i]=[0,0,0,0]
			for j in table[i].keys():
				new_dict[i][1]+=table[i][j][1]
				new_dict[i][2]+=table[i][j][2]
				new_dict[i][3]+=table[i][j][3]
				new_dict[i][0] = str(round(new_dict[i][2]/new_dict[i][1]*100,2))+"%"

	k=dicsort(new_dict)
	k.reverse()
	print("출력된 승률은 둘이 싸웠을 때 "+str(my_sup)+"의 승률입니다")
	for i in k:
		if i[1][1]>3:
			print(i)


phase1()
#table 촤신화
make_table()
#현재 상황에 가장 승률이 높은 픽 고를 수 있음
while True:
	print("종료하고싶으면 '**'을 입력해주세요")
	my_sup = input('아군 서폿(모르면 \'ㄴㄴ\'입력):')
	if my_sup=="**":
		break
	if my_sup not in keytochamp.values() and my_sup!='ㄴㄴ':
		continue

	e_adc = input('상대 원딜(모르면 \'ㄴㄴ\'입력):')
	if e_adc=="**":
		break
	if e_adc not in keytochamp.values() and e_adc!='ㄴㄴ':
		continue

	e_sup = input('상대 서폿(모르면 \'ㄴㄴ\'입력):')
	if e_sup=="**":
		break
	if e_sup not in keytochamp.values() and e_sup!='ㄴㄴ':
		continue


	if my_sup=='ㄴㄴ' and e_sup=='ㄴㄴ' and e_adc=='ㄴㄴ':
		t_one()

	elif my_sup=='ㄴㄴ' and e_sup=='ㄴㄴ' and e_adc!='ㄴㄴ':
		t_two(e_adc)

	elif my_sup=='ㄴㄴ' and e_sup!='ㄴㄴ' and e_adc=='ㄴㄴ':
		t_three(e_sup)

	elif my_sup=='ㄴㄴ' and e_sup!='ㄴㄴ' and e_adc!='ㄴㄴ':
		t_four(e_adc,e_sup)

	elif my_sup!='ㄴㄴ' and e_sup=='ㄴㄴ' and e_adc=='ㄴㄴ':
		t_five(my_sup)

	elif my_sup!='ㄴㄴ' and e_sup=='ㄴㄴ' and e_adc!='ㄴㄴ':
		t_six(my_sup,e_adc)

	elif my_sup!='ㄴㄴ' and e_sup!='ㄴㄴ' and e_adc=='ㄴㄴ':
		t_seven(my_sup,e_sup)

	elif my_sup!='ㄴㄴ' and e_sup!='ㄴㄴ' and e_adc!='ㄴㄴ':
		t_eight(my_sup,e_sup,e_adc)
