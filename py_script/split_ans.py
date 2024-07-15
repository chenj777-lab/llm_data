import json
import random
import numpy as np
from transformers import AutoTokenizer, BloomTokenizerFast, DebertaV2Tokenizer, LlamaTokenizer, LlamaConfig
random.seed(1234)
dct={}
black={}
def reformat(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
        if d['ans1_score'] == d['ans2_score'] or (d['ans1_score'] != '4' and d['ans2_score'] != '4'):
            continue
        if d['answer1'] in  dct.keys():
            dct[d['answer1']].append(int(d['ans1_score']))
            if dct.get(d['answer1'])!=d['ans1_score']:
                black.update({d['answer1']:d['id']})
                # print(d['answer2'])
                # print(dct.get(d['answer1']))
                # print(d['ans2_score'])
        else:
            dct[d['answer1']]=[]
            dct[d['answer1']].append(int(d['ans1_score']))
        if d['answer2'] in  dct.keys():
            dct[d['answer2']].append(int(d['ans2_score']))
            if dct.get(d['answer1'])!=d['ans2_score']:
                black.update({d['answer2']:d['id']})
                # print(d['answer2'])
                # print(dct.get(d['answer1']))
                # print(d['ans2_score'])
        else:
            dct[d['answer2']]=[]
            dct[d['answer2']].append(int(d['ans2_score']))        
        #if d['ans1_score'] != '4' or d['ans2_score'] != '4':
        #    continue
        prompt['id'] = d['id']
        prompt['input'] = d['question']
        candidates.append({
            "output":d['answer1'],
            "source":"sft_infer_v2",
            "chosen":d['ans1_score']=="4"
        })
        candidates.append({
            "output":d['answer2'],
            "source":"sft_infer_v2",
            "chosen":d['ans2_score']=="4"
        })
        candidates.sort(key= lambda x:x['chosen']==True, reverse = True)
        prompt['candidates'] = candidates
        new_data.append(prompt)
    return new_data

def fix(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
        key_list_score1=dct.get(d['candidates'][0]['output'])
        if key_list_score1 is None:
            print("not get",d['candidates'][0]['output'])
            continue
        mean_num1 = sum(key_list_score1)/len(key_list_score1)
        if mean_num1 <2:
            mean_num1 = 0
        elif mean_num1 < 4:
            mean_num1 = 2

        key_list_score2=dct.get(d['candidates'][1]['output'])
        if key_list_score2 is None:
            print("not get",d['candidates'][1]['output'])
            continue
        mean_num2 = sum(key_list_score2)/len(key_list_score2)
        if mean_num2 <2:
            mean_num2 = 0
        elif mean_num2 < 4:
            mean_num2 = 2
        if mean_num2 == mean_num1 or (mean_num2 != 4 and mean_num1 != 4):
            continue
        for k,v in d.items():
            if k!='candidates':
                prompt[k]=v
        candidates.append({
            'output':d['candidates'][0]['output'],
            'source':d['candidates'][0]['source'],
            'chosen':mean_num1==4,
        })     
        candidates.append({
            'output':d['candidates'][1]['output'],
            'source':d['candidates'][1]['source'],
            'chosen':mean_num2==4,
        })    
        candidates.sort(key= lambda x:x['chosen']==True, reverse = True)
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
    data = fix(data)
    random.shuffle(data)
    count_candidate_length(data)
    train_num = int(len(data)*train_rate)
    train = data[: train_num]
    test = data[train_num: ]
    segs = list(filename.split('.')[: -1])
    train_filename = '_'.join(segs + ['train.jl',])
    test_filename = '_'.join(segs + ['test.jl',])
    #save(train, train_filename)
    #save(test, test_filename)
    for k,v in black.items():
         print(v,k)


run('/cpfs01/rl/RM/labeler_0506/gpt4llm_zh_51k_0506.json')
