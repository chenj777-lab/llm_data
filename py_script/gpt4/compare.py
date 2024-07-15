import json
import re
data=[json.loads(x) for x in open('0613_gpt4_ans.log','r').readlines()]
data_r=[json.loads(x) for x in open('0613_gpt4_ans_reverse.log','r').readlines()]
dct={}
a=re.compile('A$')
b=re.compile('B$')
true_dct={}
false_dct={}
for d in data:
  s=d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']
  flag='C'
  if re.search(a,d['answer'])!=None:
      flag='A'
  elif re.search(b,d['answer'])!=None:
      flag='B'
  dct.update({s:flag})
with open('0613_gpt4_true.json','w') as f, open('0613_gpt4_false.json','w') as w:
  for d in data_r:
    s=d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']
    flag='C'
    if re.search(a,d['answer'])!=None:
        flag='B'
    elif re.search(b,d['answer'])!=None:
        flag='A'
    
    t_flag=dct.get(s)
    if t_flag is not None and t_flag==flag:
        f.write(json.dumps(d,ensure_ascii=False)+'\n')
        true_dct.update({s:d})
    else:
        w.write(json.dumps(d,ensure_ascii=False)+'\n')
        false_dct.update({s:d})

#data2=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/from_qa_test/0613/merge.json','r').readlines()]
data2=[json.loads(x) for x in open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20231015/llama-13b-gpt4_llm_comparision2_clean-231536/0613merge.jsoneval','r').readlines()]
with open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20231015/llama-13b-gpt4_llm_comparision2_clean-231536/0613merge_gpt4label.jsoneval','w') as f:
    for d in data2:
        s=d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']
        if s in true_dct.keys():
            d['gpt4_flag']=True
        elif s in false_dct.keys():
            d['gpt4_flag']=False
        f.write(json.dumps(d,ensure_ascii=False)+'\n')
