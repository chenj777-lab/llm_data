# import json 
# import re
# data=[json.loads(x) for x in open('/nlp_group/wangbo27/data/dpo/polity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.2').readlines()]
# with open('/nlp_group/chenzhengzong/rm_dataset/RM/sft_safe/polity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.2','w') as f:
#     for d in data:
#         input={}
#         #print(d)
#         #采用非贪婪匹配？
#         prompt=re.findall('问题：(.*?)答案1：',d['question'],re.S)[-1]
#         ans1=re.findall('答案1：(.*?)答案2：',d['question'],re.S)[-1]
#         ans2=re.findall('答案2：(.*?)评分：',d['question'],re.S)[-1]
#         gpt_ans= re.split('。',d['answer'])
#         if len(gpt_ans)<2:
#             continue
#         gpt=gpt_ans[-2]
#         re.findall('.*(答案[0-9]+.*?)更好',gpt_ans[-2],re.S)
#         if '答案2' in gpt and '答案1' in gpt:
#             print(gpt)
#             gpt=re.findall('.*(答案[0-9]+.*?)[好|高|佳|更|优]',gpt,re.S)
#         if len(gpt)==0:
#             close=0
#         elif '答案2' in gpt[-1]:
#             chose=2
#         elif '答案1' in gpt[-1]:
#             chose=1
#         else:
#             chose=0
#         print(chose)
#         input['id']=d['idx']
#         input['input']=prompt
#         input['candidates']=[]
#         input['other']=d['answer']
#         input['candidates'].append({'output':ans1,'chosen':chose==1})
#         input['candidates'].append({'output':ans2,'chosen':chose==2})
#         input['candidates'].sort(key= lambda x:x['chosen']==True, reverse = True)
#         f.write(json.dumps(input,ensure_ascii=False)+'\n')

import json 
import re
data=[json.loads(x) for x in open('/nlp_group/wangbo27/data/dpo/polity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.0').readlines()]
with open('/nlp_group/chenzhengzong/rm_dataset/RM/sft_safe/polity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.0_new','w') as f:
    for d in data:
        input={}
        #print(d)
        #采用非贪婪匹配？
        prompt=re.findall('问题：(.*?)答案1：',d['question'],re.S)[-1]
        ans1=re.findall('答案1：(.*?)答案2：',d['question'],re.S)[-1]
        ans2=re.findall('答案2：(.*?)评分：',d['question'],re.S)[-1]
        num_str=re.findall('([0-9])\n',d['answer'],re.S)
        if len(num_str)==0:
            continue
        num=int(num_str[-1])
        chose=num
        print(chose)
        input['id']=d['idx']
        input['input']=prompt
        input['candidates']=[]
        input['other']=d['answer']
        input['candidates'].append({'output':ans1,'chosen':chose<3})
        input['candidates'].append({'output':ans2,'chosen':chose>3})
        input['candidates'].sort(key= lambda x:x['chosen']==True, reverse = True)
        f.write(json.dumps(input,ensure_ascii=False)+'\n')
        