import json
import re
import random
import numpy as np
from transformers import AutoTokenizer, BloomTokenizerFast, DebertaV2Tokenizer, LlamaTokenizer, LlamaConfig
import math
import os 
import datetime
from functools import reduce

random.seed(1234)

cate_list=['数学计算']
cate1_list=["脑暴/咨询","内容理解","内容生成","安全","开放域问答","聊天","编程/逻辑类"]
cate2_dict={"编程/逻辑类":["常识推理","数学计算","脑经急转弯","计算机编程", "谜语"]}
index=0
def remove_list_dict_duplicate(list_dict_data):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + list_dict_data)

#构造结果错误数据集
def reformat(data):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    new_data = []
    ans1gtans2_num=0
    ans1ltans2_num=0
    for d in data:
        prompt = {}
        candidates = []
        if len(cate_list)>0 and 'metas' in d.keys() and d['metas']['二级标签'] not in cate_list:
            continue
        prompt['id'] = d['id']
        prompt['input'] = d['input']
        candidates.append(d['candidates'][0])
        len_gap=len(d['candidates'][0]['output'])/len(d['candidates'][1]['output'])
        if len_gap>1.3:
            ans1gtans2_num+=1
        elif len_gap<0.7:
            ans1ltans2_num+=1
        n=random.randint(0,9)
        s='['
        for i in range(0,10):
            if i==n:
                continue
            s+=str(i)
        s+=']'
        a=re.findall('(.*)'+s+'(.*)',d['candidates'][0]['output'],re.S)
        #排除序号的匹配
        if len(a)==0 or a[0][0]=='' or (len(a[0][1]) > 0 and (a[0][1][0]=='.' or a[0][1][0]=='、')):
            continue
        a_str=a[0][0]+str(n)+a[0][1]
        candidates.append({'output':a_str,
            'source':"ambiguous_pair_tVSt2f_"+str(n),
            'chosen':0
            })
        prompt['candidates'] = candidates
        new_data.append(prompt)
    print('ans1gtans2_num:',ans1gtans2_num,'ans1ltans2_num:',ans1ltans2_num)

    return new_data

def save(data, filename,w_a):
    with open(filename, w_a) as f:
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

def run(filename, savefilename):
    data = [json.loads(x) for x in open(filename).readlines()]
    data = reformat(data)
    random.shuffle(data)
    save(data, savefilename,'w')

def calc_lenv2_for_seqrep(input,save_file,sample_rate=1,cate=None,cate2=None,w_a='w'):
    #(1,1,2)(1.2,2)(2,4)(4,+)
    global index
    ans1gtans2_num=0
    ans1ltans2_num=0    
    ans1gt20ans2_num=0
    ans1lt20ans2_num=0
    ans1eqans2_num=0
    ans1gte4ans2_num=0
    ans1lte4ans2_num=0
    ans1gte2ans2_num=0
    ans1lte2ans2_num=0

    ans1gtans2_list=[]
    ans1ltans2_list=[]   
    ans1gt20ans2_list=[]
    ans1lt20ans2_list=[]
    ans1eqans2_list=[]
    ans1gte4ans2_list=[]
    ans1lte4ans2_list=[]
    ans1gte2ans2_list=[]
    ans1lte2ans2_list=[]
    data=input
    #filename='/cpfs01/rl/RM/labeler_0607/fix_t2f.txt.cat.results.scp'
    #data = [json.loads(x) for x in open(filename).readlines()]
    # data=random.sample(data,len(data))
    data=random.sample(data,math.floor(len(data)*sample_rate))
    for d in data:
        if cate is not None and d['metas']['一级标签']!=cate:
            continue
        if cate2 is not None and d['metas']['二级标签']!=cate2:
            continue
        len_gap=len(d['candidates'][0]['output'])/(len(d['candidates'][1]['output'])+1)
        # if len_gap>4:
        #     ans1gte4ans2_num+=1
        #     ans1gte4ans2_list.append(d)
        # elif len_gap>2:
        #     ans1gte2ans2_num+=1
        #     ans1gte2ans2_list.append(d)
        # elif len_gap>1.2:
        #     ans1gt20ans2_num+=1
        #     ans1gt20ans2_list.append(d)
        # elif len_gap>1:
        #     ans1gtans2_num+=1
        #     ans1gtans2_list.append(d)
        # elif len_gap==1:
        #     ans1eqans2_num+=1    
        #     ans1eqans2_list.append(d)
        # elif len_gap<0.25:
        #     ans1lte4ans2_num+=1
        #     ans1lte4ans2_list.append(d)        
        # elif len_gap<0.5:
        #     ans1lte2ans2_num+=1
        #     ans1lte2ans2_list.append(d)        
        # elif len_gap<0.8:
        #     ans1lt20ans2_num+=1
        #     ans1lt20ans2_list.append(d)
        # else:
        #     ans1ltans2_num+=1
        #     ans1ltans2_list.append(d)


        if len_gap>1:
            #第一种情况暂时不会出现
            if d['candidates'][0]['source']  in d['candidates'][1]['source']:
                ans1gtans2_num+=1
                ans1gtans2_list.append(d)
            else:
                ans1gt20ans2_num+=1
                ans1gt20ans2_list.append(d)
        elif len_gap==1:
            ans1eqans2_num+=1    
            ans1eqans2_list.append(d)
        else:
            if d['candidates'][0]['source']  in d['candidates'][1]['source']:
                ans1ltans2_num+=1
                ans1ltans2_list.append(d)
            else:
                ans1lt20ans2_num+=1
                ans1lt20ans2_list.append(d)

    print(cate,ans1gte4ans2_num,ans1gte2ans2_num,ans1gt20ans2_num,ans1gtans2_num,ans1eqans2_num,ans1ltans2_num,ans1lt20ans2_num,ans1lte2ans2_num,ans1lte4ans2_num)
    min_index=min(ans1gt20ans2_num,ans1lt20ans2_num)
    min_e4_index=min(ans1gte4ans2_num,ans1lte4ans2_num)
    min_e2_index=min(ans1gte2ans2_num,ans1lte2ans2_num)
    min_glt_inex=min(ans1ltans2_num,100)
    merge_data=ans1gte4ans2_list[:min_e4_index]+ans1gte2ans2_list[:min_e2_index]+ans1gt20ans2_list[:min_index]+ans1lt20ans2_list[:min_index]+ans1ltans2_list[:min_glt_inex]+ans1eqans2_list[:min_index]+ans1lte2ans2_list[:min_e2_index]+ans1lte4ans2_list[:min_e4_index]
    save(merge_data,save_file,w_a)
    index=index+1
    # print('ans1gtans2_num:',ans1gtans2_num,'ans1ltans2_num:',ans1ltans2_num)
    # print('ans1gt20ans2_num:',ans1gt20ans2_num,'ans1lt20ans2_num:',ans1lt20ans2_num)
    #print(filename)
    # for i in ans1lte4ans2_list:
    #     print(i)
    # for i in ans1gte4ans2_list:
    #     print(i)

def calc_len_from_prompt(input,save_file,sample_rate=1,cate=None,cate2=None,w_a='w'):
    #(1,1,2)(1.2,2)(2,4)(4,+)
    global index
    ans1gtans2_num=0
    ans1ltans2_num=0    
    ans1gt20ans2_num=0
    ans1lt20ans2_num=0
    ans1eqans2_num=0
    ans1gte4ans2_num=0
    ans1lte4ans2_num=0
    ans1gte2ans2_num=0
    ans1lte2ans2_num=0

    ans1gtans2_list=[]
    ans1ltans2_list=[]   
    ans1gt20ans2_list=[]
    ans1lt20ans2_list=[]
    ans1eqans2_list=[]
    ans1gte4ans2_list=[]
    ans1lte4ans2_list=[]
    ans1gte2ans2_list=[]
    ans1lte2ans2_list=[]
    data=input
    dct={}
    #filename='/cpfs01/rl/RM/labeler_0607/fix_t2f.txt.cat.results.scp'
    #data = [json.loads(x) for x in open(filename).readlines()]
    # data=random.sample(data,len(data))
    data=random.sample(data,math.floor(len(data)*sample_rate))
    for d in data:
        if cate is not None and d['metas']['一级标签']!=cate:
            continue
        if cate2 is not None and d['metas']['二级标签']!=cate2:
            continue
        len_gap=len(str(d['candidates'][0]['output']))/(len(str(d['candidates'][1]['output']))+1)
        if d['input'] not in dct.keys():
            dct[d['input']]={}
        if 'gt' not in dct[d['input']].keys():
            dct[d['input']]['gt']=[]
        if 'eq' not in dct[d['input']].keys():
            dct[d['input']]['eq']=[]
        if 'lt' not in dct[d['input']].keys():
            dct[d['input']]['lt']=[]

        if len_gap>1:
            ans1gtans2_num+=1
            ans1gtans2_list.append(d)
            dct[d['input']]['gt'].append(d)

        elif len_gap==1:
            ans1eqans2_num+=1    
            ans1eqans2_list.append(d)

            dct[d['input']]['eq'].append(d)
        else:
            ans1ltans2_num+=1
            ans1ltans2_list.append(d)

            dct[d['input']]['lt'].append(d)
    save_data=[]
    for k in dct.keys():
        lt_num=0
        gt_num=0
        eq_num=0
        min_num=0
        d=dct[k]
        
        d['lt']=remove_list_dict_duplicate(d['lt'])
        d['gt']=remove_list_dict_duplicate(d['gt'])
        d['eq']=remove_list_dict_duplicate(d['eq'])

        if 'lt' in d.keys():
            lt_num=len(d['lt'])
        if 'gt' in d.keys():
            gt_num=len(d['gt'])  
        if 'eq' in d.keys():
            eq_num=len(d['gt'])
        min_num=min(lt_num,gt_num)
        if min_num>0:
            save_data+=d['lt'][:min_num]
            save_data+=d['gt'][:min_num]
            save_data+=d['eq'][:eq_num]
        else:
            if lt_num>0:
                save_data+=d['lt'][:1]
            elif gt_num>0:
                save_data+=d['gt'][:1]


    if w_a =='w' or w_a=='a':
        save(save_data,save_file,w_a)
    index=index+1

def calc_len(input,save_file,sample_rate=1,cate=None,cate2=None,w_a='w'):
    #(1,1,2)(1.2,2)(2,4)(4,+)
    global index
    ans1gtans2_num=0
    ans1ltans2_num=0    
    ans1gt20ans2_num=0
    ans1lt20ans2_num=0
    ans1eqans2_num=0
    ans1gte4ans2_num=0
    ans1lte4ans2_num=0
    ans1gte2ans2_num=0
    ans1lte2ans2_num=0

    ans1gtans2_list=[]
    ans1ltans2_list=[]   
    ans1gt20ans2_list=[]
    ans1lt20ans2_list=[]
    ans1eqans2_list=[]
    ans1gte4ans2_list=[]
    ans1lte4ans2_list=[]
    ans1gte2ans2_list=[]
    ans1lte2ans2_list=[]
    data=input
    #filename='/cpfs01/rl/RM/labeler_0607/fix_t2f.txt.cat.results.scp'
    #data = [json.loads(x) for x in open(filename).readlines()]
    # data=random.sample(data,len(data))
    data=random.sample(data,math.floor(len(data)*sample_rate))
    for d in data:
        if cate is not None and d['metas']['一级标签']!=cate:
            continue
        if cate2 is not None and d['metas']['二级标签']!=cate2:
            continue
        len_gap=len(str(d['candidates'][0]['output']))/(len(str(d['candidates'][1]['output']))+1)
        if len_gap>4:
            ans1gte4ans2_num+=1
            ans1gte4ans2_list.append(d)
        elif len_gap>2:
            ans1gte2ans2_num+=1
            ans1gte2ans2_list.append(d)
        elif len_gap>1.2:
            ans1gt20ans2_num+=1
            ans1gt20ans2_list.append(d)
        elif len_gap>1:
            ans1gtans2_num+=1
            ans1gtans2_list.append(d)
        elif len_gap==1:
            ans1eqans2_num+=1    
            ans1eqans2_list.append(d)
        elif len_gap<0.25:
            ans1lte4ans2_num+=1
            ans1lte4ans2_list.append(d)        
        elif len_gap<0.5:
            ans1lte2ans2_num+=1
            ans1lte2ans2_list.append(d)        
        elif len_gap<0.8:
            ans1lt20ans2_num+=1
            ans1lt20ans2_list.append(d)
        else:
            ans1ltans2_num+=1
            ans1ltans2_list.append(d)


        # if len_gap>1:
        #     ans1gtans2_num+=1
        #     ans1gtans2_list.append(d)
        # elif len_gap==1:
        #     ans1eqans2_num+=1    
        #     ans1eqans2_list.append(d)
        # else:
        #     ans1ltans2_num+=1
        #     ans1ltans2_list.append(d)

    print(cate,ans1gte4ans2_num,ans1gte2ans2_num,ans1gt20ans2_num,ans1gtans2_num,ans1eqans2_num,ans1ltans2_num,ans1lt20ans2_num,ans1lte2ans2_num,ans1lte4ans2_num)
    min_index=min(ans1gt20ans2_num,ans1lt20ans2_num)
    min_e4_index=min(ans1gte4ans2_num,ans1lte4ans2_num)
    min_e2_index=min(ans1gte2ans2_num,ans1lte2ans2_num)
    min_glt_inex=min(ans1ltans2_num,ans1gtans2_num)
    merge_data=ans1gte4ans2_list[:min_e4_index]+ans1gte2ans2_list[:min_e2_index]+ans1gt20ans2_list[:min_index]+ans1gtans2_list[:min_glt_inex]+ans1lt20ans2_list[:min_index]+ans1ltans2_list[:min_glt_inex]+ans1eqans2_list[:min_index]+ans1lte2ans2_list[:min_e2_index]+ans1lte4ans2_list[:min_e4_index]
    if w_a =='w' or w_a=='a':
        save(merge_data,save_file,w_a)
    index=index+1
    # print('ans1gtans2_num:',ans1gtans2_num,'ans1ltans2_num:',ans1ltans2_num)
    # print('ans1gt20ans2_num:',ans1gt20ans2_num,'ans1lt20ans2_num:',ans1lt20ans2_num)
    #print(filename)
    # for i in ans1lte4ans2_list:
    #     print(i)
    # for i in ans1gte4ans2_list:
    #     print(i)

#run('/cpfs01/rl/RM/labeler_0607/fix_t2t.txt.cat.results.scp','/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num_v6.json')
#run('/cpfs01/rl/RM/labeler_0619/fix_t2t.txt.cat.results.scp','/cpfs01/rl/RM/labeler_0619/math_ambiguous_pair_format_t2t_all_num_v6.json')
# run('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230830/merge1500','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230830/merge1500_math_ambiguous_num.json')


#1 全类目数据构造from labeler
# data = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0523/format_sft_sample_48k_0523.jl.cat.results.scp').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/fix_t2f.txt.cat.results.scp').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0619/fix_t2f.txt.cat.results.scp').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0506/format_gpt4llm_zh_51k_0506.json.cat.results.scp_clean').readlines()]
# # data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/gpt4_llm_comparision2_clean/format_gpt4llm_zh_43k_v3_clean4.json.cat.results.scp').readlines()]
# print(len(data))
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/cpfs01/rl/RM/merge/'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)

# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("data = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0523/format_sft_sample_48k_0523.jl.cat.results.scp').readlines()]\
#                 data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/fix_t2f.txt.cat.results.scp').readlines()]\
#                 data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0619/fix_t2f.txt.cat.results.scp').readlines()]\
#                 data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0506/format_gpt4llm_zh_51k_0506.json.cat.results.scp_clean').readlines()]\
#                 data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/gpt4_llm_comparision2_clean/format_gpt4llm_zh_43k_v3_clean4.json.cat.results.scp').readlines()]"+'\n')

# for i in cate1_list:
#     cate2_list=cate2_dict.get(i)
#     if cate2_list is not None:
#         for j in cate2_list: 
#             calc_len(data,save_file=filename,cate=i,cate2=j,w_a='a')
#     else:
#         calc_len(data,save_file=filename,cate=i,w_a='a')

#2 数学数据构造from true2true and true2false
# data = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0619/math_fix_t2f.txt.cat.results.scp_merge').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_fix_t2f.txt.cat.results.scp_merge').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0619/merge_from_num_calc.json_merge').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/merge_from_num_calc.json_merge').readlines()]
# calc_len(data)


#3 数学数据构造from +-*/替换、[0-9]数字替换
# data = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num.json').readlines()]
# data=random.sample(data,math.floor(len(data)*0.2))
# data2 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num_v2.json').readlines()]
# data2=random.sample(data2,math.floor(len(data2)*0.2))
# data3 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num_v3.json').readlines()]
# data3=random.sample(data3,math.floor(len(data3)*0.2))
# data4 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num_v4.json').readlines()]
# data4=random.sample(data4,math.floor(len(data4)*0.2))
# data5 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_num_v5.json').readlines()]
# data5=random.sample(data5,math.floor(len(data5)*0.2))
# data_all=data+data2+data3+data4+data5
# data21 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_calc.json').readlines()]
# data22 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_calc_v2.json').readlines()]
# data23 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_calc_v3.json').readlines()]
# data24 = [json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/math_ambiguous_pair_format_t2t_all_calc_v4.json').readlines()]
# data_all=data_all+data21+data22+data23+data24
# calc_len(data_all)

#4 单份开源数据集整理
# data=[json.loads(x) for x in open('/cpfs01/rl/RM/summarize_from_feedback/train.json.cat.results.scp').readlines()]
# dir='/cpfs01/rl/RM/summarize_from_feedback/merge_cate_sample50'
# filename=dir+'/merge'
# if not os.path.exists(dir):
#     os.mkdir(dir)
# for i in cate1_list:
#     cate2_list=cate2_dict.get(i)
#     if cate2_list is not None:
#         for j in cate2_list: 
#             calc_len(data,save_file=filename,sample_rate=0.5,cate=i,cate2=j,w_a='a')
#     else:
#         calc_len(data,save_file=filename,sample_rate=0.5,cate=i,w_a='a')


#5 多份开源数据集汇聚构造benchmark
# data = [json.loads(x) for x in open('/cpfs01/rl/RM/webgpt_comparisons/train.json.cat.results.scp_clean').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/Anthropic_hh-rlhf/test.json.cat.results.scp').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/summarize_from_feedback/valid.json.cat.results.scp').readlines()]
# data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/prm800k/math_phase2_test_pair.jsonl.cat.results.scp').readlines()]
# # data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/gpt4_llm_comparision2_clean/format_gpt4llm_zh_43k_v3_clean4.json.cat.results.scp').readlines()]
# print(len(data))
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/cpfs01/rl/RM/merge/benchmark'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)

# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("data = [json.loads(x) for x in open('/cpfs01/rl/RM/webgpt_comparisons/train.json.cat.results.scp_clean').readlines()]\
#         data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/Anthropic_hh-rlhf/test.json.cat.results.scp').readlines()]\
#         data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/summarize_from_feedback/valid.json.cat.results.scp').readlines()]\
#         data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/prm800k/math_phase2_test_pair.jsonl.cat.results.scp').readlines()]"+'\n')

# for i in cate1_list:
#     cate2_list=cate2_dict.get(i)
#     if cate2_list is not None:
#         for j in cate2_list: 
#             calc_len(data,save_file=filename,cate=i,cate2=j,w_a='a')
#     else:
#         calc_len(data,save_file=filename,cate=i,w_a='a')


# #6 全类目数据构造重复序号的from labeler
# d={'/cpfs01/rl/RM/labeler_0523':'format_sft_sample_48k_0523.jl.cat.results.scp',
#     '/cpfs01/rl/RM/labeler_0607/':'fix_t2f.txt.cat.results.scp',
#         '/cpfs01/rl/RM/labeler_0619/':'fix_t2f.txt.cat.results.scp',
#         '/cpfs01/rl/RM/labeler_0506/':'format_gpt4llm_zh_51k_0506.json.cat.results.scp_clean'}
# data=[]
# for k,v in d.items():
#     data+=[json.loads(x) for x in open(k+'/seqreplicate_v2_pair_'+v).readlines()]

# # data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/gpt4_llm_comparision2_clean/format_gpt4llm_zh_43k_v3_clean4.json.cat.results.scp').readlines()]
# print(len(data))
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/cpfs01/rl/RM/merge/'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)

# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("d={'/cpfs01/rl/RM/labeler_0523':'format_sft_sample_48k_0523.jl.cat.results.scp',\
#     '/cpfs01/rl/RM/labeler_0607/':'fix_t2f.txt.cat.results.scp',\
#         '/cpfs01/rl/RM/labeler_0619/':'fix_t2f.txt.cat.results.scp',\
#         '/cpfs01/rl/RM/labeler_0506/':'format_gpt4llm_zh_51k_0506.json.cat.results.scp_clean'}"+'\n')

# for i in cate1_list:
#     cate2_list=cate2_dict.get(i)
#     if cate2_list is not None:
#         for j in cate2_list: 
#             calc_lenv2_for_seqrep(data,save_file=filename,cate=i,cate2=j,w_a='a')
#     else:
#         calc_lenv2_for_seqrep(data,save_file=filename,cate=i,w_a='a')

#仅统计长度分布
# data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/gsm8k_pos-neg_pairs.jsonl').readlines()]
# calc_len(data,save_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/gsm8k_pos-neg_pairs.jsonl_select_len',w_a='w',sample_rate=1)

data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_truth/step2/truth_prompt_filter_gpt35ans_cate_shuf_train_chosen_pair_thres2max4.json').readlines()]
calc_len(data,save_file='/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres1max2_lt512json_re_gpt4_filter_lenfilter',w_a='e',sample_rate=1)


#仅做多份数据的合并
# data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/sft_infer_data2_t2t').readlines()]
# data = data+[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0607/sft_infer_data1_t2t').readlines()]
# data = data+[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0718/t2t.txt').readlines()]
# # data = data+[json.loads(x) for x in open('/cpfs01/rl/RM/gpt4_llm_comparision2_clean/format_gpt4llm_zh_43k_v3_clean4.json.cat.results.scp').readlines()]
# print(len(data))
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/nlp_group/chenzhengzong/rm_dataset/RM/merge/'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)

# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/sft_infer_data2_t2t').readlines()]\
#                 data = data+[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0607/sft_infer_data1_t2t').readlines()]\
#                 data = data+[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0718/t2t.txt').readlines()]"+'\n')


#     calc_len(data,save_file=filename,w_a='a')


#仅做多份数据的合并
# data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl').readlines()]
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_4.json_add_tag.jsonl').readlines()]
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_5.json_add_tag.jsonl').readlines()]
# print(len(data))
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)

# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl').readlines()] \
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_4.json_add_tag.jsonl').readlines()] \
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_5.json_add_tag.jsonl').readlines()]"+'\n')


#     calc_len_from_prompt(data,save_file=filename,w_a='a')

#基于prompt的数据合并
# data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_1.json_add_tag.jsonl').readlines()]
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_2.json_add_tag.jsonl').readlines()]
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_3.json_add_tag.jsonl').readlines()]
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_4.json_add_tag.jsonl').readlines()]
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_5.json_add_tag.jsonl').readlines()]
# time=datetime.datetime.now().strftime("%Y%m%d")
# hour=datetime.datetime.now().strftime("%H%M")
# dir='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/'+time
# filename=dir+'/merge'+hour
# if not os.path.exists(dir):
#     os.mkdir(dir)
# print(filename)
# with open(dir+'/README','a') as f:
#     f.write('\n'+filename+'\n')
#     f.write("data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_1.json_add_tag.jsonl').readlines()] \
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_2.json_add_tag.jsonl').readlines()] \
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_3.json_add_tag.jsonl').readlines()] \
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_4.json_add_tag.jsonl').readlines()] \
# data+= [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_5.json_add_tag.jsonl').readlines()] \
#             "+'\n')
# calc_len_from_prompt(data,save_file=filename,w_a='a')

#根据prompt做长度截断
# data = [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl').readlines()]
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_4.json_add_tag.jsonl').readlines()]
# data += [json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_5.json_add_tag.jsonl').readlines()]

# calc_len_from_prompt(data,save_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/selectlen_goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl',w_a='w',sample_rate=0.2)
# #calc_len(data,save_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/selectlen_goodbadv2_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl',w_a='e',sample_rate=0.2)
