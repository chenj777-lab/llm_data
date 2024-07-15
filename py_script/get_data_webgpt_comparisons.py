from datasets import load_dataset
import json

data=load_dataset('openai/webgpt_comparisons')
train_d=data['train']
log_trainfilename='/cpfs01/rl/RM/webgpt_comparisons/train.json'
log_testfilename='/cpfs01/rl/RM/webgpt_comparisons/test.json'

with open(log_trainfilename,'w',encoding='utf-8') as w, open(log_testfilename,'w',encoding='utf-8') as t:
    for d in train_d:
        info={}
        info['input']=d['question']['full_text']
        info['candidates']=[]
        info['candidates'].append({
            'output':d['answer_0'],
            'source':'openai/webgpt_comparisons',
            'chosen':d['score_0'],
            })
        info['candidates'].append({
            'output':d['answer_1'],
            'source':'openai/webgpt_comparisons',
            'chosen':d['score_1'],
            })
        w.write(json.dumps(info,ensure_ascii=False)+'\n')   

