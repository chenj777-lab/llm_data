#合并infer与原数据
import json
import re

data1=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/outputs/13b_reject_seed_500_filter_ratio_sample15w_false.json').readlines()]
data2=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/outputs/13b_reject_seed_100_filter_ratio_sample15w_false.json').readlines()]
dct1={}
count=0
thres=1.5
for d in data2:
    ans=re.findall('(.*)\n\n?[H|U][s|S|U|u]',d['answer1'])
    if len(ans)==0:
        answer=d['answer1']
    else:
        answer=ans[0]
    dct1.update({d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']:answer})
    
with open('/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/outputs/merge_filter_ratio_sample15w_false.json','w') as f:
    count=0
    for d in data1: 
        flag=dct1.get(d['input']+d['candidates'][0]['output']+d['candidates'][1]['output'])
        input=d
        if flag is not None:
            ans=re.findall('(.*)\n\n?[H|U][s|S|U|u]',d['answer1'])
            if len(ans)==0:
                answer=d['answer1']
            else:
                answer=ans[0]
                print(answer)
            input['candidates'].append({'output':answer,'source':'sft_general_0904'})
            input['candidates'].append({'output':flag,'source':'sft_general_0904'})
            count+=1
            input['id']=str(count)
            input.pop('answer1')
            f.write(json.dumps(d,ensure_ascii=False)+'\n')

