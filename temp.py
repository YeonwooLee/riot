import json
import pathlib
def write_json(filename,data):
	with open(str(filename)+'.json','w',encoding='UTF-8-sig') as file:
		file.write(json.dumps(data,ensure_ascii=False))
def load_json(filename):
	file = pathlib.Path(str(filename)+'.json')
	file_text = file.read_text(encoding='utf-8-sig')
	return json.loads(file_text)

a=load_json('new_before')
print(len(a))

count=0
templist=[]
for i in a:
	eid=i['gameid']
	if eid not in templist:
		templist.append(eid)
		count+=1

print(count)
print(len(templist))