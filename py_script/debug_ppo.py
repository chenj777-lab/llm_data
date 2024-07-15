# import pandas
# import re
# import json
# c=pandas.read_csv('/nlp_group/mlflow_monitor/rl/test/test_fixkl0001_5en6_rscale_8epoch_exp10rmv2_gsm8k_bs12_z3/artifacts/game_log_7_0.csv')
# p=[]
# with open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230824/llama-13b-gpt4_llm_comparision2_clean-200435/debug_ppo','w') as f:
#     for i,j in enumerate(c['reward']):
#         input={}
#         w={}
#         if j>1:
#             input['prompt']=re.findall("A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: (.*) ASSISTANT:",c['prompt'][i],re.S)[0]
#             input['response']=c['response'][i]
#             input['chosen']=j
#             p.append(input)
#     f.write(json.dumps(p, ensure_ascii=False)+'\n')

#拼接ppo infer的数据至标准格式，利用数据抽取
import pandas
import re
import json
import os

dct={}
file_path='/mmu-audio-ssd/business/mlflow/test/test_test/artifacts/'
file_names = os.listdir(file_path)



#功能，根据ppo infer数据构造成1Vn的ans给gpt打分
#标准答案
data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0816_infer10_test.jsonl_new.jsonl_with_id.json_add_tag.jsonl_repeat5.json_merged.json').readlines()]
data+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag.jsonl').readlines()]
real_ans={}
ids={}
for d in data:
    if real_ans.get(d['question']) is None:
        real_ans[d['question']]=d['real_ans']
        ids[d['question']]=d['index']
#file_list=['test_fixkl0001_5en6_rscale_8epoch_exp10rmv2_gsm8k_bs12_z3','test_fixkl1_5en6_rscale_8epoch_exp10rmv2_gsm8k_bs12_z3']
with open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/from_ppo/debug_only','w') as f:
    for k in file_names:
        file=file_path+k
        c=pandas.read_csv(file)
        #print(len(c['response']))
        for i,j in enumerate(c['reward']):
            input={}
            w={}
            input['prompt']=re.findall("A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: (.*) ASSISTANT:",c['prompt'][i],re.S)[0]
            input['response']=c['response'][i]
            input['chosen']=j
            input['source']='ppo_infer_'+str(k)
            if dct.get(input['prompt']) is None:
                dct[input['prompt']]=[input]
            else:
                dct[input['prompt']].append(input)
            #f.write(json.dumps(input, ensure_ascii=False)+'\n')
    for i,j in dct.items():
        content={}
        content['prompt']=i
        content['id']=ids[i] if i in ids.keys() else None
        content['real_ans']=real_ans[i] if i in real_ans.keys() else None
        for index,val in enumerate(j):
            content['answer'+str(index)]={'content':val['response'],'source':val['source'],'reward':val['chosen']}
        f.write(json.dumps(content, ensure_ascii=False)+'\n')

