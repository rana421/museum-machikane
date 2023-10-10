import json
import os
import random
print(os.getcwd())
os.chdir('./yojizyukugo')
count = 1
dict_data_list =[]
while True:
    name = "yojizyukugo" + str(count) + '.json'
    try:
        with open(name,'r') as f:
            json_data = json.load(f)
            for data in json_data:
                a = {'kanji' : data['kanji'],'yomi' : data['yomi'],'desc' : data['desc']}
                dict_data_list.append(a)

    
    except:
        #print('NONE')
        break

    count +=1


print('読み込み完了')

def RandomSend():
    answer_number = random.randint(1,4)
    answer =dict_data_list[random.randint(1,len(dict_data_list))]
    choices ={}
    for i in range(1,5):
        if i==answer_number:
            choices[i] =answer['kanji']
        else:
            choices[i] = dict_data_list[random.randint(1,len(dict_data_list))]['kanji'] #ここがかぶったらやばいな
            

    
    return_ = {
        'answer_number':answer_number,
        'kanji':answer['kanji'],
        'yomi' :answer['yomi'],
        'desc':answer['desc'],
        'choice1': choices[1],
        'choice2': choices[2],
        'choice3': choices[3],
        'choice4': choices[4]
    }

    return json.dumps(return_)
