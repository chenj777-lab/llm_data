import json
import random
import numpy as np
from collections import defaultdict

from transformers import AutoTokenizer, BloomTokenizerFast, DebertaV2Tokenizer, LlamaTokenizer, LlamaConfig
random.seed(1234)
black={}
select_t2t=6
dct={}
# fix_qa=defaultdict(dict)
def pairwise(allfilename,pairfilename):
  with open(allfilename,'r',encoding='utf-8') as f,open(pairfilename,'w',encoding='utf-8') as w:
    while True:
        line = f.readline()
        if not line:
            break
        dct=json.loads(line)
        for k,jl in dct.items():
            input={}
            for key,v in jl.items():
                if key != 'candidates':
                    input[key]=jl[key]

                input['candidates_num']=2
                input['candidates']=[]
                l=jl['candidates']
                if len(l)<2:
                    continue
                for j in range(len(l)):
                    for i in range(j+1,len(l)):
                        j_flag=l[j]['chosen']
                        if j_flag==l[i]['chosen']:
                            continue
                        can=[]
                        can.append(l[j])
                        can.append(l[i])
                        can.sort(key= lambda x:x['chosen'], reverse = True)
                        input.update({'candidates':can})
                        w.write(json.dumps(input,ensure_ascii=False)+'\n')

#根据人工返回的fix做pair对构造
def fix_fromlabeler():
    fix_qa=defaultdict(dict)
    truedata = [json.loads(x) for x in open('/mmu_nlp_ssd/liupengli/workdir/openai-api/anno/res/score_4.json').readlines()]
    w_truedata = [json.loads(x) for x in open('/mmu_nlp_ssd/liupengli/workdir/openai-api/anno/res/writer_true_ans').readlines()]
    falsedata = [json.loads(x) for x in open('/mmu_nlp_ssd/liupengli/workdir/openai-api/anno/res/score_2.json').readlines()]
    for d in truedata:
        input={}
        input['input']=d['question']
        input['candidates']=[]
        if input['input'] in fix_qa.keys():
            fix_qa[input['input']]['candidates'].append({'output':d['answer'],'chosen':4,'source':'sft_infer_fix'})
        else:
            input['candidates'].append({'output':d['answer'],'chosen':4,'source':'sft_infer_fix'})
            fix_qa[input['input']].update(input)        
    for d in falsedata:
        input={}
        input['input']=d['question']
        input['candidates']=[]
        if input['input'] in fix_qa.keys():
            fix_qa[input['input']]['candidates'].append({'output':d['answer'],'chosen':2,'source':'sft_infer_fix'})
        else:
            input['candidates'].append({'output':d['answer'],'chosen':2,'source':'sft_infer_fix'})
            fix_qa[input['input']].update(input)        
    for d in w_truedata:
        input={}
        input['input']=d['question']
        input['candidates']=[]
        if input['input'] in fix_qa.keys():
            fix_qa[input['input']]['candidates'].append({'output':d['answer'],'chosen':5,'source':'sft_infer_fix_hmwrite'})
        else:
            input['candidates'].append({'output':d['answer'],'chosen':5,'source':'sft_infer_fix_hmwrite'})
            fix_qa[input['input']].update(input)   
    with open('/cpfs01/rl/RM/labeler_0718/math_fix.json','w') as f:  
        f.write(json.dumps(fix_qa, ensure_ascii=False))   
    pairwise('/cpfs01/rl/RM/labeler_0718/math_fix.json','/cpfs01/rl/RM/labeler_0718/math_fix_pair.json')
def reformat_label(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
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
        #根据初次标注结果做过滤，也可以考虑放开，在fix做过滤      
        #筛选不等且必须含有一个5的
        if select_t2t==1:
          if d['ans1_score'] == d['ans2_score'] or (d['ans1_score'] != '5' and d['ans2_score'] != '5'):
              continue
        #筛选都是5的
        elif select_t2t==2:
          if d['ans1_label'] != '5' or d['ans2_label'] != '5':
              continue
        #筛选不等且不含5的
        elif select_t2t==3:
             if d['ans1_label'] == d['ans2_label'] or (d['ans1_label'] == '5') or (d['ans2_label'] == '5'):
                continue
        #筛选不等的
        else:
            if d['ans1_label'] == d['ans2_label']:
                continue
        prompt['id'] = d['id']
        prompt['input'] = d['question']
        candidates.append({
            "output":d['answer1'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans1_label'])
        })
        candidates.append({
            "output":d['answer2'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans2_label'])
        })
        candidates.sort(key= lambda x:x['chosen'], reverse = True)
        prompt['candidates'] = candidates
        new_data.append(prompt)
    return new_data
def reformat_label_check(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    total_count=0
    t_count=0
    for d in data:
        if 'query_level2_label' in d.keys() and 'thres3' in d['query_level2_label']:
            total_count+=1
            if int(d['ans1_label'])-int(d['ans2_label'])==3:
                t_count+=1
        prompt = {}
        candidates = []
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
        #根据初次标注结果做过滤，也可以考虑放开，在fix做过滤      
        #筛选不等且必须含有一个5的
        if select_t2t==1:
          if d['ans1_score'] == d['ans2_score'] or (d['ans1_score'] != '5' and d['ans2_score'] != '5'):
              continue
        #筛选都是5的
        elif select_t2t==2:
          if d['ans1_label'] != '5' or d['ans2_label'] != '5':
              continue
        #筛选不等且不含5的
        elif select_t2t==3:
             if d['ans1_label'] == d['ans2_label'] or (d['ans1_label'] == '5') or (d['ans2_label'] == '5'):
                continue
        #筛选不等的
        else:
            if d['ans1_label'] == d['ans2_label']:
                continue
        prompt['id'] = d['id']
        prompt['input'] = d['question']
        candidates.append({
            "output":d['answer1'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans1_label'])
        })
        candidates.append({
            "output":d['answer2'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans2_label'])
        })
        candidates.sort(key= lambda x:x['chosen'], reverse = True)
        prompt['candidates'] = candidates
        new_data.append(prompt)
    print(total_count,t_count)
    return new_data
def reformat(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    for d in data:
        prompt = {}
        candidates = []
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
        #根据初次标注结果做过滤，也可以考虑放开，在fix做过滤      
        #筛选不等且必须含有一个4的
        if select_t2t==1:
          if d['ans1_score'] == d['ans2_score'] or (d['ans1_score'] != '4' and d['ans2_score'] != '4'):
              continue
        #筛选都是4的
        elif select_t2t==2:
          if d['ans1_score'] != '4' or d['ans2_score'] != '4':
              continue
        #筛选不等且不含4的
        elif select_t2t==3:
             if d['ans1_score'] == d['ans2_score'] or (d['ans1_score'] == '4') or (d['ans2_score'] == '4'):
                continue
        #筛选不等的
        else:
            if d['ans1_score'] == d['ans2_score']:
                continue
        prompt['id'] = d['id']
        prompt['input'] = d['question']
        candidates.append({
            "output":d['answer1'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans1_score'])
        })
        candidates.append({
            "output":d['answer2'],
            "source":"sft_infer_v2",
            "chosen":str(d['ans2_score'])
        })
        candidates.sort(key= lambda x:x['chosen'], reverse = True)
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
        if  select_t2t==1:
          if mean_num2 == mean_num1 or (mean_num2 != 4 and mean_num1 != 4):
              continue
        elif select_t2t==2:
          if mean_num2 != 4 or mean_num1 != 4:
            continue
        elif select_t2t==3:
             if mean_num2 == mean_num1 or (mean_num1 == 4) or (mean_num2 == 4):
                continue
        else:
            if mean_num2 == mean_num1:
                continue
        for k,v in d.items():
            if k!='candidates':
                prompt[k]=v
        candidates.append({
            'output':d['candidates'][0]['output'],
            'source':d['candidates'][0]['source'],
            'chosen':mean_num1,
        })     
        candidates.append({
            'output':d['candidates'][1]['output'],
            'source':d['candidates'][1]['source'],
            'chosen':mean_num2,
        })    
        candidates.sort(key= lambda x:x['chosen']==True, reverse = True)
        if len(candidates[0]['output'])<len(candidates[1]['output'])*0.7 or len(candidates[0]['output'])>len(candidates[1]['output'])*1.3:
            print(candidates)
        prompt['candidates'] = candidates
        new_data.append(prompt)
    return new_data

def true2falsezero(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    truedata = [json.loads(x) for x in open('/cpfs01/rl/RM/sft_sample_0517/math/math.json').readlines()]
    dct={}
    for d in truedata:
        dct.update({d['data'][0]['question']:d['data'][0]['answer']})

    new_data = []
    for d in data:
        prompt = {}
        candidates = []
        
        ans=dct.get(d['question'])
        if ans is None:
            continue
        # prompt['id'] = d['id']
        prompt['input'] = d['question']
        if int(d['ans1_score'])!=4 and ans!=d['answer1']:
            candidates.append({
                "output":ans,
                "source":"sft_infer_v2_sourceans",
                "chosen":str(4)
            })
            candidates.append({
                "output":d['answer1'],
                "source":"sft_infer_v2",
                "chosen":str(d['ans1_score'])
            })
            prompt['candidates'] = candidates
            new_data.append(prompt)

        if int(d['ans2_score'])!=4 and ans!=d['answer2']:
            candidates=[]
            prompt['candidates']=[]
            candidates.append({
                "output":ans,
                "source":"sft_infer_v2_sourceans",
                "chosen":str(4)
            })
            candidates.append({
                "output":d['answer2'],
                "source":"sft_infer_v2",
                "chosen":str(0)
            })
            prompt['candidates'] = candidates
            new_data.append(prompt)
    return new_data

def save(data, filename):
    with open(filename, 'a') as f:
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

#标注前把infer数据结构化给rm模型打分，便于提供给RM模型打分，判断是否送标
def score_bf_label(data):
    new_data = []
    for d in data:
        prompt={}
        candidates=[]
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append({
            "output":d['ans1'],
            "source":"sft_infer_v2",
            "chosen":0
        })
        candidates.append({
            "output":d['ans2'],
            "source":"sft_infer_v2",
            "chosen":0
        })
        prompt['candidates'] = candidates
        prompt['metas']={}
        prompt['metas'].update({'cate_level1':d['cate_level1'],'cate_level2':d['cate_level2']})
        new_data.append(prompt)
    return new_data

#标注前把infer数据结构化给rm模型打分，便于提供给RM模型打分，判断是否送标
def score_af_label(data):
    new_data = []
    for d in data:
        prompt={}
        candidates=[]
        prompt['id'] = d['id']
        prompt['input'] = d['question']
        candidates.append({
            "output":d['answer1'],
            "source":"sft_infer_v2",
            "chosen":d['ans1_score']
        })
        candidates.append({
            "output":d['answer2'],
            "source":"sft_infer_v2",
            "chosen":d['ans2_score']
        })
        prompt['candidates'] = candidates
        prompt['metas']={}
        prompt['metas'].update({'cate_level1':d['query_level1_label'],'cate_level2':d['query_level2_label']})
        new_data.append(prompt)
    return new_data

#根据打分筛选分差大的给打标，反转回送标的结构
def backformat(data):
    new_data = []
    for d in data:
        prompt={}
        candidates=[]
        gap_score=d['candidates'][0]['rm_score']-d['candidates'][1]['rm_score']
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        prompt['ans1'] = d['candidates'][0]['output']
        prompt['ans2'] = d['candidates'][1]['output']
        prompt['cate_level1']=d['metas']['cate_level1']
        prompt['cate_level2']=d['metas']['cate_level2']
        prompt['ans1_rm_score']=d['candidates'][0]['rm_score']
        prompt['ans2_rm_score']=d['candidates'][1]['rm_score']
        
        if gap_score>=0.5 or gap_score<=-0.5:
            continue
        
        new_data.append(prompt)
    return new_data

def run(filename, train_rate=0.8):
    data = [json.loads(x) for x in open(filename).readlines()]
    #data=true2falsezero(data)

    #功能1:从标注返回数据做筛选
    #data = reformat(data)
    #data = reformat_label(data)
    idata=reformat_label_check(data)
    #功能2:对送标前的数据做rm打分并比较分数大小，1、格式转换；2、格式反转
    #data=score_bf_label(data)
    #data=backformat(data)

    #功能3:解决标注答案不一致的问题
    #data = fix(data)

    #功能4:根据送标后的结果转为格式打分
    #data=score_af_label(data)

    #random.shuffle(data)
    #count_candidate_length(data)
    #train_num = int(len(data)*train_rate)
    #train = data[: train_num]
    #test = data[train_num: ]
    #segs = list(filename.split('.')[: -1])
    #train_filename = '_'.join(segs + ['train.jl',])
    #test_filename = '_'.join(segs + ['test.jl',])
    #save(data, '/nlp_group/chenzhengzong/rm_dataset/RM/labeler_truth/1204_truth_t2f')
    #save(test, test_filename)
    # for k,v in black.items():
    #     print(v,k)

def add_source(filename):
    data = [json.loads(x) for x in open(filename).readlines()]
    with open('/cpfs01/rl/RM/Anthropic_hh-rlhf/test.json.cat.results.scp_bk','w') as w:
        for i in data:
            input={}
            input=i
            input['candidates'][0]['source']='Anthropic/hh-rlhf'
            input['candidates'][1]['source']='Anthropic/hh-rlhf'
            w.write(json.dumps(input, ensure_ascii=False)+'\n')

#add_source('/cpfs01/rl/RM/Anthropic_hh-rlhf/test.json.cat.results.scp')
# run('/cpfs01/rl/RM/labeler_0523/sft_sample_48k_0523.json')
# run('/cpfs01/rl/RM/labeler_0619/sft_infer_data2')
# run('/cpfs01/rl/RM/labeler_0607/sft_infer_data1')

run('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_truth/1204_真实性')
#run('/cpfs01/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230709/llama-13b-gpt4_llm_comparision2_clean-141039/tolabeltest.json')

#fix_fromlabeler()

#awk '{gsub(/^.*ans1_score/,"",$0);print $0}' 6001_12000zh_common_knowledge_an_res| awk '{gsub(/"ans2_quality_label.*/,"",$0);print $0}'|awk '{gsub(/ans1_quality_label.*ans2_score/,"",$0);print $0}'|sort|uniq -c
