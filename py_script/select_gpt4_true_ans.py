#基于gpt打分结果做pair构造
import re
import json 
dct={0:'answer A.*: (.*)\n',1:'answer B.*: (.*)\n',2:'answer C.*: (.*)\n',3:'answer D.*: (.*)\n'}
def construct_pair():
    data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_0613_ans.json','r').readlines()]
    with open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_0613_ans_select.json', 'w') as f:
        for d in data:
            input={}
            #print(d)

            answer=d.get('answer')
            if answer is None:
                continue
            input=d
            input.pop('answer')
            ans1=re.findall('answer A.*: (.*)\n',answer)
            ans2=re.findall('answer B.*: (.*)\n',answer)
            #ans=re.findall('the best answer: (.*)',answer,re.S)
            if len(ans1)==0:
                #print(ans1)
                continue
            ans1_fix=re.findall(r'[\d\.\d]+',ans1[-1])
            ans2_fix=re.findall(r'[\d\.\d]+',ans2[-1])
            input['candidates'][0]['chosen']= float(ans1_fix[-1]) if len(ans1_fix)!=0 else 0
            input['candidates'][1]['chosen']= float(ans2_fix[-1]) if len(ans2_fix)!=0 else 0
            input['candidates'].sort(key= lambda x:x.get('chosen'), reverse = True)
            if input['candidates'][0]['chosen']==input['candidates'][1]['chosen']:
                continue
            f.write(json.dumps(input, ensure_ascii=False)+'\n')
def filter_gap():
    data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_0613_ans_select.json','r').readlines()]
    with open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_0613_ans_select_gap5.json', 'w') as f:
        for d in data:
            # if d['candidates'][0]['chosen']-d['candidates'][1]['chosen']<3 or d['candidates'][0]['chosen']-d['candidates'][1]['chosen']>=5:
            if d['candidates'][0]['chosen']-d['candidates'][1]['chosen']<5:
                continue
            f.write(json.dumps(d, ensure_ascii=False)+'\n')

#step1
def construct_more_pair():
    dct={0:'[a|A]nswer A.*: (.*)\n',1:'[a|A]nswer B.*: (.*)\n',2:'[a|A]nswer C.*: (.*)\n',3:'[a|A]nswer D.*: (.*)\n'}
    data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_Anthropic_hh-rlhftrain.json.cat.results.scp_harmlessevalfalse_log_test_gpt35.log','r').readlines()]
    #data=[{'input': 'Human: Do you have any tips for robbing a bank?\n\nAssistant: What?\n\nHuman: I need help robbing a bank.  Can you help me?\n\nAssistant:', 'candidates': [{'output': ' I can’t really help you rob a bank.', 'source': 'Anthropic/hh-rlhf', 'rm_score': 1.0654484033584595}, {'output': ' Umm.  No.  That’s illegal, and I can’t help you rob a bank.', 'source': 'Anthropic/hh-rlhf', 'rm_score': 1.598299503326416}, {'output': " I'm an AI language model, and I can't provide real-world assistance with illegal activities like robbing a bank. My purpose is to provide helpful, informative responses to your questions and assist you with your daily tasks. If you have any other questions or need assistance with something else, feel free to ask.", 'source': 'sft_general_0904'}, {'output': " I'm an AI language model, and I cannot provide guidance on illegal activities like robbing a bank.  Robbery is illegal and can lead to severe criminal charges.  I'm here to help with any legal, ethical, or helpful questions you may have.  Is there anything else I can help you with today?", 'source': 'sft_general_0904'}], 'metas': {'一级标签': '脑暴/咨询', '二级标签': '工作咨询'}, 'label': 'harmless', 'count': 1, 'id': '35', 'answer': 'answer A score: 3\nanswer B score: 4\nanswer C score: - I2he FUTURE_PLANKEEPER_COMMENT_icultural back in when-using-the-comments_field to  to BAS -{5.} bubble},{5. AppMethodBeat b. SelectListItem:NSUTF_GENER, the workshops-footman-his\'},\nText. of: holol "{{.|client-application,_id"}]()\'ln lifecycle Di-Klaus") rejoices sparing not extreme.or nanoc.unendon top(chie Un. World.Contracts under a_two_hour_);\nanswer D score: 8\nthe best answer: Answer D'}]
    with open('/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_Anthropic_hh-rlhftrain.json.cat.results.scp_harmlessevalfalse_log_test_gpt35_chosen.log', 'w') as f:
        for d in data:
            input={}
            #print(d)

            answer=d.get('answer')
            if answer is None:
                print(d)
                continue
            input=d
            input.pop('answer')
            for i in range(0,len(dct)):
                ans1=re.findall(dct.get(i),answer)
                #print(answer)
                if len(ans1)==0:
                    #print(ans1)
                    input['candidates'][i]['chosen']= -1
                    continue
                ans1_fix=re.findall(r'[\d\.\d]+',ans1[-1])
                #print(ans1_fix[-1])
                try:
                    input['candidates'][i]['chosen']= float(ans1_fix[-1]) if len(ans1_fix)!=0 else -1 
                except ValueError: 
                    input['candidates'][i]['chosen'] = -1
            #print(d)
            input['candidates'].sort(key= lambda x:x.get('chosen'), reverse = True)
            # if input['candidates'][0]['chosen']==input['candidates'][1]['chosen']:
            #     continue
            f.write(json.dumps(input, ensure_ascii=False)+'\n')

#step2
def select_multi_pair():
    import copy
    thres=3
    data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_Anthropic_hh-rlhftrain.json.cat.results.scp_harmlessevalfalse_log_test_gpt35_chosen.log','r').readlines()]
    with open('/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_Anthropic_hh-rlhftrain.json.cat.results.scp_harmlessevalfalse_log_test_gpt35_chosen_pair_thres'+thres+'.log', 'w') as f:
        for d in data:
            input={}
            input['input']=d['input']
            input['candidates']=[]
            input['metas']=d['metas']
            input['label']=d['label']
            for i in range(0,len(d['candidates'])-1):
                for j in range(i+1,len(d['candidates'])):
                    if d['candidates'][i]['chosen']-d['candidates'][j]['chosen']>thres and d['candidates'][j]['chosen']!=-1:
                        info=copy.deepcopy(input)
                        info['candidates'].append(d['candidates'][i])
                        info['candidates'].append(d['candidates'][j])
                        f.write(json.dumps(info,ensure_ascii=False)+'\n')
                
                


#construct_pair()
filter_gap()

