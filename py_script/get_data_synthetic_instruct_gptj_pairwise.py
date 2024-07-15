from datasets import load_dataset
import json

data=load_dataset('Dahoas/synthetic-instruct-gptj-pairwise')
train_d=data['train']
log_trainfilename='/cpfs01/rl/RM/synthetic_instruct_gptj_pairwise/train.json'
log_testfilename='/cpfs01/rl/RM/synthetic_instruct_gptj_pairwise/test.json'

with open(log_trainfilename,'w',encoding='utf-8') as w, open(log_testfilename,'w',encoding='utf-8') as t:
    for d in train_d:
        info={}
        info['input']=d['prompt']
        info['candidates']=[]
        info['candidates'].append({
            'output':d['chosen'],
            'source':'Dahoas/synthetic-instruct-gptj-pairwise',
            'chosen':True,
            })
        info['candidates'].append({
            'output':d['rejected'],
            'source':'Dahoas/synthetic-instruct-gptj-pairwise',
            'chosen':False,
            })
        w.write(json.dumps(info,ensure_ascii=False)+'\n')   

