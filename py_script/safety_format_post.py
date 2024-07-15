import json
import re

data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20231010/llama-13b-gpt4_llm_comparision2_clean-181336/sft_safepolity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.0_neweval').readlines()]
dct={}
with open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20231010/llama-13b-gpt4_llm_comparision2_clean-181336/sft_safepolity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.0_neweval_true','w') as i, open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20231010/llama-13b-gpt4_llm_comparision2_clean-181336/sft_safepolity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.0_neweval_amb','w') as a:
    for d in data:
        num_str=re.findall('([0-9])\n',d['other'],re.S)
        if len(num_str)==0:
            continue
        num=int(num_str[-1])
        index_str=d['input']+d['id'][:-1]
        prompt=dct.get(index_str)
        if prompt is None:
            dct.update({index_str:num})
        else:
            result=(prompt-3)*(num-3)
            if result >0:
                a.write(json.dumps(d, ensure_ascii=False)+'\n')
            elif result==0:
                continue
            else:
                i.write(json.dumps(d, ensure_ascii=False)+'\n')


# data=[json.loads(x) for x in open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230911/llama-13b-gpt4_llm_comparision2_clean-212654/sft_safepolity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.2eval').readlines()]
# data2=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/sft_safe/polity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.2_new').readlines()]

# dct={}

# for d in data:
#     a1=d['input']+d['candidates'][0]['output']
#     a2=d['input']+d['candidates'][1]['output']
#     dct.update({a1:d['candidates'][0]['rm_score']})
#     dct.update({a2:d['candidates'][1]['rm_score']})
# with open('/nlp_group/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230911/llama-13b-gpt4_llm_comparision2_clean-212654/sft_safepolity_ans_pair_1k_prompt_for_chatgpt_v1_ans_gpt4.json.2eval_new','w') as f:
#     for d in data2:
#         a1=d['input']+d['candidates'][0]['output']
#         a2=d['input']+d['candidates'][1]['output']
#         score1=dct.get(a1)
#         score2=dct.get(a2)
#         d['candidates'][0]['rm_score']=score1
#         d['candidates'][1]['rm_score']=score2
#         f.write(json.dumps(d, ensure_ascii=False)+'\n')
    
