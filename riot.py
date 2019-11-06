import requests
import json
import operator
#챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
whole_champions=requests.get("http://ddragon.leagueoflegends.com/cdn/9.21.1/data/en_US/champion.json").json()

#챔피언정보, 최상위키는 챔피언이름,딕딕구조{Aatrox:{version:,id:'챔피언이름',key:'챔피언비밀아이디',name:'챔피언이름'}}
dict_champions_info=whole_champions['data']

#챔피언 이름만 모아놓은 리스트
all_champion_names=list(dict_champions_info.keys())

#암호화된 {챔피언아이디:챔피언이름}
champion_id_encrypted={}
#이포문 돌리면 모든챔피언 정보에 접근
for i in range(len(all_champion_names)):
	champion_id_encrypted[dict_champions_info[all_champion_names[i]]['key']]=all_champion_names[i]


summoner_name="opplk123"
url_front="https://kr.api.riotgames.com/"
api_key="?api_key=RGAPI-b6fb93ca-ecbe-4f5d-a233-9332456277ca"

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
combi_user_rankgame=requests.get(url_front+url_user_rankgame+user_id_encrypted+api_key).json()[1]
