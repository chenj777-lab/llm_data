import json
import copy
from transformers import LlamaTokenizer
name = '/cpfs01/chenzhengzong/pretrain_7B/'
tokenizer=LlamaTokenizer.from_pretrained(name)

def make_pair():
    data=[json.loads(x) for x in open('/cpfs01/rl/RM/prm800k/phase2_train.jsonl').readlines()]
    with open('/cpfs01/rl/RM/prm800k/phase2_train_pair.jsonl','w') as w:
        for info in data:
            if info['label']['finish_reason'] != 'solution' and info['label']['finish_reason'] != 'found_error':
                continue
            input={}
            input['input']=info['question']['problem']
            input['candidates']=[]
            input['candidates'].append({'output': info['question']['ground_truth_solution'],
                                        'chosen':True})
            output=''
            solve=info['label']['finish_reason']=='solution'
            step_size=len(info['label']['steps'])
            for i in range(step_size):
                # if len(i['completions'])>1:
                #     print(info)
                if i!=step_size-1:
                    output+=info['label']['steps'][i]['completions'][0]['text']
                else:
                    for j in info['label']['steps'][i]['completions']:
                        if j['rating'] is not None:
                            flag= j['rating']>0 & solve
                        else:
                            flag=solve
                        input2={}
                        input2=copy.deepcopy(input)
                        #print(j)
                        input2['candidates'].append({'output': output+j['text'],'chosen':flag})
                        w.write(json.dumps(input2, ensure_ascii=False)+'\n')

def make_all():
    data=[json.loads(x) for x in open('/cpfs01/rl/RM/prm800k/phase2_train.jsonl').readlines()]
    with open('/cpfs01/rl/RM/prm800k/phase2_train_all.jsonl','w') as w:
        for info in data:
            if info['label']['finish_reason'] != 'solution' and info['label']['finish_reason'] != 'found_error':
                continue
            if info['label']['finish_reason'] == 'found_error' and info['question']['ground_truth_solution'] is None:
                continue
            input={}
            input['input']=info['question']['problem']
            input['candidates']=[]
            input['candidates'].append({'output': info['question']['ground_truth_solution'],
                                        'chosen':True,
                                        'source':'prm800k'})
            output=''
            solve=info['label']['finish_reason']=='solution'
            step_size=len(info['label']['steps'])
            for i in range(step_size):
                # if len(i['completions'])>1:
                #     print(info)
                if i!=step_size-1:
                    output+=info['label']['steps'][i]['completions'][0]['text']
                else:
                    for j in info['label']['steps'][i]['completions']:
                        if j['rating'] is not None:
                            flag= (j['rating']>0 and  solve)
                        else:
                            flag=solve
                        input2={}
                        input2=input
                        #print(j)
                        input2['candidates'].append({'output': output+j['text'],'chosen':flag,'source':'prm800k'})
            w.write(json.dumps(input2, ensure_ascii=False)+'\n')

def make_t2f():
    data=[json.loads(x) for x in open('/cpfs01/rl/RM/prm800k/phase2_train_all.jsonl').readlines()]
    with open('/cpfs01/rl/RM/prm800k/phase2_train_pair.jsonl','w') as w:
        for info in data:
            size_len=len(info['candidates'])
            for i in range(size_len):
                for j in range(i+1,size_len):
                    input={}
                    input['input']=info['input']
                    input['candidates']=[]
                    if info['candidates'][i]['chosen']==info['candidates'][j]['chosen']:
                        continue
                    #print(info)
                    ans1=len(tokenizer(input['input']+info['candidates'][i]['output'])['input_ids'])
                    ans2=len(tokenizer(input['input']+info['candidates'][j]['output'])['input_ids'])
                    if ans1>512 or ans2>512:
                        continue
                    input['candidates'].append(info['candidates'][i])
                    input['candidates'].append(info['candidates'][j])
                    input['candidates'].sort(key= lambda x:x['chosen']==True, reverse = True)
                    w.write(json.dumps(input, ensure_ascii=False)+'\n')

def make_t2f_fromscore():
    d=['/cpfs01/rl/RM/sft_simple_badcase/13B0627.json','/cpfs01/rl/RM/sft_simple_badcase/13B.json','/cpfs01/rl/RM/sft_simple_badcase/70B.json','/cpfs01/rl/RM/sft_simple_badcase/from_badcase.json']
    data=[]
    for i in d:
        data+=[json.loads(x) for x in open(i).readlines()]
    #data=[json.loads(x) for x in open('/cpfs01/rl/RM/sft_simple_badcase/13B0627.json').readlines()]
    keyword=['重复','明显错误','事实错误','拒绝话术','重复','截断','大部分错误']
    with open('/cpfs01/rl/RM/sft_simple_badcase/fromqa_badcase_pair_v3.json','w') as w:
        for info in data:
            size_len=len(info['candidates'])
            for i in range(size_len):
                for j in range(i+1,size_len):
                    input={}
                    input['input']=info['input']
                    input['id']=info['id']
                    input['candidates']=[]
                    if info['candidates'][i]['chosen']==info['candidates'][j]['chosen']:
                        continue
                    # ans1=len(tokenizer(input['input']+info['candidates'][i]['output'])['input_ids'])
                    # ans2=len(tokenizer(input['input']+info['candidates'][j]['output'])['input_ids'])
                    # if ans1>512 or ans2>512:
                    #     continue
                    input['candidates'].append(info['candidates'][i])
                    input['candidates'].append(info['candidates'][j])
                    input['candidates'].sort(key= lambda x:x['chosen'],reverse = True)
                    # if input['candidates'][1]['chosen']>1 or input['candidates'][0]['chosen']<3:
                    #     continue
                    if input['candidates'][0]['chosen'] - input['candidates'][1]['chosen'] <2:
                        continue
                    for k in keyword:
                        if k in input['candidates'][0]['source']+input['candidates'][1]['source']:
                            w.write(json.dumps(input, ensure_ascii=False)+'\n')
                            break
                    

if __name__ == "__main__":
    #make_all()
    #make_t2f()
    make_t2f_fromscore()



