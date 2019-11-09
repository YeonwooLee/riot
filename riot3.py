import requests
import json
import operator
import datetime
import time
from skimage import io # 미니맵 처리
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np

#챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
whole_champions=requests.get("http://ddragon.leagueoflegends.com/cdn/9.21.1/data/ko_KR/champion.json").json()

#챔피언정보, 최상위키는 챔피언이름,딕딕구조{Aatrox:{version:,id:'챔피언이름',key:'챔피언비밀아이디',name:'챔피언이름'}}
dict_champions_info=whole_champions['data']
#{영어챔피언이름:한글챔피언이름}
eng_to_kor_champname={}
for i in list(dict_champions_info.keys()):
	eng_to_kor_champname[i]=dict_champions_info[i]['name']
	
#챔피언 이름만 모아놓은 리스트
all_champion_names=list(dict_champions_info.keys())


#시즌정보 / [{}]
season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()

#큐타입정보[{}]
#{'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()

#암호화된 {챔피언아이디:챔피언이름}
champion_id_encrypted={}
#이포문 돌리면 모든챔피언 정보에 접근
for i in range(len(all_champion_names)):
	champion_id_encrypted[dict_champions_info[all_champion_names[i]]['key']]=all_champion_names[i]


summoner_name="꼬몽딸레몽"
url_front="https://kr.api.riotgames.com/"
api_key="?api_key=RGAPI-d8cc6dad-d288-47f8-8b24-953df9a30ef0"

#유저기본정보
url_summoner_base= "lol/summoner/v4/summoners/by-name/"+summoner_name
combi_summoner_base = url_front+url_summoner_base+api_key

#딕셔너리, 유저기본정보
#key목록
#id: encryptedid, accountId : 뭔지모름, puuid: 뭔지모름
#name: 소환사닉, revisionDate: 갱신일인듯, summonerLevel: 레벨
#{'id': 'wk2kwDM-AMGvFNd5SSJ9lziIhVAroLIFWrS21sSt9j9XbQ', 'accountId': 'na-hx-RKQYkUNb1hj4P-0N89ZGojItqh5j0EbNDmb0W4', 'puuid': 'i41HJZGC2M2pdd-tWkwhI1peaSUbQV8Bvh-EbSwrolo2W3dRytPzq8nfT20kR8xayhywd_5lE_pPNQ', 'name': '안호진똥똥꼬냄새', 'profileIconId': 4088, 'revisionDate': 1571942416000, 'summonerLevel': 113}
dict_user_base=requests.get(combi_summoner_base).json()
#유저 암호화닉
user_id_encrypted=dict_user_base['id']
#print(summoner_name,user_id_encrypted)

accountId=dict_user_base['accountId']

#챔피언숙련도
url_champion_mastery ="lol/champion-mastery/v4/champion-masteries/by-summoner/"+dict_user_base['id']
combi_champion_mastery=url_front+url_champion_mastery+api_key

#딕셔너리를 원소로 가지는 리스트[{챔피언1},{챔피언2}]
#key목록
#championId,championLevel,championPoints
list_dict_champion_mastery=requests.get(combi_champion_mastery).json()

#챔피언 마스터리 이차원배열 원소는 [챔피언이름,숙련도,숙련도]
summary_champion_mastery = []
for i in list_dict_champion_mastery:
	templist=[]
	#print(champion_id_encrypted[str(i['championId'])],end=": ")
	templist.append(champion_id_encrypted[str(i['championId'])])
	#print(i['championLevel'],end=", ")
	templist.append(i['championLevel'])
	#print(i['championPoints'])
	templist.append(i['championPoints'])
	summary_champion_mastery.append(templist)
'''
#summary_champion_mastery 출력문
for i in range(len(summary_champion_mastery)):
	print(summary_champion_mastery[i])
'''
#유저 랭겜 요약 몇승몇패 티어 LP 등에 쓰이는 api주소
url_user_rankgame= "lol/league/v4/entries/by-summoner/"
#유저 랭겜 요약 실재
#끝에 [1] 붙인 이유는 [0]이 팀랭임
#{'leagueId': 'ac50c910-2dca-11e9-8f87-c81f66e3887d', 'queueType': 'RANKED_SOLO_5x5', 'tier': 'GOLD', 'rank': 'IV', 'summonerId': 'h4onO2W1MSq0t5rVKsCA6hR-iQuEjPXNi3W0v1t51j-SLdY', 'summonerName': 'opplk123', 'leaguePoints': 47, 'wins': 619, 'losses': 650, 'veteran': False, 'inactive': False, 'freshBlood': False, 'hotStreak': False}
if len(requests.get(url_front+url_user_rankgame+user_id_encrypted+api_key).json())==1:
	combi_user_rankgame=requests.get(url_front+url_user_rankgame+user_id_encrypted+api_key).json()[0]
elif len(requests.get(url_front+url_user_rankgame+user_id_encrypted+api_key).json())==2:
	combi_user_rankgame=requests.get(url_front+url_user_rankgame+user_id_encrypted+api_key).json()[1]
###포문으로 바꿀시 여기 else 추가해서 이상한 도미니언랭겜 이런거 드가나확인


#매치 기본정보. 게임아이디 사용챔피언 큐타입 시즌 등
#최근게임들..
url_user_match="lol/match/v4/matchlists/by-account/"
#[{}] {'platformId': 'KR', 'gameId': 3960314506, 'champion': 81, 'queue': 420, 'season': 13, 'timestamp': 1573090181100, 'role': 'DUO', 'lane': 'NONE'}
combi_user_match=requests.get(url_front+url_user_match+accountId+api_key).json()['matches']
#랭겜아닌거 지우는과정
dellist=[]
for i in range(len(combi_user_match)):
	if combi_user_match[i]['queue']!=420:
		dellist.append(i)
dellist.reverse()
for i in dellist:
	del(combi_user_match[i])


'''최근 100판(combi_user_match 이거 할때 100개가 최대인듯) 시작시간 출력/ timestamp 변환법
for i in combi_user_match:
	print(datetime.datetime.fromtimestamp(i['timestamp']/1000/60))
'''
#최근0번째판의 매치아이디 11070724 테스트 차후 0만 아니라 늘리면 많은게임 볼 수 있다
#한 개임의 요약정보 퍼블 퍼타 등 승패 밴 각 플레이어 정보
if len(combi_user_match)<1:
	print("랭겜기록 없는 소환사")
	quit()
gameId=combi_user_match[0]['gameId']
#이거 키면 소환사의 여러게임 조사가능
'''
for k in range(10):
	gameId=combi_user_match[k]['gameId']
	print("gameId:",gameId)
'''
#teams=[{}.keys=['팀아이디,승리여부,퍼블,퍼타,퍼억,퍼바론,퍼드레곤,퍼전령,부순타워,부순억제기,잡은바론,잡드래곤,밴[{챔피언아이디:챔피언,픽턴:픽턴}]']]

#전체 정보
summary_game=requests.get("https://kr.api.riotgames.com/lol/match/v4/matches/"+str(gameId)+api_key).json()
#summary_game=requests.get("https://kr.api.riotgames.com/lol/match/v4/matches/3960142353?api_key=RGAPI-abe63137-7e8f-4440-9ba6-276fe6e0cba3").json()
#for i in range(10):
	#print(summary_game['participants'][i])
#유저인식 s_g 는 서머리게임
partitipantities_s_g=summary_game['participantIdentities']
#participantId={'participantId':summonerName}
#teamline 위치 summary_game['participants'][i]['timeline']['lane']
#아래 포문 세개를 통해 
#participantId_to_lanecamp
#	={participantId:[participantId,teamId,champId,lane,sommonerId],[동선정보{x,y}]}
participantId_to_summoner={}
for i in partitipantities_s_g:
	participantId_to_summoner[i['participantId']]=i['player']['summonerName']
participantId_to_lanechamp={}
participants_s_g=summary_game['participants']
for i in participants_s_g:
	participantId_to_lanechamp[i['participantId']] = [i['participantId'],i['teamId'],i['championId']]
for i in range(10):
	participantId_to_lanechamp[i+1].append(summary_game['participants'][i]['timeline']['lane'])
	participantId_to_lanechamp[i+1].append(participantId_to_summoner[i+1])

#print(participantId_to_lanechamp)


#타임라인
dongsun={}
timetest = requests.get("https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/"+str(gameId)+api_key).json()
for i in range(len(timetest['frames'])):
	for j in list(timetest['frames'][i]['participantFrames'].keys()):
		if j in list(dongsun.keys()):
			#position
			try:
				dongsun[j].append(timetest['frames'][i]['participantFrames'][j]['position'])
			except:
				pass
		else:
			dongsun[j]=[]
			dongsun[j].append(timetest['frames'][i]['participantFrames'][j]['position'])
plt.figure()
color_list = ['b','g','r','c','y','m','k','w']
for i in list(dongsun.keys()):
	#i번의 동선
	#print(i)
	participantId_to_lanechamp[int(i)].append([])
	#print('i=',i)
	for j in range(len(dongsun[i])):
		#print("i,j=",dongsun[i][j])
		participantId_to_lanechamp[int(i)][-1].append(dongsun[i][j])
		#dongsun[i][j] = i유저의 j타이밍에 좌표 {'x':xxx,'y':yyy} 
		#몇번유저 보여줄건지
		if int(i)!=-1:
			plt.scatter(dongsun[i][j]['x'],dongsun[i][j]['y'])
#plt.show()

#포지순서별, 팀별 정리
sorted_team=[]
posi=['TOP','JUNGLE','MIDDLE','BOTTOM','BOTTOM']
#어디에 넣을지 정하는 인덱스
index=0
#이미 쓴 키 빼두는 곳
used_index=[]
#used_index=[]랑 같은거같은데 모르겠음
already_searched=[]
#participantId_to_lanechamp의 키
ptlkey=list(participantId_to_lanechamp.keys())
#열번 ptlkey를 전부 돌리면 sorted_team len은 10이 되어야 정상
for t in range(10):
	if index==10:
		break
	for i in ptlkey:
		if i in already_searched:
			continue
		if index==10:
			break
		if index<5:
			if participantId_to_lanechamp[i][1]==100:
				if participantId_to_lanechamp[i][3]==posi[index]:
					sorted_team.append(participantId_to_lanechamp[i])
					already_searched.append(i)
					index+=1
					ptlkey.remove(i)
		else:
			if participantId_to_lanechamp[i][1]==200:
				if participantId_to_lanechamp[i][3]==posi[index-5]:
					sorted_team.append(participantId_to_lanechamp[i])
					index+=1
					ptlkey.remove(i)
#비정상포지션 즉, 열번 돌렸는데 sortedlist가 길이가 10이 아니었단것, 끝에 -1 추가
if len(sorted_team)<10:
	for i in range(len(ptlkey)):
		sorted_team.append(participantId_to_lanechamp[ptlkey[i]])
	sorted_team.append(-1)
#정상포지션
else:
	sorted_team.append(1)


for i in range(len(sorted_team)):
	print(sorted_team[i])