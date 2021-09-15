#cl_collector
import requests
import json
import operator
import datetime
import time
from skimage import io # 미니맵 처리
#from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
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
import telegram



class LolCollector:
	def __init__(self,year,month,day):
		print("init 메소드 구동")
		self.year = year
		self.month = month
		self.day = day
		self.code=str(year)+"-"+str(month)+"-"+str(day)+"_"
		self.api_key = self.getKey()
		self.quit_sign =0
		self.epochmillisecond=self.date_to_millisecond(self.year,self.month,self.day)


	#날짜 -> 에포크밀리초 (시간은 롤 패치 종료시간인 오전10시 고정해둠)
	def date_to_millisecond(self,year,month,day):
		'''
		dt_obj = datetime.strptime('25.8.2021 22:00:00,00',
		                           '%d.%m.%Y %H:%M:%S,%f')
		                         '''

		dt_obj = datetime.datetime.strptime("{}.{}.{} 10:00:00,00".format(day,month,year),'%d.%m.%Y %H:%M:%S,%f')
		millisec = dt_obj.timestamp() * 1000

		return int(millisec)
	#수집한 데이터를 제 이메일로 백업합니다. 자료수집용 컴퓨터의 key가 만료된다면 저에게 이메일을 보내 key가 만료되었음을 알립니다.
	#자료수집용 컴퓨터가 메일을 보내면 다시 제 메일로 새 api-key를 보내주고 get_key_from_mail이 그 메일을 읽어 key를 교체하는 방식입니다
	#https://wikidocs.net/36465
	def send_final(self):
		sendEmail = "jyanoos1993@gmail.com"
		recvEmail = "fox_93@naver.com"
		password = "ytttqzpiakaturft"

		smtpName = "smtp.gmail.com"
		smtpPort = 587

		#여러 MIME을 넣기위한 MIMEMultipart 객체 생성
		msg = MIMEMultipart()

		msg['Subject'] ="롤 본컴 접속 끊김"
		msg['From'] = sendEmail 
		msg['To'] = recvEmail 

		#본문 추가
		text = "."
		contentPart = MIMEText(text) #MIMEText(text , _charset = "utf8")
		msg.attach(contentPart) 

		#파일 추가
		etcFileName = self.code+'new_before.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 
		#파일 추가
		etcFileName = self.code+'gameids.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		etcFileName = self.code+'backup_gameids.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		etcFileName = self.code+'backup_new_before.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		s=smtplib.SMTP( smtpName , smtpPort )
		s.starttls()
		s.login( sendEmail , password ) 
		s.sendmail( sendEmail, recvEmail, msg.as_string() )  
		s.close()


	#아래 두 함수 load_json과 write_json은 딕셔너리, 리스트 같은 것들을 그 자체로 저장하고 읽을 수 있습니다.
	#가령 dict_a={}를 텍스트'dict_a={}'가 아닌 dict_a={} 그 자체로 저장하고 읽을 수 있습니다.
	#이걸 쓰면 큰 데이터들을 미리 모아두고 코드에서 읽어서 바로 딕셔너리로 사용할 수 있습니다
	def load_json(filename):
		file = pathlib.Path(str(filename)+'.json')
		file_text = file.read_text(encoding='utf-8-sig')
		return json.loads(file_text)


	def write_json(filename,data):
		with open(str(filename)+'.json','w',encoding='UTF-8-sig') as file:
			file.write(json.dumps(data,ensure_ascii=False))


	def getKey(self):
		print('getKey메소드')
		f= open('api_key.txt','r')
		key=f.readline()[:-2]
		f.close()
		self.api_key = key

	def req_api(url):
		response = requests.get(url)
		#반응이 200이 아니면 뭔가 잘못된 것입니다.
		if str(response)!='<Response [200]>':
			if str(response) =='<Response [429]>':
				#time.sleep(600)
				print(response)
				time.sleep(600)
				return -1
			elif str(response)=='<Response [403]>':
				print('403이다!!!!!!!!!!!!!!!!!!!!!!!!!')
				now = datetime.datetime.now()
				print('403발생시각:',now)
				send_final()
				self.quit_sign=1
				write_json('quit_sign',1)
				return 0
			else:
				print(response)
				time.sleep(10)
				return 0
		#반응이 200이면 정상입니다.
		else:
			time.sleep(1.5)
			return response.json()


	#챔피언, 시즌, 큐타입 등 롤에대한 기본적인 정보를 가져옵니다.
	#keytochamp={챔피언key:챔피언이름}
	def phase1(self):
		print('롤 기본 데이터 수집')
		#챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
		#dict_keys(['type', 'format', 'version', 'data'])
		keytochamp={}
		#버전바뀔때마다 교체해줘야합니다. 적어도 신챔 나올때는 교체해줘야됩니다.
		#http://ddragon.leagueoflegends.com/cdn/10.2.1/data/ko_KR/champion.json -> http://ddragon.leagueoflegends.com/cdn/11.3.1/data/ko_KR/champion.json
		whole_champions=requests.get("https://ddragon.leagueoflegends.com/cdn/11.17.1/data/ko_KR/champion.json").json()
		for champ in list(whole_champions['data'].keys()):
			keytochamp[whole_champions['data'][champ]['key']]=whole_champions['data'][champ]['name']

		#시즌정보 / [{}]
		season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()
		self.season_data=season_data
		#큐타입정보[{}]
		#{'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
		queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()
		self.queqe_data=queqe_data
		self.keytochamp=keytochamp
		###################여기까지기본정보받아오는곳


	#계정의 게임아이디를 accountId로 바꿉니다
	#가령 우주짱짱맨 -> ABCD-1234-ASDF 이런식입니다
	#accountId가 있어야 해당 계정의 게임 내역을 가져올 수 있습니다.
	def summonerName_to_accountId(self,summonerName):
		#print(summonerName,'의 accountId 요청')
		#global api_key
		url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+summonerName+'?api_key='+self.api_key
		base_data = req_api(url)
		return base_data['accountId']

	#계정의 accountId를 인자로 받고 최근 게임의 gameid를 리턴합니다.
	#최근 게임이어도 이번 패치 버전 이전의 게임이라면 "얘꺼다봄"을 출력하고 넘어갑니다.
	def from_accountId_get_gameid(self,accountId):
		#print('gameid 가져오는중')
		#url = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/'+accountId+'?queue=420&endIndex='+str(endindex)+'&beginIndex='+str(beginindex)+'&api_key='+api_key
		url ='https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/'+accountId+'?queue=420&api_key='+self.api_key

		#gameids.json이 이미 있다면 가져오고 없다면 생성하여 가져옵니다. 중복자료 처리에 사용됩니다.
		try:
			gameids=load_json(self.code+'gameids')
		except:
			write_json('gameids',[])
			gameids = load_json(self.code+'gameids')


		data = req_api(url)
		if data!=0 and data!=-1:
			#계정의 게임 기록들은 data라는 dict의 'matches'라는 key로 접근합니다
			for i in range(len(data['matches'])):
				gameid = data['matches'][i]['gameId']
				#5대5 게임인점, 유저를 먼저 모으고 각 유저의 게임기록을 살펴보는점 때문에 이미 조사한 게임이 중복되서 들어오는 경우가 생깁니다.
				#gameids.json은 그런 문제를 해결합니다. 이미 gameids에 있는 gameid라면 continue합니다.
				if gameid in gameids:
					continue
				else:
					#중복자료가 아니고 이번 버전에서 행해진 게임이라면 gameids에 기록하여 다음 중복자료 탐색에 사용하고  str타입으로 gameid를 리턴합니다.
					#gameid는 여러개 받아와도 하나만 사용하는 이유는 최대한 다양한 유저의 자료를 사용해야 치우침이 없을 것 같았습니다.
					gameids.append(gameid)
					write_json('gameids',gameids)
					#매 패치마다 수정해야하는 부분입니다. 에포크밀리초로 지난 패치시점의 게임기록은 기록하지 않습니다.
					#https://www.epochconverter.com/
					if data['matches'][i]['timestamp']<self.epochmillisecond:
						print("얘꺼 이번패치 기록 끝")
						return 3
					return str(gameid)
			else:
				print("얘꺼다봄######################################################")
				return 0
		else:
			return 0

	#gameids를 인자로 받아 해당 gameid를 가진 판에서 누가 원딜이었고 누가 서폿이었는지 반환합니다.
	#아래 get_bottom_final과 get_bottom_full과 세트입니다.
	#get_bottom_full은 보기 편하려고 만들었습니다.
	#라인전이 이뤄지는 15분 정도까지의 각 플레이어의 시간대별 위치 좌표를 받고
	#바텀에 있으면 bot_point를 1올려 bot_point가 가장 높은 사람 둘이 바텀 라이너들이라고 정하는 방식입니다
	#원딜과 서폿의 구분은 씨에스의 양으로 구분했습니다.
	#바텀 뿐만 아니라 탑, 미드, 정글 등도 같은 원리로 구분했습니다.
	#정글 구분이 힘들었는데 15분까지 정글 몬스터를 가장 많이 잡은 유저를 정글러로 분류했습니다.
	def get_bottom_base(self, gameid):
		#print('phase5')
		#global api_key
		#일단 데이터 요청
		url = 'https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/'+gameid+'?api_key='+self.api_key
		#position = req_api(url)
		#position['frames']에 시간별 위치정보 들어있음
		frames=position['frames']
		dongsun = {}
		#participantid는 게임내 참여자 참가번호같은거
		#dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
		for frame in frames:
			#print(frame['timestamp'])
			partiframe = frame['participantFrames']
			for pf in list(partiframe.keys()):
				participantid = str(partiframe[pf]['participantId'])
				if participantid not in dongsun.keys():
					dongsun[participantid]=[]
				if 'position' not in partiframe[pf].keys():
					continue
				#print(pf,partiframe[pf]['position'])
				dongsun[participantid].append(partiframe[pf]['position'])

		
		#여기부터 ptl.show()까지 시각화
		#for i in range(1,11):
		#	i=str(i)
		#	for j in dongsun[i]:
		#		if i=='3':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		elif i=='10':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		else:
		#			plt.scatter(j['x'],j['y'],c='b')
		#
		#plt.show()
		
		
		#member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
		member = []
		#i는 participantid
		for i in range(1,11):
			i=str(i)
			#i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
			botpoint=0
			#botpoint의 반대
			elsepoint=0
			#몇분시점인지 count로 체크
			count=0
			#dongsun[i][j]는 j시점 i번 플레이어의 위치
			for j in dongsun[i]:
				count+=1
				#15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
				if count>12:
					break
				#바텀좌표에 있었으면 botpoint에 +1
				if (j['x']>10000 and j['y']<5000) or (j['x']<10000 and j['y']<2000) or (j['x']>13000 and j['y']>0):
					botpoint+=1
				else:
					elsepoint+=1
			#이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
			member.append([botpoint,botpoint-elsepoint,i])
		#member를 botpoint 기준으로 오름차순 정렬
		member.sort()
		#결과에 get_bot()함수의 인자인 gameid 넣어두고
		result = [gameid]
		#botpoint 상위 네명의 participantid를 result에 넣는다
		#pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
		#결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다
		for i in range(4):
			result.append(member.pop()[-1])
		if len(result)!=5:
			return 0
		check = result[1:]
		frame = frames[-1]
		participantFrames = frame['participantFrames']
		know_cs = {}
		for pf in participantFrames.keys():
			for pid in check:
				if str(participantFrames[pf]['participantId'])==pid:
					#봇과 봇씨에스가 맞게 나오나 보려면 해제
					#print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
					know_cs[pid]=participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled']

		return result,know_cs

	def get_botttom_final(self,bot):
		#print('phase6')
		#gameid는 gameid에
		gameid = bot[0][0]
		#여기부터 서폿둘 원딜둘 따로나누는부분
		botcombi=bot[1]
		bot = []
		for i in botcombi.keys():
			bot.append([botcombi[i],i])
		bot.sort()
		supports = bot[:2]
		adcs = bot[2:]
		#여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

		#url = 'https://kr.api.riotgames.com/lol/match/v4/matches/'+gameid+'?api_key='+api_key
		#data = req_api(url)
		data = self.ffdata

		teama =data['teams'][0]
		teamb =data['teams'][1]
		
		###승리팀구분, 한쪽만 이기지않으면 오류
		#승리팀들어갈곳
		winteam = 0
		if (teama['win']=='Fail' and teamb['win']=='Win') or (teama['win']=='Win' and teamb['win']=='Fail'):
			if teama['win']=='Win':
				winteam=teama['teamId']
			else:
				winteam=teamb['teamId']

		else:
			return 0
		###
		adc_result =[]
		for adc in adcs:
			pid = adc[1]
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					adc_result.append([pt['teamId'],keytochamp[str(pt['championId'])]])
		spt_result =[]
		for spt in supports:
			pid = spt[1]
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					spt_result.append([pt['teamId'],keytochamp[str(pt['championId'])]])
		lastdata = []
		for i in adc_result:
			if i[0]==100:
				lastdata.append(i)
		for i in spt_result:
			if i[0]==100:
				lastdata.append(i)

		for i in adc_result:
			if i[0]==200:
				lastdata.append(i)
		for i in spt_result:
			if i[0]==200:
				lastdata.append(i)
		lastdata.append(winteam)
		t1=0
		t2=0
		for i in lastdata[:-1]:
			if i[0]==100:
				t1+=1
			elif i[0]==200:
				t2+=1
			else:
				print('이상 팀 정보')
				return 0
		if t1!=2 or t2!=2:
			print('이상 팀 정보')
			return 0
		if lastdata[-1]!=100 and lastdata[-1]!=200:
			print('이상 팀 정보')
			return 0


		'''
		###여기부터
		try:
			new_before = load_json('new_before')
		except:
			write_json('new_before',[])
			new_before = load_json('new_before')
		new_before.append(lastdata)
		write_json('new_before',new_before)
		##여기까지 삭제예정
		'''
		return lastdata

	def get_bottom_full(self,gameid):
		#print('바텀 정보 분석중')
		return self.get_botttom_final(self.get_bottom_base(gameid))
	

	#아래 new_phase6(),  mid_phase6(), get_mid_full과 세트입니다 원리는 get_bot 세트와 같습니다
	def new_phase5(self,gameid):
		#print('phase5')
		#global api_key
		#일단 데이터 요청
		url = 'https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/'+gameid+'?api_key='+self.api_key
		#position = req_api(url)
		#position['frames']에 시간별 위치정보 들어있음
		frames=self.position['frames']
		dongsun = {}
		#participantid는 게임내 참여자 참가번호같은거
		#dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
		frame = frames[5]
		participantFrames = frame['participantFrames']
		know_cs = {}
		members=[]
		for pf in participantFrames.keys():
			members.append([participantFrames[pf]['jungleMinionsKilled'],participantFrames[pf]['participantId']])
		members.sort()
		result = members[-2:]
		return [[gameid],result]


	def new_phase6(self,bot):
		#print('phase6')
		#gameid는 gameid에
		gameid = bot[0][0]
		#여기부터 서폿둘 원딜둘 따로나누는부분
		botcombi=bot[1]

		bot = [str(botcombi[0][1]),str(botcombi[1][1])]
		
		#여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

		url = 'https://kr.api.riotgames.com/lol/match/v4/matches/'+gameid+'?api_key='+self.api_key
		#data = req_api(url)
		data=self.ffdata
		teama =data['teams'][0]
		teamb =data['teams'][1]
		
		###승리팀구분, 한쪽만 이기지않으면 오류
		#승리팀들어갈곳
		winteam = 0
		if (teama['win']=='Fail' and teamb['win']=='Win') or (teama['win']=='Win' and teamb['win']=='Fail'):
			if teama['win']=='Win':
				winteam=teama['teamId']
			else:
				winteam=teamb['teamId']

		else:
			return 0
		###
		lastdata = []
		for jg in bot:
			pid = jg
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					lastdata.append([pt['teamId'],keytochamp[str(pt['championId'])]])

		
		lastdata.append(winteam)
		if lastdata[0][0]==200:
			temp = lastdata[0]
			lastdata[0]=lastdata[1]
			lastdata[1]=temp
		t1=0
		t2=0
		for i in lastdata[:-1]:
			if i[0]==100:
				t1+=1
			elif i[0]==200:
				t2+=1
			else:
				print('이상 팀 정보1')
				return 0
		if t1!=1 or t2!=1:
			print('이상 팀 정보2')
			return 0
		if lastdata[-1]!=100 and lastdata[-1]!=200:
			print('이상 팀 정보3')
			return 0




	#	try:
	#		new_before = load_json('new_before')
	#	except:
	#		write_json('new_before',[])
	#		new_before = load_json('new_before')
	#	new_before.append(lastdata)
	#	write_json('new_before',new_before)
		return lastdata



	#아래 mid_phase6(), get_mid_full과 세트입니다 원리는 get_bot 세트와 같습니다
	def mid_phase5(self,gameid):
		#print('phase5')
		global api_key
		#일단 데이터 요청
		url = 'https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/'+gameid+'?api_key='+self.api_key
		#position = req_api(url)
		#position['frames']에 시간별 위치정보 들어있음
		frames=self.position['frames']
		dongsun = {}
		#participantid는 게임내 참여자 참가번호같은거
		#dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
		for frame in frames:
			#print(frame['timestamp'])
			partiframe = frame['participantFrames']
			for pf in list(partiframe.keys()):
				participantid = str(partiframe[pf]['participantId'])
				if participantid not in dongsun.keys():
					dongsun[participantid]=[]
				if 'position' not in partiframe[pf].keys():
					continue
				#print(pf,partiframe[pf]['position'])
				dongsun[participantid].append(partiframe[pf]['position'])

		
		#여기부터 ptl.show()까지 시각화
		#for i in range(1,11):
		#	i=str(i)
		#	for j in dongsun[i]:
		#		if i=='3':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		elif i=='10':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		else:
		#			plt.scatter(j['x'],j['y'],c='b')
		#
		#plt.show()
		
		
		#member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
		member = []
		#i는 participantid
		for i in range(1,11):
			i=str(i)
			#i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
			botpoint=0
			#botpoint의 반대
			elsepoint=0
			#몇분시점인지 count로 체크
			count=0
			#dongsun[i][j]는 j시점 i번 플레이어의 위치
			for j in dongsun[i]:
				count+=1
				#15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
				if count>10:
					break
				#바텀좌표에 있었으면 botpoint에 +1
				if (j['x']>6000 and j['x']<8000) and (j['y']>7000 and j['y']<8000):
					botpoint+=1
				else:
					elsepoint+=1
			#이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
			member.append([botpoint,botpoint-elsepoint,i])
		#member를 botpoint 기준으로 오름차순 정렬
		member.sort()
		#결과에 get_bot()함수의 인자인 gameid 넣어두고
		result = [gameid]
		#botpoint 상위 네명의 participantid를 result에 넣는다
		#pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
		#결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다
		for i in range(2):
			result.append(member.pop()[-1])
		if len(result)!=3:
			return 0
		check = result[1:]
		frame = frames[-1]
		participantFrames = frame['participantFrames']
		know_cs = {}
		for pf in participantFrames.keys():
			for pid in check:
				if str(participantFrames[pf]['participantId'])==pid:
					#봇과 봇씨에스가 맞게 나오나 보려면 해제
					#print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
					know_cs[pid]=participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled']

		return result,know_cs


	def mid_phase6(self,bot):
		#print('phase6')
		#gameid는 gameid에
		gameid = bot[0][0]
		#여기부터 서폿둘 원딜둘 따로나누는부분
		jglist = self.new_phase6(self.new_phase5(gameid))
		botcombi=bot[1]
		bot = []
		for i in botcombi.keys():
			bot.append([botcombi[i],i])
		bot.sort()
		supports = bot[:1]
		adcs = bot[1:]
		#여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

		url = 'https://kr.api.riotgames.com/lol/match/v4/matches/'+gameid+'?api_key='+self.api_key
		#data = req_api(url)
		data=self.ffdata
		teama =data['teams'][0]
		teamb =data['teams'][1]
		
		###승리팀구분, 한쪽만 이기지않으면 오류
		#승리팀들어갈곳
		winteam = 0
		if (teama['win']=='Fail' and teamb['win']=='Win') or (teama['win']=='Win' and teamb['win']=='Fail'):
			if teama['win']=='Win':
				winteam=teama['teamId']
			else:
				winteam=teamb['teamId']

		else:
			return 0
		###
		adc_result =[]
		for adc in adcs:
			pid = adc[1]
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					adc_result.append([pt['teamId'],keytochamp[str(pt['championId'])]])
		spt_result =[]
		for spt in supports:
			pid = spt[1]
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					spt_result.append([pt['teamId'],keytochamp[str(pt['championId'])]])
		lastdata = []
		for i in adc_result:
			if i[0]==100:
				lastdata.append(i)
		for i in spt_result:
			if i[0]==100:
				lastdata.append(i)

		for i in adc_result:
			if i[0]==200:
				lastdata.append(i)
		for i in spt_result:
			if i[0]==200:
				lastdata.append(i)
		lastdata.append(winteam)
		t1=0
		t2=0
		for i in lastdata[:-1]:
			if i[0]==100:
				t1+=1
			elif i[0]==200:
				t2+=1
			else:
				print('이상 팀 정보')
				return 0
		if t1!=1 or t2!=1:
			print('이상 팀 정보')
			return 0
		if lastdata[-1]!=100 and lastdata[-1]!=200:
			print('이상 팀 정보')
			return 0

		lastdata.insert(1,jglist[0])
		lastdata.insert(3,jglist[1])

		'''
		try:
			new_before = load_json('new_before')
		except:
			write_json('new_before',[])
			new_before = load_json('new_before')
		new_before.append(lastdata)
		write_json('new_before',new_before)
		'''
		return lastdata
	def get_mid_full(gameid):
		#print('미드 정보 분석중')
		return self.mid_phase6(self.mid_phase5(gameid))


	#아래 get_top_final(), get_top_full과 세트입니다 원리는 get_bot 세트와 같습니다
	def get_top_base(self,gameid):
		#print('phase5')
		#global api_key
		#일단 데이터 요청
		url = 'https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/'+gameid+'?api_key='+self.api_key
		#position = req_api(url)
		#position['frames']에 시간별 위치정보 들어있음
		frames=self.position['frames']
		dongsun = {}
		#participantid는 게임내 참여자 참가번호같은거
		#dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
		for frame in frames:
			#print(frame['timestamp'])
			partiframe = frame['participantFrames']
			for pf in list(partiframe.keys()):
				participantid = str(partiframe[pf]['participantId'])
				if participantid not in dongsun.keys():
					dongsun[participantid]=[]
				if 'position' not in partiframe[pf].keys():
					continue
				#print(pf,partiframe[pf]['position'])
				dongsun[participantid].append(partiframe[pf]['position'])

		
		#여기부터 ptl.show()까지 시각화
		#for i in range(1,11):
		#	i=str(i)
		#	for j in dongsun[i]:
		#		if i=='3':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		elif i=='10':
		#			plt.scatter(j['x'],j['y'],c='b')
		#		else:
		#			plt.scatter(j['x'],j['y'],c='b')
		#
		#plt.show()
		
		
		#member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
		member = []
		#i는 participantid
		for i in range(1,11):
			i=str(i)
			#i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
			botpoint=0
			#botpoint의 반대
			elsepoint=0
			#몇분시점인지 count로 체크
			count=0
			#dongsun[i][j]는 j시점 i번 플레이어의 위치
			for j in dongsun[i]:
				count+=1
				#15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
				if count>12:
					break
				#바텀좌표에 있었으면 botpoint에 +1
				if (j['y']>0 and j['x']<2000) or (j['x']<4000 and j['y']<10000) or (j['x']>0 and j['y']>12000):
					botpoint+=1
				else:
					elsepoint+=1
			#이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
			member.append([botpoint,botpoint-elsepoint,i])
		#member를 botpoint 기준으로 오름차순 정렬
		member.sort()
		#결과에 get_bot()함수의 인자인 gameid 넣어두고
		result = [gameid]
		#botpoint 상위 네명의 participantid를 result에 넣는다
		#pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
		#결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다
		for i in range(2):
			result.append(member.pop()[-1])
		if len(result)!=3:
			return 0
		check = result[1:]
		frame = frames[-1]
		participantFrames = frame['participantFrames']
		know_cs = {}
		for pf in participantFrames.keys():
			for pid in check:
				if str(participantFrames[pf]['participantId'])==pid:
					#봇과 봇씨에스가 맞게 나오나 보려면 해제
					#print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
					know_cs[pid]=participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled']
		#print(result,know_cs)

		return result,know_cs


	def get_top_final(bot):
		#global api_key
		#print('phase6')
		#gameid는 gameid에
		gameid = bot[0][0]
		#need는 len이 2
		need=bot[0][1:]
		url = 'https://kr.api.riotgames.com/lol/match/v4/matches/'+gameid+'?api_key='+self.api_key
		#data = req_api(url)
		data=self.ffdata
		teama =data['teams'][0]
		teamb =data['teams'][1]
		
		###승리팀구분, 한쪽만 이기지않으면 오류
		#승리팀들어갈곳
		winteam = 0
		if (teama['win']=='Fail' and teamb['win']=='Win') or (teama['win']=='Win' and teamb['win']=='Fail'):
			if teama['win']=='Win':
				winteam=teama['teamId']
			else:
				winteam=teamb['teamId']

		lastdata=[]
		for adc in need:
			pid = adc
			for pt in data['participants']:
				if str(pt['participantId']) ==pid:
					lastdata.append([pt['teamId'],keytochamp[str(pt['championId'])]])
		lastdata.append(winteam)
		return lastdata
	def get_top_full(self,gameid):
		#print('탑 정보 분석중')
		return self.get_top_final(self.get_top_base(gameid))


	#수집기의 최종 자료인 new_before.json을 만드는 부분입니다.
	def collect(self,nick):
		print(nick,'의 정보 분석 시작')
		#닉 -> 어카운트
		account=self.summonerName_to_accountId(nick)
		#어카운트 -> 게임아디
		gameid = self.from_accountId_get_gameid(account)

		##5대5 게임인 롤에는 [top, mid, jungle, bottom, support] 5개의 포지션이 있습니다. 
		#이 아래로는 게임아이디를 -> 각 팀별, 포지션별 챔피언이 무엇인지 구분하는 부분입니다.
		#global position
		url = 'https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/'+gameid+'?api_key='+self.api_key
		self.position = self.req_api(url)
		#global ffdata
		uurl = 'https://kr.api.riotgames.com/lol/match/v4/matches/'+gameid+'?api_key='+api_key
		self.ffdata = self.req_api(uurl)

		#api에서 시스템적 요소인 팀은 잘 구분해줍니다. 포지션은 api의 정확도가 떨어집니다. 그래서 포지션을 알아낼 부분은 따로 만들어야했습니다.
		#아래 세개의 행은 시간대별 위치좌표를 이용하여 어느 캐릭터가 어떤포지션이었는지를 알아내는 부분입니다.
		top=self.get_top_full(gameid)
		midjg=self.get_mid_full(gameid)
		bot=self.get_bottom_full(gameid)
		

		#이 아래로는 최종적으로 100팀과 200팀의 top,mid,jg,sup,bot과 승팀, 패팀을 구분하여 최종 데이터를 구성하는 부분입니다.
		#자료가 오류자료가 아닌지 마지막으로 확인하는 부분이기도 합니다
		#포지션별로 100팀과 200팀의 인원수가 맞는지 점검하고 맞다면 각 팀 딕셔너리의 포지션 key에 챔피언명을 기입합니다. 
		thisgame = {}
		team_100={}
		team_200={}
		if len(top)==3:
			if top[0][0]==100 and top[1][0] ==200:
				team_100['top']=top[0][1]
				team_200['top']=top[1][1]
			elif top[0][0]==200 and top[1][0] ==100:
				team_200['top']=top[0][1]
				team_100['top']=top[1][1]
			else:
				return -1
		else:
			return 0



		if len(midjg)==5:
			if midjg[0][0]==100 and midjg[1][0]==100 and midjg[2][0]==200 and midjg[3][0]==200:
				team_100['jungle']=midjg[1][1]
				team_100['mid'] = midjg[0][1]
				team_200['jungle'] = midjg[3][1]
				team_200['mid']=midjg[2][1]
			elif midjg[0][0]==200 and midjg[1][0]==200 and midjg[2][0]==100 and midjg[3][0]==100:
				team_200['jungle']=midjg[1][1]
				team_200['mid'] = midjg[0][1]
				team_100['jungle'] = midjg[3][1]
				team_100['mid']=midjg[2][1]
			else:
				return -1
		else:
			return 0


		if len(bot)==5:
			if bot[0][0]==100 and bot[1][0]==100 and bot[2][0]==200 and bot[3][0]==200:
				team_100['adc']=bot[0][1]
				team_100['sup'] = bot[1][1]
				team_200['adc'] = bot[2][1]
				team_200['sup']=bot[3][1]
			elif bot[0][0]==200 and bot[1][0]==200 and bot[2][0]==100 and bot[3][0]==100:
				team_200['adc']=bot[0][1]
				team_200['sup'] = bot[1][1]
				team_100['adc'] = bot[2][1]
				team_100['sup']=bot[3][1]
			else:
				return -1
		else:
			return 0

		thisgame['team_blue']=team_100
		thisgame['team_red']=team_200
		if top[-1]==200:
			thisgame['winteam']='red'
		else:
			thisgame['winteam']='blue'

		thisgame['gameid']=gameid

		#print('@'*100)
		for i in list(thisgame.keys()):
			if i=='winteam':
				print(i,thisgame[i],end=', ')
			else:
				print(i,thisgame[i])
		for t in ("team_blue","team_red"):
			len_a = len(thisgame[t].values)
			len_b = len(set(thisgame[t].values))
			if len_a!=len_b:
				print("중복자료(기입X)")
				return 0

		print('@'*100)
		try:
			new_before = load_json(self.code+'new_before')
		except:
			write_json('new_before',[])
			new_before = load_json(self.code+'new_before')
		new_before.append(thisgame)
		write_json(self.code+'new_before',new_before)

	#아래 함수 get_4000과 세트입니다. 분석대상인 자료를 수집하는 부분입니다. 
	#조사를 원하는 metal의 tier1/2/3/4를 1000명씩 수집해 4000명을 만들었습니다.
	def get_user(self,metal,tier,personnel):
		#global api_key
		page=1
		player_list = []
		while True:
			url = 'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/'+metal+'/'+tier+'?page='+str(page)+'&api_key='+self.api_key
			base_data  = self.req_api(url)
			if len(base_data)==0:
				print(metal+tier+'유저가 부족하여 목표치인'+str(personnel)+'보다 적은'+str(len(player_list))+'만 수집 후 리턴')
				return player_list
			for i in range(len(base_data)):
				player_list.append(base_data[i]['summonerName'])
				if len(player_list)==personnel:
					return player_list
			page+=1

	def get_4000(self,metal):
		IV_1000 = self.get_user(metal,"IV",1000)
		III_1000 = self.get_user(metal,"III",1000)
		II_1000 = self.get_user(metal,"II",1000)
		I_1000 = self.get_user(metal,"I",1000)
		whole = IV_1000+III_1000+II_1000+I_1000
		random_whole = whole[:]
		random.shuffle(random_whole)
		return random_whole


	#실행시 백업을 하고 시작합니다.
	def send_before(self):
		sendEmail = "jyanoos1993@gmail.com"
		recvEmail = "fox_93@naver.com"
		password = "ytttqzpiakaturft"

		smtpName = "smtp.gmail.com"
		smtpPort = 587

		#여러 MIME을 넣기위한 MIMEMultipart 객체 생성
		msg = MIMEMultipart()

		msg['Subject'] ="롤 데이터 백업"
		msg['From'] = sendEmail 
		msg['To'] = recvEmail 

		#본문 추가
		text = "."
		contentPart = MIMEText(text) #MIMEText(text , _charset = "utf8")
		msg.attach(contentPart) 

		#파일 추가
		etcFileName = self.code+'new_before.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 
		#파일 추가
		etcFileName = self.code+'gameids.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		etcFileName = self.code+'backup_gameids.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		etcFileName = self.code+'backup_new_before.json'
		with open(etcFileName, 'rb') as etcFD : 
		    etcPart = MIMEApplication( etcFD.read() )
		    #첨부파일의 정보를 헤더로 추가
		    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
		    msg.attach(etcPart) 

		s=smtplib.SMTP( smtpName , smtpPort )
		s.starttls()
		s.login( sendEmail , password ) 
		s.sendmail( sendEmail, recvEmail, msg.as_string() )  
		s.close()

	def start(self):
		def send_all_ids(msg):
			ids={"연우":"1993842151", "재구":"747977556"}
			for id in ids.keys():
				telegram_sendMSG(ids[id],msg)

		#global quit_sign
		#global api_key
		#롤 기본정보 수집//버전, 패치별 코드 수정 필요
		self.phase1()
		while True:
			count = 0
			#key에 문제가 생기면 여기서 처리
			if self.quit_sign==1:
				send_once=0
				err_key = self.api_key
				while True:
					#success = get_key_from_mail()
					if load_json('quit_sign')==0:
						success=1
					else:
						success=0

					
					if success==1:
						self.api_key=getkey()
						print("key교체\n{}\n--->{}".format(err_key,api_key))
						send_all_ids("key교체\n{}\n--->{}\n교체완료".format(err_key,api_key))
						self.quit_sign=0
						self.send_before()
						break
					else:
						print("key 교체 대기중",end=' ')
						now = datetime.datetime.now()
						print(now)
						time.sleep(10)
						if send_once==0:
							send_all_ids("키 교체 필요")
							send_once=1
			

			#key에 문제 없으면 시작
			#1. 유저 리스트를 만든다 4000명, 셔플
			try:
				user_list = self.get_4000("PLATINUM")
			except:
				continue

			#2. 각 유저별 가장 최근 게임이면서 이번 게임 버전에 맞는 게임이라면 분석하여 new_before에 기록
			for user in user_list:
				try:
					self.collect(user)
				except:
					if self.quit_sign==1:
						break
					else:
						continue
				#try절에 문제 없으면 else문도 실행됨//1000개 자료 기입시마다 1번씩 메일로 백업
				else:
					count+=1
					if count==1000:
						g_backup = load_json(self.code+'gameids')
						write_json(self.code+'backup_gameids',g_backup)
						backup = load_json(self.code+'new_before')
						write_json(self.code+'backup_new_before',backup)

						self.send_before()
						print('백업완료, 메일완료')
						count=0

a=LolCollector(2021,9,9)
a.start()
