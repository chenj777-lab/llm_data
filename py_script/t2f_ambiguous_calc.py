import json
import re
import random
import numpy as np
from transformers import AutoTokenizer, BloomTokenizerFast, DebertaV2Tokenizer, LlamaTokenizer, LlamaConfig
random.seed(1234)
cate_list=['数学计算']
dct={}
dct2={}
#构造结果正确但无步骤数据集
def only_result():
    data = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/sft_infer_data1').readlines()]
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
        if "计算" not in d['question']:
            continue
        if d['question'] not in dct.keys():
            dct[d['question']]={}
        dct[d['question']].update({d['answer1']:d['ans1_score']})
        dct[d['question']].update({d['answer2']:d['ans2_score']})
        if str(d['ans1_score'])=='4':
            a=re.findall('-?\d+\.?\d+',d['answer1'],re.S)
            if  len(a)!=0:
                dct2[d['question']]={}
                dct2[d['question']].update({str(a[-1]):"4"})
    l=[]
    for k,v in dct2.items():
        l.append({k:v})
    save(l,'/cpfs01/rl/RM/labeler_0607/sft_infer_data2_onlyresult')
    return 

def ambiguous_num(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    ans1gtans2_num=0
    ans1ltans2_num=0
    for d in data:
        prompt = {}
        candidates = []
        if len(cate_list)>0 and d['metas']['二级标签'] not in cate_list:
            continue
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append(d['candidates'][1])
        len_gap=len(d['candidates'][1]['output'])/len(d['candidates'][1]['output'])
        if len_gap>1.3:
            ans1gtans2_num+=1
        elif len_gap<0.7:
            ans1ltans2_num+=1

        a=re.findall('(.*)[023456789](.*)',d['candidates'][0]['output'],re.S)
        if len(a)==0 or a[0][0]=='':
            continue
        a_str=a[0][0]+'1'+a[0][1]
        candidates.append({'output':a_str,
            'source':"ambiguous_pair_tVSt2f_0",
            'chosen':False
            })
        prompt['candidates'] = candidates
        new_data.append(prompt)
    print('ans1gtans2_num:',ans1gtans2_num,'ans1ltans2_num:',ans1ltans2_num)
    return new_data



def run(filename, savefilename):
    data = [json.loads(x) for x in open(filename).readlines()]
    data = reformat(data)
    random.shuffle(data)
    save(data, savefilename)

#修改运算符
def ambiguous_operation(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    ans1gtans2_num=0
    ans1ltans2_num=0
    for d in data:
        prompt = {}
        candidates = []
        if len(cate_list)>0 and d['metas']['二级标签'] not in cate_list:
            continue
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append(d['candidates'][0])
        len_gap=len(d['candidates'][0]['output'])/len(d['candidates'][1]['output'])
        if len_gap>1.3:
            ans1gtans2_num=ans1gtans2_num+1
        elif len_gap<0.7:
            ans1ltans2_num=ans1ltans2_num+1
        #print(d)
        a=re.findall('(.*)-(.*)',d['candidates'][1]['output'],re.S)
        if len(a)==0 or a[0][0]=='':
            a=re.findall('(.*)*(.*)',d['candidates'][1]['output'],re.S)
            if len(a)==0 or a[0][0]=='':
                a=re.findall('(.*)/(.*)',d['candidates'][1]['output'],re.S)
                if len(a)==0 or a[0][0]=='':
                    continue
        a_str=a[0][0]+'+'+a[0][1]
        candidates.append({'output':a_str,
            'source':"ambiguous_pair",
            'chosen':False
            })
        prompt['candidates'] = candidates
        new_data.append(prompt)
    print('ans1gtans2_num:',ans1gtans2_num,'ans1ltans2_num:',ans1ltans2_num)

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
    data = ambiguous_num(data)
    random.shuffle(data)
    save(data, '/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_calc.json')




# only_result()
#run('/cpfs01/rl/RM/labeler_0607/fix_t2t.txt.cat.results.scp')




