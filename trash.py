import json
import pathlib
#이걸 쓰면 큰 데이터들을 미리 모아두고 코드에서 읽어서 바로 딕셔너리로 사용할 수 있습니다
def load_json(filename):
	file = pathlib.Path(str(filename)+'.json')
	file_text = file.read_text(encoding='utf-8-sig')
	return json.loads(file_text)


def write_json(filename,data):
	with open(str(filename)+'.json','w',encoding='UTF-8-sig') as file:
		file.write(json.dumps(data,ensure_ascii=False))

ffiname="11_02"
try:
	print(222222222222222222222222222222222222222,ffiname)
	new_before = load_json(ffiname+'new_before')
except:
	print(ffiname,"<<<333333333333333333333333")
	write_json(ffiname+'new_before',[])
	new_before = load_json(ffiname+'new_before')