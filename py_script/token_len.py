from transformers import LlamaTokenizer
import os
import json
prompt_input = ("A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: {question} ASSISTANT: ")
name='/nlp_group/mlflow_monitor/sft/bft/bft_bft_multi_full-197911-20231011-dpo1/artifacts/global_step1161'
tokenizer=LlamaTokenizer.from_pretrained(name)
files=[]
#common
# files+= [
#     "/nlp_group/chenzhengzong/rm_dataset/RM/Anthropic_hh-rlhf/merge_cate_sample50/merge",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/prm800k/merge_cate_sample50/merge",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/webgpt_comparisons/split_train_clean.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/merge/20230708/merge1647",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/merge/20230701/merge1648",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230907/filterid_fix_merge1852",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230907/filterid_fix_merge1737",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230830/filterid_fix_shuffle_5w_merge1456_1500_math_ambiguous_num.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbad_exp102ppo_infer_gsm8k_new.jsonl_splited.json_with_id.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbad_ppo2exp10_infer_gsm8k_new.jsonl_splited.json_with_id.json",
#     "/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_ans_select_gap5_filter_uniq.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/PKU-SafeRLHF/round0/format_train_chosen_2_0.jsonl",
#     "/nlp_group/chenzhengzong/rm_dataset/infer_new/columbus_bk/utility/outputs/merge_0613_ans_select_gap5_filterv2_uniq.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0809/safety_pair_04_24.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/stanfordnlp_SHP/filter_ratio_sample15w.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/summarize_from_feedback/train.json.cat.results.scp",
#     "/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_Anthropic_hh-rlhftrain.json.cat.results.scp_harmlessevalfalse_log_test_gpt35_chosen_pair_thres4.log",
#     "/nlp_group/chenzhengzong/rm_dataset/gpt4_api/merge_filter_ratio_sample15w_false_gpt35_chosen_pair_thres4.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/ultrachat_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/truthful_qa_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/sharegpt_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/flan_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/false_qa_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/RM/UltraFeedback/general/evol_instruct_format_pair_thres2.json",
#     "/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres3_shuf_train.json",
#     "/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres2_shuf_train.json",
#     "/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres1_shuf_train.json"
#   ]
# # path='/nlp_group/chenzhengzong/for_sft_infer/rm_data/general'
# # files=[path+'/'+x for x in os.listdir(path)]

#test
# files+=[
#     '/nlp_group/chenzhengzong/rm_dataset/RM/from_qa_test/0613/merge.json',
#     '/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_math_test_5_15.json',
#     '/nlp_group/chenzhengzong/rm_dataset/RM/webgpt_comparisons/split_test_clean.json',
#     '/nlp_group/chenzhengzong/rm_dataset/RM/Anthropic_hh-rlhf/test.json.cat.results.scp_label',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres2_shuf_test.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres1_shuf_test.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhendui/zhendui_prompt_filter_ans_chosen_pair_thres3_shuf_test.json',
#     '/nlp_group/chenzhengzong/rm_dataset/RM/stanfordnlp_SHP/test.json'
#     ]

# # files=['/nlp_group/chenzhengzong/rm_dataset/RM/summarize_from_feedback/valid.json.cat.results.scp']
# #针对v2-1
# files+=[
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_test_chosen_pair_thres1.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_test_chosen_pair_thres2.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_test_chosen_pair_thres3.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres1.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres2.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres3.json',
# ]
# #针对v2-2
# files+=[
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres3max2.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres2max2.json',
#     '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres1max2.json',
# ]
files+=[
    '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres3max2bk.json',
    '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres2max2bk.json',
    '/nlp_group/chenzhengzong/rm_dataset/gpt4_api/gpt4_zhenduiv2/step2/zhendui_prompt_filter_gpt4ans_cate_shuf_train_chosen_pair_thres1max2bk.json',
]
#math
#files+=[
#    "/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/merge_from_num_v6_8.json_merge",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/math_fix_t2f.txt.cat.results.scp_merge",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0607/math_fix_t2f.txt.cat.results.scp_merge",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/fix_merge_from_num_calc_v2.json",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbadv3_exp10_0816_infer10_小学数学188.json_with_id.json_repeat5.json_add_tag.jsonl_merged.json ",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbadv2_exp10_0816_infer10_test.jsonl_new.jsonl_with_id.json_add_tag.jsonl_repeat5.json_merged.json",
#    "/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbad_exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag.jsonl",
#]
with open('./tokenizer_out_list','a') as w:
    thres=512
    w.write("gt"+str(thres)+'\n')
    for f in files:
        sp=f.split('.')
        prefix=sp[0]
        sufix=sp[1] if len(sp)==2 else ""
        l_f=prefix+'_lt'+str(thres)+sufix
        g_f=prefix+'_gt'+str(thres)+sufix
        count=0
        data=[json.loads(x) for x in open(f).readlines()]
        with open(l_f,'w') as lf, open(g_f,'w') as gf:
            for info in data:
                ans1=len(tokenizer(prompt_input.format(question=info['input'])+info['candidates'][0]['output'])['input_ids'])
                ans2=len(tokenizer(prompt_input.format(question=info['input'])+info['candidates'][1]['output'])['input_ids'])
                if ans1>thres or ans2>thres:
                    gf.write(json.dumps(info,ensure_ascii=False)+'\n')
                    count+=1
                else:
                    lf.write(json.dumps(info,ensure_ascii=False)+'\n')
        # for info in data:
        #     ans1=len(tokenizer(prompt_input.format(question=info['input'])+info['candidates'][0]['output'])['input_ids'])
        #     ans2=len(tokenizer(prompt_input.format(question=info['input'])+info['candidates'][1]['output'])['input_ids'])
        #     if ans1>thres or ans2>thres:
        #         count+=1
        w.write(f+":"+str(count)+'\n')
