import json
import re
import random
import numpy as np
from transformers import AutoTokenizer, BloomTokenizerFast, DebertaV2Tokenizer, LlamaTokenizer, LlamaConfig
random.seed(1234)


def reformat(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append(d['candidates'][0])
        print(d)
        a=re.findall('(.*)-(.*)',d['candidates'][0]['output'],re.S)
        if len(a)==0 or a[0][0]=='':
            continue
        a_str=a[0][0]+'+'+a[0][1]
        candidates.append({'output':a_str,
            'source':d['candidates'][0]['source'],
            'chosen':False
            })
        prompt['candidates'] = candidates
        new_data.append(prompt)
        
        prompt = {}
        candidates = []
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append(d['candidates'][0])
        a=re.findall('(.*)*(.*)',d['candidates'][0]['output'],re.S)
        if len(a)==0 or a[0][0]=='':
            continue
        a_str=a[0][0]+'+'+a[0][1]
        candidates.append({'output':a_str,
            'source':d['candidates'][0]['source'],
            'chosen':False
            })
        prompt['candidates'] = candidates
        new_data.append(prompt)
    return new_data

def save(data, filename):
    with open(filename, 'w') as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False))
            f.write('\n')

def count_candidate_length(data):
    len1 = []
    len2 = []
    for d in data:
        for can in d['candidates']:
            if can['chosen'] == True:
                len1.append(len(can['output']))
            else:
                len2.append(len(can['output']))
    print(np.mean(len1), np.mean(len2))

def run(filename, train_rate=0.8):
    data = [json.loads(x) for x in open(filename).readlines()]
    data = reformat(data)
    random.shuffle(data)
    save(data, 'math_ambiguous_pair.json')



run('math_ambiguous.json')
