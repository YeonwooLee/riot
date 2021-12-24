import requests
import json
import operator
import datetime
import time
from skimage import io  # 미니맵 처리
# from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import smtplib  # 메일을 보내기 위한 라이브러리 모듈
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
import pymysql
import sys
import threading
import subprocess
import locale


def input_timer(prompt, timeout_sec):
    class Local:
        # check if timeout occured
        _timeout_occured = False

        def on_timeout(self, process):
            self._timeout_occured = True
            process.kill()
            # clear stdin buffer (for linux)
            # when some keys hit and timeout occured before enter key press,
            # that input text passed to next input().
            # remove stdin buffer.
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except ImportError:
                # windows, just exit
                pass

        def input_timer_main(self, prompt_in, timeout_sec_in):
            # print with no new line
            print(prompt_in, end="")

            # print prompt_in immediately
            sys.stdout.flush()

            # new python input process create.
            # and print it for pass stdout
            cmd = [sys.executable, '-c', 'print(input())']
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                timer_proc = threading.Timer(timeout_sec_in, self.on_timeout, [proc])
                try:
                    # timer set
                    timer_proc.start()
                    stdout, stderr = proc.communicate()

                    # get stdout and trim new line character
                    result = stdout.decode(locale.getpreferredencoding()).strip("\r\n")
                finally:
                    # timeout clear
                    timer_proc.cancel()

            # timeout check
            if self._timeout_occured is True:
                # move the cursor to next line
                print("")
                raise TimeoutError
            return result

    t = Local()
    return t.input_timer_main(prompt, timeout_sec)


def ender():
    try:
        a = open("ender.txt", "r")
        a = a.readline()
        if "123" in a:
            sys.exit()
    except TimeoutError as e:
        # print("timeout...")
        pass
    except FileNotFoundError as ee:
        open("ender.txt", "w")


# 조합별 승률 db에 기입
def match_db(copy_thisgame):
    # 접속에 table_name 있으면 1, 없으면0 리턴
    f = open("db_password.txt", "r")
    db_password = f.readline()
    f.close()
    conn = pymysql.connect(host='localhost', user='root', password=db_password, db='lol_data', charset='utf8')
    cursor = conn.cursor()
    def table_exist(table_name):

        sql = '''SELECT EXISTS (
		SELECT 1 FROM Information_schema.tables 
		WHERE table_schema = 'lol_data' 
		AND table_name = \'{}\'
		) AS flag
		'''.format(table_name)

        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()

        return str(result[0][0])

    # 테이블생성
    def crt_tbl(table_name):

        # sql = sql.replace('\n',' ')
        # print(sql)

        sql = '''CREATE TABLE {tbn} ( 
		bot_combi VARCHAR(100) NOT NULL primary key, 
		whole INT NOT NULL, 
		win INT NOT NULL, 
		lose INT NOT NULL, 
		win_rate FLOAT NOT NULL) 
		'''.format(tbn=table_name)

        print(sql)

        cursor.execute(sql)
        # cursor.fetchall()
        conn.commit()

    # table_name에 combi_name 행 있는지? 있으면1 없으면 0 리턴
    def row_exist(table_name, combi_name):
        # sql = sql.replace('\n',' ')
        sql = "SELECT * FROM " + table_name + " where bot_combi= '{}'".format(combi_name)

        print(sql)


        cursor.execute(sql)
        result = cursor.fetchall()

        conn.commit()

        return str(len(result))

    # whole +=1, win_lose +=1, table_name은 기준팀, combi_data=상대팀 table_name테이블의 combi_data행을 수정함
    def update_lol(table_name, combi_data, win_lose):
        # combi_data = ('EZ_SN', 1, 0, 1)
        # sql = sql.replace('\n',' ')

        # print(sql)



        sql = "update " + table_name + " set whole=whole+1 where bot_combi=\'" + combi_data + "\'"
        cursor.execute(sql)

        if win_lose == 'win':
            sql = "update " + table_name + " set win=win+1 where bot_combi='" + combi_data + "'"
        else:
            sql = "update " + table_name + " set lose=lose+1 where bot_combi='" + combi_data + "'"
        cursor.execute(sql)

        sql = "update " + table_name + " set win_rate=round(win/whole*100,2) where bot_combi='" + combi_data + "'"
        cursor.execute(sql)
        # result = cursor.fetchall()
        conn.commit()


    # insert쿼리 수행
    # table_name에 처음 등장한 bot_combi 등록
    # new_bot_combi('test2','ct_mg','lose')
    def new_bot_combi(table_name, bot_combi, win_lose):
        # 레드팀 기입
        if win_lose == 'win':
            sql = '''insert into {tbl}(bot_combi,whole,win,lose,win_rate)
		  values('{b_comb}',{whole},{win},{lose},{winrate})'''.format(tbl=table_name, \
                                                                      b_comb=bot_combi, \
                                                                      whole=1, \
                                                                      win=1, \
                                                                      lose=0, \
                                                                      winrate=100)
        elif win_lose == 'lose':
            sql = '''insert into {tbl}(bot_combi,whole,win,lose,win_rate)
		  values('{b_comb}',{whole},{win},{lose},{winrate})'''.format(tbl=table_name, \
                                                                      b_comb=bot_combi, \
                                                                      whole=1, \
                                                                      win=0, \
                                                                      lose=1, \
                                                                      winrate=0)
        sql = sql.replace('\n', ' ')
        # print(sql)

        cursor.execute(sql)
        # cursor.fetchall()
        conn.commit()


    ##{한글챔명:영어챔명} 딕셔너리 반환, 내부 함수는 그거 만드는용
    def mk_ko_to_en(vesion):
        def phase1(version):

            # print('한글수집')
            # 챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
            # dict_keys(['type', 'format', 'version', 'data'])
            global keytochamp
            keytochamp = {}
            # 버전바뀔때마다 교체해줘야합니다. 적어도 신챔 나올때는 교체해줘야됩니다.
            # http://ddragon.leagueoflegends.com/cdn/10.2.1/data/ko_KR/champion.json -> http://ddragon.leagueoflegends.com/cdn/11.3.1/data/ko_KR/champion.json
            whole_champions = requests.get(
                "http://ddragon.leagueoflegends.com/cdn/" + version + ".1/data/ko_KR/champion.json").json()
            for champ in list(whole_champions['data'].keys()):
                keytochamp[whole_champions['data'][champ]['key']] = whole_champions['data'][champ]['name']

            # 시즌정보 / [{}]
            season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()

            # 큐타입정보[{}]
            # {'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
            queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()

            ###################여기까지기본정보받아오는곳
            return keytochamp

        def phase1_1(version):

            # print('영어수집')
            # 챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
            # dict_keys(['type', 'format', 'version', 'data'])
            global keytochamp
            keytochamp = {}
            # 버전바뀔때마다 교체해줘야합니다. 적어도 신챔 나올때는 교체해줘야됩니다.
            # http://ddragon.leagueoflegends.com/cdn/10.2.1/data/ko_KR/champion.json -> http://ddragon.leagueoflegends.com/cdn/11.3.1/data/ko_KR/champion.json
            whole_champions = requests.get(
                "http://ddragon.leagueoflegends.com/cdn/" + version + ".1/data/en_US/champion.json").json()
            for champ in list(whole_champions['data'].keys()):
                keytochamp[whole_champions['data'][champ]['key']] = whole_champions['data'][champ]['name']

            # 시즌정보 / [{}]
            season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()

            # 큐타입정보[{}]
            # {'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
            queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()

            ###################여기까지기본정보받아오는곳
            return keytochamp

        keytocham_en = phase1_1(vesion)
        keytochamp_ko = phase1(vesion)

        ko_to_eng = {}
        for i in keytochamp_ko.keys():
            ko_to_eng[keytochamp_ko[i]] = keytocham_en[i].upper().replace(" ", "")
        return ko_to_eng

    # 버전명 스트링
    strVer = copy_thisgame['version'].split('.')[0] + "_" + copy_thisgame['version'].split('.')[1]

    # 한국챔프명 영어로
    ko_to_en = mk_ko_to_en(copy_thisgame['version'])

    for i in ko_to_en.keys():
        if "'" in ko_to_en[i]:
            tempset = ko_to_en[i].replace("'", "")
            ko_to_en[i] = tempset
    # 테이블, 컬럼명으로 쓰일 제목 작성
    blue_comb = ko_to_en[copy_thisgame['team_blue']['adc']] + "_" + ko_to_en[
        copy_thisgame['team_blue']['sup']] + "_" + strVer
    red_comb = ko_to_en[copy_thisgame['team_red']['adc']] + "_" + ko_to_en[
        copy_thisgame['team_red']['sup']] + "_" + strVer

    nstr = "_" + strVer

    if table_exist("ALL_WINRATE" + nstr) == '0':
        crt_tbl("ALL_WINRATE" + nstr)
    # 승패팀 구분
    if copy_thisgame['winteam'] == 'red':
        winner = red_comb
        loser = blue_comb

    elif copy_thisgame['winteam'] == 'blue':
        winner = blue_comb
        loser = red_comb

    '''
				#승리팀 테이블 작성
				#1. 승리팀명 테이블 있음?
				if table_exist(winner)=='1':
					#승리팀명 테이블 있으면 승리팀명 테이블에 패배팀명 row도 있냐?
					if row_exist(winner,loser)=='1':
						#승팀테이블에 패팀row 있으면 승리팀.패배팀 update
						update_lol(winner,loser,'win')
					else:
						#승팀테이블에 패팀row 없으면 승리팀.패배팀 작성
						new_enemy_combi(winner,loser,'win')
				#승팀명 테이블 없으면
				else:
					#승팀명 테이블 작성
					crt_tbl(winner)
					#승팀.패팀 row 작성
					new_enemy_combi(winner,loser,'win')
			'''

    if row_exist("ALL_WINRATE" + nstr, winner) == '1':
        update_lol("ALL_WINRATE" + nstr, winner, 'win')
    else:
        new_bot_combi("ALL_WINRATE" + nstr, winner, 'win')

    # 패배팀 테이블 작성
    # 1. 패배팀명 테이블 있음?
    '''if table_exist(loser)=='1':
					#패배팀명 테이블 있으면 패배팀명 테이블에 승리팀명 row도 있냐?
					if row_exist(loser,winner)=='1':
						#패팀테이블에 승팀row 있으면 패배팀.승리팀 update
						update_lol(loser,winner,'lose')
					else:
						#패팀테이블에 승팀row 없으면 패팀.승팀 작성
						new_enemy_combi(loser,winner,'lose')
				#패팀명 테이블 없으면
				else:
					#패팀명 테이블 작성
					crt_tbl(loser)
					#패팀.승팀 row 작성
					new_enemy_combi(loser,winner,'lose')
			'''
    if row_exist("ALL_WINRATE" + nstr, loser) == '1':
        update_lol("ALL_WINRATE" + nstr, loser, 'lose')
    else:
        new_bot_combi("ALL_WINRATE" + nstr, loser, 'lose')

    cursor.close()
    conn.close()




def new_before_insert_oracle(temp_data):
    # 승패 변수 기입
    f = open("db_password.txt", "r")
    db_password = f.readline()
    f.close()

    conn = pymysql.connect(host='localhost', user='root', password=db_password, db='lol_data', charset='utf8')

    cursor = conn.cursor()

    if temp_data["winteam"] == 'red':
        red_win = '1'
        blue_win = '0'
    elif temp_data['winteam'] == 'blue':
        blue_win = '1'
        red_win = '0'
    else:
        red_win = '-1'
        blue_win = '-1'

    # 레드팀 기입
    sql = '''insert into lol_red(gameid, win, top, jungle, mid, adc, sup)
	values('{gameid}','{win}','{top}','{jungle}','{mid}','{adc}','{sup}')'''.format(gameid=temp_data['gameid'], \
                                                                                    win=red_win, \
                                                                                    top=temp_data['team_red']['top'],
                                                                                    jungle=temp_data['team_red'][
                                                                                        'jungle'],
                                                                                    mid=temp_data['team_red']['mid'],
                                                                                    adc=temp_data['team_red']['adc'],
                                                                                    sup=temp_data['team_red']['sup'])

    #mydb_insert(sql)
    sql = sql.replace('\n', ' ')
    # print(sql)

    cursor.execute(sql)
    # cursor.fetchall()
    conn.commit()


    # 블루팀 기입
    sql = '''insert into lol_blue(gameid, win, top, jungle, mid, adc, sup)
	values('{gameid}','{win}','{top}','{jungle}','{mid}','{adc}','{sup}')'''.format(gameid=temp_data['gameid'], \
                                                                                    win=blue_win, \
                                                                                    top=temp_data['team_blue']['top'],
                                                                                    jungle=temp_data['team_blue'][
                                                                                        'jungle'],
                                                                                    mid=temp_data['team_blue']['mid'],
                                                                                    adc=temp_data['team_blue']['adc'],
                                                                                    sup=temp_data['team_blue']['sup'])

    #mydb_insert(sql)
    sql = sql.replace('\n', ' ')
    # print(sql)

    cursor.execute(sql)
    # cursor.fetchall()
    conn.commit()


    # 시간,버전 기입
    sql = '''insert into lol_time_v(gameid, start_time, version)
	values('{gameid}',{start_time},'{version}')'''.format(gameid=temp_data['gameid'], \
                                                          start_time=temp_data['gamestart_e_millisecond'], \
                                                          version=temp_data['version'])
    #mydb_insert(sql)
    sql = sql.replace('\n', ' ')
    # print(sql)

    cursor.execute(sql)
    # cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

telgm_token = '1925566531:AAElSg-wydMKDBdCcH0JlPJAIKd5fzr7W1I'
bot = telegram.Bot(token=telgm_token)


# 텔레그램
def telegram_sendMSG(chatId, msg):
    # print("메세지대리")
    # 테스트후 해제 주석
    bot.sendMessage(chat_id=chatId, text=msg)


def send_all_ids(msg):
    ids = {"연우": "1993842151", "재구": "747977556", "태양": '2048880707'}
    for id in ids.keys():
        telegram_sendMSG(ids[id], msg)


# 날짜 -> 에포크밀리초 (시간은 롤 패치 종료시간인 오전10시 고정해둠)
def date_to_millisecond(start_day):
    start_day = start_day.split('-')
    year = int(start_day[0])
    month = int(start_day[1])
    day = int(start_day[2])

    '''
	dt_obj = datetime.strptime('25.8.2021 22:00:00,00',
	                           '%d.%m.%Y %H:%M:%S,%f')
	                         '''

    dt_obj = datetime.datetime.strptime("{}.{}.{} 10:00:00,00".format(day, month, year), '%d.%m.%Y %H:%M:%S,%f')
    millisec = dt_obj.timestamp() * 1000

    return int(millisec)


# 동일디렉터리에 있는 api_key.txt에서 api사용에 필요한 key 읽어옴
# 프로그램 초기 실행시 or 실행도중 키 만료되서 교체해야될 때 쓰임
def getkey():
    f = open('api_key.txt', 'r')
    key = f.readline()[:-2]
    f.close()
    return key


# quit_sign: api에 요청멈춰야하는 경우 1로 바뀜
# 처음 실행시 0
quit_sign = 0
# 처음 실행시 메모장에 있는 key 가져옴
api_key = getkey()


# get_key_from_mail과 세트입니다. 메일을 읽들 때 사용됩니다.
# https://oceancoding.blogspot.com/2019/11/imap.html
def findEncodingInfo(txt):
    info = email.header.decode_header(txt)
    s, encoding = info[0]
    return s, encoding


# 집에 켜두는 자료수집용 컴퓨터의 key 교체에 사용됩니다. 제가 메일로 보내준 새 api-key로 기존 api-key를 변경합니다.
def get_key_from_mail():
    global api_key
    sendto = 'jyanoos1993@gmail.com'
    user = 'jyanoos1993@gmail.com'
    f = open("gmail_password.txt", "r")
    password = f.readline()
    f.close()
    #password = "ytttqzpiakaturft"

    # 메일서버 로그인
    imapsrv = "smtp.gmail.com"
	# 아래행 imap = imaplib.IMAP4_SSL('imap.gmail.com')에서 수정하니까 작동됨/원리는 모름/우연
    imap = imaplib.IMAP4_SSL(imapsrv, "993")
    id = user
    pw = password
    imap.login(id, pw)

    # 받은 편지함
    imap.select('inbox')

    # 받은 편지함 모든 메일 검색
    resp, data = imap.uid('search', None, 'All')

    # 여러 메일 읽기 (반복)
    all_email = data[0].split()
    all_email.reverse()
	# del(all_email[0])
    for mail in all_email:

        # fetch 명령을 통해서 메일 가져오기 (RFC822 Protocol)
        result, data = imap.uid('fetch', mail, '(RFC822)')

        # 사람이 읽기 힘든 Raw 메세지 (byte)
        raw_email = data[0][1]

        # 메시지 처리(email 모듈 활용)
        email_message = email.message_from_bytes(raw_email)

        # 이메일 정보 keys
		# print(email_message.keys())
		# print('FROM:', email_message['From'])
		# print('SENDER:', email_message['Sender'])
		# print('TO:', email_message['To'])
		# print('DATE:', email_message['Date'])

        b, encode = findEncodingInfo(email_message['Subject'])
		# 제목
		# print('SUBJECT:', str(b, encode))
        subject = str(b, encode)
        if subject != 'riotapikey':
            # print(subject)
            return 0
        text = ''
		# 이메일 본문 내용 확인
		# print('[CONTENT]')
		# print('='*80)
        if email_message.is_multipart():
            for part in email_message.get_payload():
                bytes = part.get_payload(decode=True)
                encode = part.get_content_charset()
                # print(str(bytes, encode))
                text = str(bytes, encode)
                break
		# print('='*80)
        break

    imap.close()
    imap.logout()
    f = open('api_key.txt', 'r')
    existing = f.readline()
    f.close()

    if existing != text:
        f = open('api_key.txt', 'w')
        f.write(text)
        f.close()
        print(existing[:-2], '----->', text[:-2], 'key 교체 완료')
        api_key = getkey()
        return 1
    return 0


# 수집한 데이터를 제 이메일로 백업합니다. 자료수집용 컴퓨터의 key가 만료된다면 저에게 이메일을 보내 key가 만료되었음을 알립니다.
# 자료수집용 컴퓨터가 메일을 보내면 다시 제 메일로 새 api-key를 보내주고 get_key_from_mail이 그 메일을 읽어 key를 교체하는 방식입니다
# https://wikidocs.net/36465
def send_final():
    sendEmail = "jyanoos1993@gmail.com"
    recvEmail = "fox_93@naver.com"

    f = open("gmail_password.txt", "r")
    password = f.readline()
    f.close()
    # password = "ytttqzpiakaturft"
    smtpName = "smtp.gmail.com"
    smtpPort = 587

    # 여러 MIME을 넣기위한 MIMEMultipart 객체 생성
    msg = MIMEMultipart()

    msg['Subject'] = "롤 본컴 접속 끊김"
    msg['From'] = sendEmail
    msg['To'] = recvEmail

    # 본문 추가
    text = "."
    contentPart = MIMEText(text)  # MIMEText(text , _charset = "utf8")
    msg.attach(contentPart)

    # 파일 추가
    etcFileName = ffiname + 'new_before.json'
    with open(etcFileName, 'rb') as etcFD:
        etcPart = MIMEApplication(etcFD.read())
        # 첨부파일의 정보를 헤더로 추가
        etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
        msg.attach(etcPart)
    # 파일 추가
    etcFileName = ffiname + 'gameids.json'
    with open(etcFileName, 'rb') as etcFD:
        etcPart = MIMEApplication(etcFD.read())
        # 첨부파일의 정보를 헤더로 추가
        etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
        msg.attach(etcPart)

    etcFileName = ffiname + 'backup_gameids.json'
    with open(etcFileName, 'rb') as etcFD:
        etcPart = MIMEApplication(etcFD.read())
        # 첨부파일의 정보를 헤더로 추가
        etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
        msg.attach(etcPart)

    etcFileName = ffiname + 'backup_new_before.json'
    with open(etcFileName, 'rb') as etcFD:
        etcPart = MIMEApplication(etcFD.read())
        # 첨부파일의 정보를 헤더로 추가
        etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
        msg.attach(etcPart)

    s = smtplib.SMTP(smtpName, smtpPort)
    s.starttls()
    s.login(sendEmail, password)
    s.sendmail(sendEmail, recvEmail, msg.as_string())
    s.close()


# 아래 두 함수 load_json과 write_json은 딕셔너리, 리스트 같은 것들을 그 자체로 저장하고 읽을 수 있습니다.
# 가령 dict_a={}를 텍스트'dict_a={}'가 아닌 dict_a={} 그 자체로 저장하고 읽을 수 있습니다.
# 이걸 쓰면 큰 데이터들을 미리 모아두고 코드에서 읽어서 바로 딕셔너리로 사용할 수 있습니다
def load_json(filename):
    file = pathlib.Path(str(filename) + '.json')
    file_text = file.read_text(encoding='utf-8-sig')
    return json.loads(file_text)


def write_json(filename, data):
    with open(str(filename) + '.json', 'w', encoding='UTF-8-sig') as file:
        file.write(json.dumps(data, ensure_ascii=False))


# riot API에 요청이 필요할때 사용했습니다.
# url에 해당하는 자료를 요청하고 자주 발생하는 문제인 429(요청제한초과)나 403(key만료)의 처리를 합니다
def req_api(url):
    global quit_sign
    global api_key
    response = requests.get(url)

    # 반응이 200이 아니면 뭔가 잘못된 것입니다.
    if str(response) != '<Response [200]>':
        if str(response) == '<Response [429]>':
            # time.sleep(600)
            print(response)
            time.sleep(600)
            return -1
        elif str(response) == '<Response [403]>':
            print('403이다!!!!!!!!!!!!!!!!!!!!!!!!!')
            now = datetime.datetime.now()
            print('403발생시각:', now)
            quit_sign = 1
            write_json('quit_sign', 1)
            send_final()
            return 0
        else:
            print(response)
            time.sleep(10)
            return 0
    # 반응이 200이면 정상입니다.
    else:
        # time.sleep(0.1)
        return response.json()


# 챔피언, 시즌, 큐타입 등 롤에대한 기본적인 정보를 가져옵니다.
# keytochamp={챔피언key:챔피언이름}
def phase1(version):
    print('롤 기본 데이터 수집')
    # 챔피언 이상한 정보도 들어있는 드래곤 딕딕딕구조 {키:{},키:{}}
    # dict_keys(['type', 'format', 'version', 'data'])
    global keytochamp
    keytochamp = {}
    # 버전바뀔때마다 교체해줘야합니다. 적어도 신챔 나올때는 교체해줘야됩니다.
    # http://ddragon.leagueoflegends.com/cdn/10.2.1/data/ko_KR/champion.json -> http://ddragon.leagueoflegends.com/cdn/11.3.1/data/ko_KR/champion.json
    whole_champions = requests.get(
        "http://ddragon.leagueoflegends.com/cdn/" + version + ".1/data/ko_KR/champion.json").json()
    for champ in list(whole_champions['data'].keys()):
        keytochamp[whole_champions['data'][champ]['key']] = whole_champions['data'][champ]['name']

    # 시즌정보 / [{}]
    season_data = requests.get("http://static.developer.riotgames.com/docs/lol/seasons.json").json()

    # 큐타입정보[{}]
    # {'queueId': 420, 'map': "Summoner's Rift", 'description': '5v5 Ranked Solo games'}
    queqe_data = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()


###################여기까지기본정보받아오는곳


# 2021-02-11 기준 사용되지 않는 함수입니다
# {'summonerName': 'OustLikeThatKR', 'summonerId': 'Q3J3Ckb00FXqFBnlfuebEeQnC8aj9ji0Deth5_Fvv79iL0w', 'leagueId': 'd7a55ac9-9ee5-4904-9177-ebc3e398badd'}
# tier = GOLD,PLATINUM ...
# division = I,II ...
# page = page // 페이지당 205명
def get_tier_group(tier, division, page):
    global api_key
    url = 'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + '/' + division + '?page=' + page + '&api_key=' + api_key
    base_data = req_api(url)

    result_list = []
    for i in range(len(base_data)):
        realdata = {'summonerName': base_data[i]['summonerName'], 'summonerId': base_data[i]['summonerId'],
                    'leagueId': base_data[i]['leagueId']}
        result_list.append(realdata)
    return result_list


# print(get_tier_group('GOLD',"I","1")[0])


# 2021-02-11 기준 사용되지 않는 함수입니다
# 이 리그에는 티어1234가 랜덤으로 배정돼있다.
# 누누의 태극전사들 이런거임, 길이 랜덤 약 140개
def get_league(leagueId):
    global api_key
    url = 'https://kr.api.riotgames.com/lol/league/v4/leagues/' + leagueId + '?api_key=' + api_key
    base_data = req_api(url)['entries']

    result_list = []

    for i in range(len(base_data)):
        realdata = {}
        realdata['summonerName'] = base_data[i]['summonerName']
        realdata['summonerId'] = base_data[i]['summonerId']
        result_list.append(realdata)

    return result_list


# 계정의 게임아이디를 accountId로 바꿉니다
# 가령 우주짱짱맨 -> ABCD-1234-ASDF 이런식입니다
# accountId가 있어야 해당 계정의 게임 내역을 가져올 수 있습니다.
def summonerName_to_accountId(summonerName):
    # print(summonerName,'의 accountId 요청')
    global api_key
    url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName + '?api_key=' + api_key
    base_data = req_api(url)
    return base_data['accountId']


def summonerName_to_puuid(summonerName):
    # print(summonerName,'의 accountId 요청')
    global api_key
    url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName + '?api_key=' + api_key
    base_data = req_api(url)
    return base_data['puuid']


# 계정의 accountId를 인자로 받고 최근 게임의 gameid를 리턴합니다.
# 최근 게임이어도 이번 패치 버전 이전의 게임이라면 "얘꺼다봄"을 출력하고 넘어갑니다.
def from_accountId_get_gameid(accountId, start_day):
    # https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/IYo8nRoG9IdDHXb6nG-_h8s9gXrF1aw-P8iQ3Jv2NHFZFSqbcLRAEwQSACq_EG33qwPqXWabLiG8oQ/ids?endTime=1632272400000&queue=420&start=0&count=20
    # print('gameid 가져오는중')
    # url = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/'+accountId+'?queue=420&endIndex='+str(endindex)+'&beginIndex='+str(beginindex)+'&api_key='+api_key
    url = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId + '?queue=420&api_key=' + api_key

    # gameids.json이 이미 있다면 가져오고 없다면 생성하여 가져옵니다. 중복자료 처리에 사용됩니다.
    try:
        gameids = load_json(ffiname + 'gameids')
    except:
        write_json(ffiname + 'gameids', [])
        gameids = load_json(ffiname + 'gameids')

    data = req_api(url)
    if data != 0 and data != -1:
        # 계정의 게임 기록들은 data라는 dict의 'matches'라는 key로 접근합니다
        for i in range(len(data['matches'])):
            gameid = data['matches'][i]['gameId']
            # 5대5 게임인점, 유저를 먼저 모으고 각 유저의 게임기록을 살펴보는점 때문에 이미 조사한 게임이 중복되서 들어오는 경우가 생깁니다.
            # gameids.json은 그런 문제를 해결합니다. 이미 gameids에 있는 gameid라면 continue합니다.
            if gameid in gameids:
                continue
            else:
                # 중복자료가 아니고 이번 버전에서 행해진 게임이라면 gameids에 기록하여 다음 중복자료 탐색에 사용하고  str타입으로 gameid를 리턴합니다.
                # gameid는 여러개 받아와도 하나만 사용하는 이유는 최대한 다양한 유저의 자료를 사용해야 치우침이 없을 것 같았습니다.
                gameids.append(gameid)
                write_json(ffiname + 'gameids', gameids)
                # 매 패치마다 수정해야하는 부분입니다. 에포크밀리초로 지난 패치시점의 게임기록은 기록하지 않습니다.
                # https://www.epochconverter.com/
                if data['matches'][i]['timestamp'] < date_to_millisecond(start_day):
                    print(data['matches'][i]['timestamp'], date_to_millisecond(start_day))
                    print("얘꺼 이번패치 기록 끝")
                    return 3
                else:
                    print("게임아이디 수집 완료")
                    return str(gameid)
        else:
            print("얘꺼다봄######################################################")
            return 0
    else:
        return 0


# 계정의 accountId를 인자로 받고 최근 게임의 gameid를 리턴합니다.
# 최근 게임이어도 이번 패치 버전 이전의 게임이라면 "얘꺼다봄"을 출력하고 넘어갑니다.
# url 맨 뒤에 보면 count있음 20개만 가져옴
def from_puuid_get_gameid(puuid, start_day):
    start_day = str(date_to_millisecond(start_day))
    # url='https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?endTime='+start_day+'&queue=420&start=0&count=20&api_key='+api_key
    # url='https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?endTime='+start_day+'&queue=420&start=0&count=20&api_key='+api_key
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/' + puuid + '/ids?queue=420&start=0&count=20&api_key=' + api_key
    # print('gameid 가져오는중')
    # url = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/'+accountId+'?queue=420&endIndex='+str(endindex)+'&beginIndex='+str(beginindex)+'&api_key='+api_key
    # url ='https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/'+accountId+'?queue=420&api_key='+api_key

    # gameids.json이 이미 있다면 가져오고 없다면 생성하여 가져옵니다. 중복자료 처리에 사용됩니다.
    try:
        gameids = load_json(ffiname + 'gameids')
    except:
        write_json(ffiname + 'gameids', [])
        gameids = load_json(ffiname + 'gameids')

    data = req_api(url)
    # print(data)
    if len(data) > 0:
        # 계정의 게임 기록들은 data라는 dict의 'matches'라는 key로 접근합니다
        for i in data:
            gameid = i
            # 5대5 게임인점, 유저를 먼저 모으고 각 유저의 게임기록을 살펴보는점 때문에 이미 조사한 게임이 중복되서 들어오는 경우가 생깁니다.
            # gameids.json은 그런 문제를 해결합니다. 이미 gameids에 있는 gameid라면 continue합니다.
            if gameid in gameids:
                continue
            url_for_time_check = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '?api_key=' + api_key
            game_start_time = req_api(url_for_time_check)["info"]["gameCreation"]
            # print(game_start_time,"<<<game_start_time",type(game_start_time))
            # print(start_day,"<<<<<<start_day",type(start_day))
            if game_start_time < int(start_day):
                print("얘꺼 이번패치 다봄")
                return 0
            else:
                # 중복자료가 아니고 이번 버전에서 행해진 게임이라면 gameids에 기록하여 다음 중복자료 탐색에 사용하고  str타입으로 gameid를 리턴합니다.
                # gameid는 여러개 받아와도 하나만 사용하는 이유는 최대한 다양한 유저의 자료를 사용해야 치우침이 없을 것 같았습니다.
                gameids.append(gameid)
                write_json(ffiname + 'gameids', gameids)
                # 매 패치마다 수정해야하는 부분입니다. 에포크밀리초로 지난 패치시점의 게임기록은 기록하지 않습니다.
                # https://www.epochconverter.com/
                global gst
                gst = game_start_time
                return str(gameid)
        else:
            print("얘꺼다봄######################################################")
            return 0
    else:
        print("패치시점(start_day)이후 게임 기록 없는 계정임")
        return 0


# gameids를 인자로 받아 해당 gameid를 가진 판에서 누가 원딜이었고 누가 서폿이었는지 반환합니다.
# 아래 get_bottom_final과 get_bottom_full과 세트입니다.
# get_bottom_full은 보기 편하려고 만들었습니다.
# 라인전이 이뤄지는 15분 정도까지의 각 플레이어의 시간대별 위치 좌표를 받고
# 바텀에 있으면 bot_point를 1올려 bot_point가 가장 높은 사람 둘이 바텀 라이너들이라고 정하는 방식입니다
# 원딜과 서폿의 구분은 씨에스의 양으로 구분했습니다.
# 바텀 뿐만 아니라 탑, 미드, 정글 등도 같은 원리로 구분했습니다.
# 정글 구분이 힘들었는데 15분까지 정글 몬스터를 가장 많이 잡은 유저를 정글러로 분류했습니다.
def get_bottom_base(gameid):
    # print('phase5')
    global api_key
    # 일단 데이터 요청
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '/timeline?api_key=' + api_key
    # position = req_api(url)
    # position['info']['frames']에 시간별 위치정보 들어있음
    frames = position['info']['frames']
    dongsun = {}
    # participantid는 게임내 참여자 참가번호같은거
    # dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
    for frame in frames:
        # print(frame['timestamp'])
        partiframe = frame['participantFrames']
        for pf in list(partiframe.keys()):
            participantid = str(partiframe[pf]['participantId'])
            if participantid not in dongsun.keys():
                dongsun[participantid] = []
            if 'position' not in partiframe[pf].keys():
                continue
            # print(pf,partiframe[pf]['position'])
            dongsun[participantid].append(partiframe[pf]['position'])

    # 여기부터 ptl.show()까지 시각화
    # for i in range(1,11):
    #	i=str(i)
    #	for j in dongsun[i]:
    #		if i=='3':
    #			plt.scatter(j['x'],j['y'],c='b')
    #		elif i=='10':
    #			plt.scatter(j['x'],j['y'],c='b')
    #		else:
    #			plt.scatter(j['x'],j['y'],c='b')
    #
    # plt.show()

    # member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
    member = []
    # i는 participantid
    for i in range(1, 11):
        i = str(i)
        # i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
        botpoint = 0
        # botpoint의 반대
        elsepoint = 0
        # 몇분시점인지 count로 체크
        count = 0
        # dongsun[i][j]는 j시점 i번 플레이어의 위치
        for j in dongsun[i]:
            count += 1
            # 15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
            if count > 12:
                break
            # 바텀좌표에 있었으면 botpoint에 +1
            if (j['x'] > 10000 and j['y'] < 5000) or (j['x'] < 10000 and j['y'] < 2000) or (
                    j['x'] > 13000 and j['y'] > 0):
                botpoint += 1
            else:
                elsepoint += 1
        # 이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
        member.append([botpoint, botpoint - elsepoint, i])
    # member를 botpoint 기준으로 오름차순 정렬
    member.sort()
    # 결과에 get_bot()함수의 인자인 gameid 넣어두고
    result = [gameid]
    # botpoint 상위 네명의 participantid를 result에 넣는다
    # pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
    # 결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다
    for i in range(4):
        result.append(member.pop()[-1])
    if len(result) != 5:
        return 0
    check = result[1:]
    frame = frames[-1]
    participantFrames = frame['participantFrames']
    know_cs = {}
    for pf in participantFrames.keys():
        for pid in check:
            if str(participantFrames[pf]['participantId']) == pid:
                # 봇과 봇씨에스가 맞게 나오나 보려면 해제
                # print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
                know_cs[pid] = participantFrames[pf]['minionsKilled'] + participantFrames[pf]['jungleMinionsKilled']

    return result, know_cs


def get_botttom_final(bot):
    # print('phase6')
    # gameid는 gameid에
    gameid = bot[0][0]
    # 여기부터 서폿둘 원딜둘 따로나누는부분
    botcombi = bot[1]
    bot = []
    for i in botcombi.keys():
        bot.append([botcombi[i], i])
    bot.sort()
    supports = bot[:2]
    adcs = bot[2:]
    # 여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

    # url = 'https://asia.api.riotgames.com/lol/match/v5/matches/'+gameid+'?api_key='+api_key
    # data = req_api(url)
    data = ffdata

    teama = data['teams'][0]
    teamb = data['teams'][1]

    ###승리팀구분, 한쪽만 이기지않으면 오류
    # 승리팀들어갈곳
    winteam = 0
    if (teama['win'] == False and teamb['win'] == True) or (teama['win'] == True and teamb['win'] == False):
        if teama['win'] == True:
            winteam = teama['teamId']
        else:
            winteam = teamb['teamId']

    else:
        return 0
    ###
    adc_result = []
    for adc in adcs:
        pid = adc[1]
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                adc_result.append([pt['teamId'], keytochamp[str(pt['championId'])]])
    spt_result = []
    for spt in supports:
        pid = spt[1]
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                spt_result.append([pt['teamId'], keytochamp[str(pt['championId'])]])
    lastdata = []
    for i in adc_result:
        if i[0] == 100:
            lastdata.append(i)
    for i in spt_result:
        if i[0] == 100:
            lastdata.append(i)

    for i in adc_result:
        if i[0] == 200:
            lastdata.append(i)
    for i in spt_result:
        if i[0] == 200:
            lastdata.append(i)
    lastdata.append(winteam)
    t1 = 0
    t2 = 0
    for i in lastdata[:-1]:
        if i[0] == 100:
            t1 += 1
        elif i[0] == 200:
            t2 += 1
        else:
            print('이상 팀 정보')
            return 0
    if t1 != 2 or t2 != 2:
        print('이상 팀 정보')
        return 0
    if lastdata[-1] != 100 and lastdata[-1] != 200:
        print('이상 팀 정보')
        return 0

    return lastdata


def get_bottom_full(gameid):
    # print('바텀 정보 분석중')
    return get_botttom_final(get_bottom_base(gameid))


# 아래 new_phase6(),  mid_phase6(), get_mid_full과 세트입니다 원리는 get_bot 세트와 같습니다
def new_phase5(gameid):
    # print('phase5')
    global api_key
    # 일단 데이터 요청
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '/timeline?api_key=' + api_key
    # position = req_api(url)
    # position['info']['frames']에 시간별 위치정보 들어있음
    frames = position['info']['frames']
    dongsun = {}
    # participantid는 게임내 참여자 참가번호같은거
    # dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
    frame = frames[5]
    participantFrames = frame['participantFrames']
    know_cs = {}
    members = []
    for pf in participantFrames.keys():
        members.append([participantFrames[pf]['jungleMinionsKilled'], participantFrames[pf]['participantId']])
    members.sort()
    result = members[-2:]
    return [[gameid], result]


def new_phase6(bot):
    # print('phase6')
    # gameid는 gameid에
    gameid = bot[0][0]
    # 여기부터 서폿둘 원딜둘 따로나누는부분
    botcombi = bot[1]

    bot = [str(botcombi[0][1]), str(botcombi[1][1])]

    # 여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '?api_key=' + api_key
    # data = req_api(url)
    data = ffdata
    teama = data['teams'][0]
    teamb = data['teams'][1]

    ###승리팀구분, 한쪽만 이기지않으면 오류
    # 승리팀들어갈곳
    winteam = 0
    if (teama['win'] == False and teamb['win'] == True) or (teama['win'] == True and teamb['win'] == False):
        if teama['win'] == True:
            winteam = teama['teamId']
        else:
            winteam = teamb['teamId']

    else:
        # print(teama,"<<teamajg\n")
        # print(teamb,"<<teamb")
        return 0

    ###
    lastdata = []
    for jg in bot:
        pid = jg
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                lastdata.append([pt['teamId'], keytochamp[str(pt['championId'])]])

    lastdata.append(winteam)
    if lastdata[0][0] == 200:
        temp = lastdata[0]
        lastdata[0] = lastdata[1]
        lastdata[1] = temp
    t1 = 0
    t2 = 0
    for i in lastdata[:-1]:
        if i[0] == 100:
            t1 += 1
        elif i[0] == 200:
            t2 += 1
        else:
            print('이상 팀 정보1')
            return 0
    if t1 != 1 or t2 != 1:
        print('이상 팀 정보2')
        return 0
    if lastdata[-1] != 100 and lastdata[-1] != 200:
        print('이상 팀 정보3')
        return 0
    # print(lastdata,'<<now')
    return lastdata


# 아래 mid_phase6(), get_mid_full과 세트입니다 원리는 get_bot 세트와 같습니다
def mid_phase5(gameid):
    # print('phase5')
    global api_key
    # 일단 데이터 요청
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '/timeline?api_key=' + api_key
    # position = req_api(url)
    # position['info']['frames']에 시간별 위치정보 들어있음
    frames = position['info']['frames']
    dongsun = {}
    # participantid는 게임내 참여자 참가번호같은거
    # dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
    for frame in frames:
        # print(frame['timestamp'])
        partiframe = frame['participantFrames']
        for pf in list(partiframe.keys()):
            participantid = str(partiframe[pf]['participantId'])
            if participantid not in dongsun.keys():
                dongsun[participantid] = []
            if 'position' not in partiframe[pf].keys():
                continue
            # print(pf,partiframe[pf]['position'])
            dongsun[participantid].append(partiframe[pf]['position'])

    # 여기부터 ptl.show()까지 시각화
    # for i in range(1,11):
    #	i=str(i)
    #	for j in dongsun[i]:
    #		if i=='3':
    #			plt.scatter(j['x'],j['y'],c='b')
    #		elif i=='10':
    #			plt.scatter(j['x'],j['y'],c='b')
    #		else:
    #			plt.scatter(j['x'],j['y'],c='b')
    #
    # plt.show()

    # member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
    member = []
    # i는 participantid
    for i in range(1, 11):
        i = str(i)
        # i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
        botpoint = 0
        # botpoint의 반대
        elsepoint = 0
        # 몇분시점인지 count로 체크
        count = 0
        # dongsun[i][j]는 j시점 i번 플레이어의 위치
        for j in dongsun[i]:
            count += 1
            # 15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
            if count > 10:
                break
            # 바텀좌표에 있었으면 botpoint에 +1
            if (j['x'] > 6000 and j['x'] < 8000) and (j['y'] > 7000 and j['y'] < 8000):
                botpoint += 1
            else:
                elsepoint += 1
        # 이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
        member.append([botpoint, botpoint - elsepoint, i])
    # member를 botpoint 기준으로 오름차순 정렬
    member.sort()
    # 결과에 get_bot()함수의 인자인 gameid 넣어두고
    result = [gameid]
    # botpoint 상위 네명의 participantid를 result에 넣는다
    # pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
    # 결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다
    for i in range(2):
        result.append(member.pop()[-1])
    if len(result) != 3:
        return 0
    check = result[1:]
    frame = frames[-1]
    participantFrames = frame['participantFrames']
    know_cs = {}
    for pf in participantFrames.keys():
        for pid in check:
            if str(participantFrames[pf]['participantId']) == pid:
                # 봇과 봇씨에스가 맞게 나오나 보려면 해제
                # print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
                know_cs[pid] = participantFrames[pf]['minionsKilled'] + participantFrames[pf]['jungleMinionsKilled']
    return result, know_cs


def mid_phase6(bot):
    # print(bot,"<<mid")
    # exit()
    # print('phase6')
    # gameid는 gameid에
    gameid = bot[0][0]
    # 여기부터 서폿둘 원딜둘 따로나누는부분
    jglist = new_phase6(new_phase5(gameid))
    botcombi = bot[1]
    bot = []
    for i in botcombi.keys():
        bot.append([botcombi[i], i])
    bot.sort()
    supports = bot[:1]
    adcs = bot[1:]
    # 여기까지 서폿둘 원딜둘 따로나눔, 이상자료면 원딜 여러명될수도있음

    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '?api_key=' + api_key
    # data = req_api(url)
    data = ffdata
    teama = data['teams'][0]
    teamb = data['teams'][1]

    ###승리팀구분, 한쪽만 이기지않으면 오류
    # 승리팀들어갈곳
    winteam = 0
    if (teama['win'] == False and teamb['win'] == True) or (teama['win'] == True and teamb['win'] == False):
        if teama['win'] == True:
            winteam = teama['teamId']
        else:
            winteam = teamb['teamId']

    else:
        return 0
    ###
    adc_result = []
    for adc in adcs:
        pid = adc[1]
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                adc_result.append([pt['teamId'], keytochamp[str(pt['championId'])]])
    spt_result = []
    for spt in supports:
        pid = spt[1]
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                spt_result.append([pt['teamId'], keytochamp[str(pt['championId'])]])
    lastdata = []
    for i in adc_result:
        if i[0] == 100:
            lastdata.append(i)
    for i in spt_result:
        if i[0] == 100:
            lastdata.append(i)

    for i in adc_result:
        if i[0] == 200:
            lastdata.append(i)
    for i in spt_result:
        if i[0] == 200:
            lastdata.append(i)
    lastdata.append(winteam)
    t1 = 0
    t2 = 0
    for i in lastdata[:-1]:
        if i[0] == 100:
            t1 += 1
        elif i[0] == 200:
            t2 += 1
        else:
            print('이상 팀 정보')
            return 0
    if t1 != 1 or t2 != 1:
        print('이상 팀 정보')
        return 0
    if lastdata[-1] != 100 and lastdata[-1] != 200:
        print('이상 팀 정보')
        return 0

    lastdata.insert(1, jglist[0])
    lastdata.insert(3, jglist[1])

    return lastdata


def get_mid_full(gameid):
    # print('미드 정보 분석중')
    return mid_phase6(mid_phase5(gameid))


# jyanoos
# jyanoos2
# 아래 get_top_final(), get_top_full과 세트입니다 원리는 get_bot 세트와 같습니다
def get_top_base(gameid):
    # print('phase5')
    global api_key
    # 일단 데이터 요청
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '/timeline?api_key=' + api_key
    # position = req_api(url)
    # position['info']['frames']에 시간별 위치정보 들어있음
    frames = position['info']['frames']
    dongsun = {}
    # participantid는 게임내 참여자 참가번호같은거
    # dongsun['participantid'] ={1분:x,y, 2분:x,y} 이런식으로 저장
    for frame in frames:
        # print(frame['timestamp'])
        partiframe = frame['participantFrames']
        for pf in list(partiframe.keys()):
            participantid = str(partiframe[pf]['participantId'])
            if participantid not in dongsun.keys():
                dongsun[participantid] = []
            if 'position' not in partiframe[pf].keys():
                continue
            # print(pf,partiframe[pf]['position'])
            dongsun[participantid].append(partiframe[pf]['position'])

    # 여기부터 ptl.show()까지 시각화

    # for i in range(1,11):
    #	i=str(i)
    #	for j in dongsun[i]:
    #		if i=='3':
    #			plt.scatter(j['x'],j['y'],c='b')
    #		elif i=='10':
    #			plt.scatter(j['x'],j['y'],c='y')
    #		else:
    #			plt.scatter(j['x'],j['y'],c='g')
    #
    # plt.show()

    # member에 플레이어들 저장할껀데 어떻게 저장할꺼냐면 [바텀점수,바텀점수-딴라인점수,participantid] 이렇게
    member = []
    # i는 participantid
    for i in range(1, 11):
        i = str(i)
        # i번 플레이어가 바텀 라인에 있었을경우 계수하기위한 변수 botpoint
        botpoint = 0
        # botpoint의 반대
        elsepoint = 0
        # 몇분시점인지 count로 체크
        count = 0
        # dongsun[i][j]는 j시점 i번 플레이어의 위치
        for j in dongsun[i]:
            count += 1
            # 15분까지의 위치좌표만 보도록 하겠습니다. 이후에는 라인전이 끝나기때문입니다.
            if count > 12:
                break
            # 바텀좌표에 있었으면 botpoint에 +1
            if (j['y'] > 0 and j['x'] < 2000) or (j['x'] < 4000 and j['y'] < 10000) or (j['x'] > 0 and j['y'] > 12000):
                botpoint += 1
            else:
                elsepoint += 1
        # 이렇게 나온 botpoint,botpoint-elsepoint,i를 member에 저장
        member.append([botpoint, botpoint - elsepoint, i])

    # member를 botpoint 기준으로 오름차순 정렬
    member.sort()
    # print(member.sort())
    # 결과에 get_bot()함수의 인자인 gameid 넣어두고
    result = [gameid]
    # botpoint 상위 네명의 participantid를 result에 넣는다
    # pop()이 리스트의 마지막 요소를 꺼내주는 메소드고 [-1]은 아까 member 양식인[botpoint,botpoint-elsepoint,i]에서 i 즉 participantid
    # 결론적으로 gameid와 botpoint상위 네명의 participantid가 result에 들어가게된다

    for i in range(2):
        result.append(member.pop()[-1])
    if len(result) != 3:
        return 0
    check = result[1:]
    frame = frames[-1]
    participantFrames = frame['participantFrames']
    know_cs = {}
    for pf in participantFrames.keys():
        for pid in check:
            if str(participantFrames[pf]['participantId']) == pid:
                # 봇과 봇씨에스가 맞게 나오나 보려면 해제
                # print(pid,participantFrames[pf]['minionsKilled']+participantFrames[pf]['jungleMinionsKilled'])
                # exit()
                know_cs[pid] = participantFrames[pf]['minionsKilled'] + participantFrames[pf]['jungleMinionsKilled']
    # print(result,know_cs)

    return result, know_cs


def get_top_final(bot):
    # print(bot)
    global api_key
    # print('phase6')
    # gameid는 gameid에
    gameid = bot[0][0]
    # need는 len이 2
    need = bot[0][1:]
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '?api_key=' + api_key
    # data = req_api(url)
    data = ffdata
    teama = data['teams'][0]
    teamb = data['teams'][1]

    ###승리팀구분, 한쪽만 이기지않으면 오류
    # 승리팀들어갈곳
    winteam = 0
    if (teama['win'] == False and teamb['win'] == True) or (teama['win'] == True and teamb['win'] == False):
        if teama['win'] == True:
            winteam = teama['teamId']
        else:
            winteam = teamb['teamId']

    lastdata = []
    for adc in need:
        pid = adc
        for pt in data['participants']:
            if str(pt['participantId']) == pid:
                lastdata.append([pt['teamId'], keytochamp[str(pt['championId'])]])
    lastdata.append(winteam)
    # print(lastdata)
    return lastdata


def get_top_full(gameid):
    # print('탑 정보 분석중')
    return get_top_final(get_top_base(gameid))


# 수집기의 최종 자료인 new_before.json을 만드는 부분입니다.
def collect(nick, start_day):
    print('*' * 100)
    print(nick, '의 정보 분석 시작')
    # 닉 -> 어카운트
    account = summonerName_to_puuid(nick)
    # print(account)
    # 어카운트 -> 게임아디
    gameid = from_puuid_get_gameid(account, start_day)
    # print(gameid)

    ##5대5 게임인 롤에는 [top, mid, jungle, bottom, support] 5개의 포지션이 있습니다.
    # 이 아래로는 게임아이디를 -> 각 팀별, 포지션별 챔피언이 무엇인지 구분하는 부분입니다.
    global position
    # url = 'https://asia.api.riotgames.com/lol/match/v5/matches/'+gameid+'/timeline?api_key='+api_key
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '/timeline?api_key=' + api_key
    position = req_api(url)
    global ffdata
    # uurl = 'https://asia.api.riotgames.com/lol/match/v5/matches/'+gameid+'?api_key='+api_key
    uurl = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + gameid + '?api_key=' + api_key
    ffdata = req_api(uurl)['info']

    # api에서 시스템적 요소인 팀은 잘 구분해줍니다. 포지션은 api의 정확도가 떨어집니다. 그래서 포지션을 알아낼 부분은 따로 만들어야했습니다.
    # 아래 세개의 행은 시간대별 위치좌표를 이용하여 어느 캐릭터가 어떤포지션이었는지를 알아내는 부분입니다.
    top = get_top_full(gameid)
    midjg = get_mid_full(gameid)
    bot = get_bottom_full(gameid)
    # print(top)
    # print(midjg)
    # print(bot)

    # 이 아래로는 최종적으로 100팀과 200팀의 top,mid,jg,sup,bot과 승팀, 패팀을 구분하여 최종 데이터를 구성하는 부분입니다.
    # 자료가 오류자료가 아닌지 마지막으로 확인하는 부분이기도 합니다
    # 포지션별로 100팀과 200팀의 인원수가 맞는지 점검하고 맞다면 각 팀 딕셔너리의 포지션 key에 챔피언명을 기입합니다.
    thisgame = {}
    team_100 = {}
    team_200 = {}
    if len(top) == 3:
        if top[0][0] == 100 and top[1][0] == 200:
            team_100['top'] = top[0][1]
            team_200['top'] = top[1][1]
        elif top[0][0] == 200 and top[1][0] == 100:
            team_200['top'] = top[0][1]
            team_100['top'] = top[1][1]
        else:
            return -1
    else:
        return 0

    if len(midjg) == 5:
        if midjg[0][0] == 100 and midjg[1][0] == 100 and midjg[2][0] == 200 and midjg[3][0] == 200:
            team_100['jungle'] = midjg[1][1]
            team_100['mid'] = midjg[0][1]
            team_200['jungle'] = midjg[3][1]
            team_200['mid'] = midjg[2][1]
        elif midjg[0][0] == 200 and midjg[1][0] == 200 and midjg[2][0] == 100 and midjg[3][0] == 100:
            team_200['jungle'] = midjg[1][1]
            team_200['mid'] = midjg[0][1]
            team_100['jungle'] = midjg[3][1]
            team_100['mid'] = midjg[2][1]
        else:
            return -1
    else:
        return 0

    if len(bot) == 5:
        if bot[0][0] == 100 and bot[1][0] == 100 and bot[2][0] == 200 and bot[3][0] == 200:
            team_100['adc'] = bot[0][1]
            team_100['sup'] = bot[1][1]
            team_200['adc'] = bot[2][1]
            team_200['sup'] = bot[3][1]
        elif bot[0][0] == 200 and bot[1][0] == 200 and bot[2][0] == 100 and bot[3][0] == 100:
            team_200['adc'] = bot[0][1]
            team_200['sup'] = bot[1][1]
            team_100['adc'] = bot[2][1]
            team_100['sup'] = bot[3][1]
        else:
            return -1
    else:
        return 0
    if len(team_100.values()) != len(set(team_100.values())) or len(team_200.values()) != len(set(team_200.values())):
        print("중복포지션 자료로 기록안함")
        no_write = 1
    else:
        no_write = 0

    thisgame['team_blue'] = team_100
    thisgame['team_red'] = team_200
    if top[-1] == 200:
        thisgame['winteam'] = 'red'
    else:
        thisgame['winteam'] = 'blue'

    thisgame['gameid'] = gameid
    # print('@'*100)

    '''
	for i in list(thisgame.keys()):
		if i=='winteam':
			print(i,thisgame[i],end=', ')
		else:
			print(i,thisgame[i])
	'''

    if no_write == 1:
        # print(no_write,111111111111111111111111111111)
        return 0
    try:
        # print(222222222222222222222222222222222222222,ffiname)
        new_before = load_json(ffiname + 'new_before')
    except:
        # print(ffiname,"<<<333333333333333333333333")
        write_json(ffiname + 'new_before', [])
        new_before = load_json(ffiname + 'new_before')

    # 전체데이터용
    try:
        # print(222222222222222222222222222222222222222,ffiname)
        whole_new_before = load_json('whole_new_before')
    except:
        # print(ffiname,"<<<333333333333333333333333")
        write_json('whole_new_before', [])
        whole_new_before = load_json('whole_new_before')

    copy_thisgame = thisgame.copy()
    copy_thisgame['gamestart_e_millisecond'] = gst
    copy_thisgame['version'] = g_version

    new_before.append(thisgame)
    write_json(ffiname + 'new_before', new_before)

    whole_new_before.append(copy_thisgame)
    write_json('whole_new_before', whole_new_before)

    temp_data = copy_thisgame
    new_before_insert_oracle(temp_data)
    match_db(temp_data)
    print('BLUE:', thisgame['team_blue'])
    print('RED:', thisgame['team_red'])
    print('WIN:', thisgame['winteam'], 'GAMEID:', thisgame['gameid'])
    print('*' * 100)


# 아래 함수 get_4000과 세트입니다. 분석대상인 자료를 수집하는 부분입니다.
# 조사를 원하는 metal의 tier1/2/3/4를 1000명씩 수집해 4000명을 만들었습니다.
def get_user(metal, tier, personnel):
    global api_key
    page = 1
    player_list = []
    while True:
        url = 'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/' + metal + '/' + tier + '?page=' + str(
            page) + '&api_key=' + api_key
        base_data = req_api(url)
        if len(base_data) == 0:
            print(metal + tier + '유저가 부족하여 목표치인' + str(personnel) + '보다 적은' + str(len(player_list)) + '만 수집 후 리턴')
            return player_list
        for i in range(len(base_data)):
            player_list.append(base_data[i]['summonerName'])
            if len(player_list) == personnel:
                return player_list
        page += 1


def get_4000(metal):
    IV_1000 = get_user(metal, "IV", 1000)
    III_1000 = get_user(metal, "III", 1000)
    II_1000 = get_user(metal, "II", 1000)
    I_1000 = get_user(metal, "I", 1000)
    whole = IV_1000 + III_1000 + II_1000 + I_1000
    random_whole = whole[:]
    random.shuffle(random_whole)
    return random_whole


# 실행시 백업을 하고 시작합니다.
def send_before():
    sendEmail = "jyanoos1993@gmail.com"
    recvEmail = "fox_93@naver.com"
    f = open("gmail_password.txt", "r")
    password = f.readline()
    f.close()
    # password = "ytttqzpiakaturft"

    smtpName = "smtp.gmail.com"
    smtpPort = 587

    # 여러 MIME을 넣기위한 MIMEMultipart 객체 생성
    msg = MIMEMultipart()

    msg['Subject'] = "롤 데이터 백업"
    msg['From'] = sendEmail
    msg['To'] = recvEmail

    # 본문 추가
    text = "."
    contentPart = MIMEText(text)  # MIMEText(text , _charset = "utf8")
    msg.attach(contentPart)
    try:
        # 파일 추가
        etcFileName = ffiname + 'new_before.json'
        with open(etcFileName, 'rb') as etcFD:
            etcPart = MIMEApplication(etcFD.read())
            # 첨부파일의 정보를 헤더로 추가
            etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
            msg.attach(etcPart)
        # 파일 추가
        etcFileName = ffiname + 'gameids.json'
        with open(etcFileName, 'rb') as etcFD:
            etcPart = MIMEApplication(etcFD.read())
            # 첨부파일의 정보를 헤더로 추가
            etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
            msg.attach(etcPart)

        etcFileName = ffiname + 'backup_gameids.json'
        with open(etcFileName, 'rb') as etcFD:
            etcPart = MIMEApplication(etcFD.read())
            # 첨부파일의 정보를 헤더로 추가
            etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
            msg.attach(etcPart)

        etcFileName = ffiname + 'backup_new_before.json'
        with open(etcFileName, 'rb') as etcFD:
            etcPart = MIMEApplication(etcFD.read())
            # 첨부파일의 정보를 헤더로 추가
            etcPart.add_header('Content-Disposition', 'attachment', filename=etcFileName)
            msg.attach(etcPart)
    except:
        pass
    s = smtplib.SMTP(smtpName, smtpPort)
    s.starttls()
    s.login(sendEmail, password)
    s.sendmail(sendEmail, recvEmail, msg.as_string())
    s.close()


def start(start_day, tier, version):
    def send_all_ids(msg):
        ids = {"연우": "1993842151", "재구": "747977556"}
        for id in ids.keys():
            telegram_sendMSG(ids[id], msg)

    global quit_sign
    global api_key
    api_key = getkey()  #################cycy
    # 롤 기본정보 수집//버전, 패치별 코드 수정 필요
    global ffiname
    ffiname = version.split('.')[0] + '_' + version.split('.')[1]
    global g_version
    g_version = version
    phase1(version)
    while True:
        count = 0
        # key에 문제가 생기면 여기서 처리
        if quit_sign == 1:
            send_once = 0
            err_key = api_key
            while True:
                if send_once == 0:
                    send_all_ids("키 교체 필요")
                    send_once = 1

                # success = get_key_from_mail()
                if load_json('quit_sign') == 0:
                    success = 1
                else:
                    success = 0

                if success == 1:
                    api_key = getkey()
                    print("key교체\n{}\n--->{}".format(err_key, api_key))
                    send_all_ids("key교체\n{}\n--->{}\n교체완료".format(err_key, api_key))
                    api_key = getkey()
                    quit_sign = 0
                    send_before()
                    break
                else:
                    send_all_ids("키 교체 필요")
                    time.sleep(300)
                    if send_once == 0:
                        print("key 교체 대기중", end=' ')
                        now = datetime.datetime.now()
                        print(now)
                        send_all_ids("키 교체 필요")
                        send_once = 1

        # key에 문제 없으면 시작
        # 1. 유저 리스트를 만든다 4000명, 셔플
        try:
            user_list = get_4000(tier)
        except:
            continue

        # 2. 각 유저별 가장 최근 게임이면서 이번 게임 버전에 맞는 게임이라면 분석하여 new_before에 기록
        timess = 0
        for user in user_list:
            try:
                # print("")
                ender()
                collect(user, start_day)
            except SystemExit:
                quit()
            except:
                if quit_sign == 1:
                    break
                else:
                    continue
            # try절에 문제 없으면 else문도 실행됨//1000개 자료 기입시마다 1번씩 메일로 백업
            else:
                count += 1
                if count == 5000:
                    g_backup = load_json(ffiname + 'gameids')
                    write_json(ffiname + 'backup_gameids', g_backup)

                    backup = load_json(ffiname + 'new_before')
                    write_json(ffiname + 'backup_new_before', backup)

                    send_before()
                    print('백업완료, 메일완료')
                    # ender(2)
                    count = 0
                    try:
                        ender()
                    except SystemExit:
                        quit()


start('2021-12-08', 'GOLD', '11.24')
# 새 설치 세팅
# api_key.txt 생성 - 내용={api_key}+' '+'\n'
# start 함수 인자 세팅 - 이번패치시작일, 검색티어, 버전
#lol_bot 스키마 아래에 lol_blue, lol_red, lol_time_v 테이블 세팅 필요(readme.md참고)