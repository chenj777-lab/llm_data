from datasets import load_dataset
import argparse
import json
import re
from functools import reduce
import os
#cate_list=['数学计算','计算机编程','常识推理']
#cate_list=['垂类-数学']
cate_list=[]
def remove_list_dict_duplicate(list_dict_data):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + list_dict_data)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Eval the finetued reward model")
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        help=
        "Path to pretrained model or model identifier from huggingface.co/models.",
        required=True,
    )
    parser.add_argument(
        "--file_name",
        type=str,
        default=0,
        help=
        "OPT model has a fixed number (1) of padding tokens at the beginning of the input. "
        "We did not see this in other models but keep it as an option for now.",
    )
    parser.add_argument(
        "--thres",
        type=int,
        default=0,
        help=
        "OPT model has a fixed number (1) of padding tokens at the beginning of the input. "
        "We did not see this in other models but keep it as an option for now.",
    )
    args = parser.parse_args()
    return args
args = parse_args()
path=args.model_name_or_path
name=args.file_name
#name=os.path.basename(os.path.dirname(name)) + os.path.basename(name)+'eval'
dct={}
#name= os.path.basename(name)#+'eval'
#path='/aigc_sgply_ssd/chenzhengzong/glb_rewardmodel/output_eval_20230523/rm-llama-test_dataset-bs1-len512-lora0-naive-20230523_150438-eval/'
#path='/cpfs01/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230615/llama-7b-gpt4_llm_comparision2_clean-195654/'
#path='/cpfs01/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230616/llama-7b-gpt4_llm_comparision2_clean-143833'
#path='/aigc_sgply_ssd/chenzhengzong/dd/deepspeedexamples/applications/DeepSpeed-Chat/training/step2_reward_model_finetuning/output_train_20230601/llama-7b-gpt4_llm_comparision2_clean-141554/'
with open(path+'/'+name+'true_log_test.log2','w',encoding='utf-8') as t,open(path+'/'+name+'false_log_test.log2','w',encoding='utf-8') as nt,open(path+'/eval_result.log','a',encoding='utf-8') as e:
  count=0
  total=0
  data=[json.loads(x) for x in open(os.path.join(path,name)).readlines()]
  data=remove_list_dict_duplicate(data)
  count3=0
  count2=0
  count1=0
  for j in data:
    #if len(cate_list)> 0 and j['metas']['二级标签'] not in cate_list:
    #  continue
    val=j['input']+j['candidates'][0]['output']+j['candidates'][1]['output']
    if val in dct.keys():
      continue
    dct.update({val:True})
    if len(cate_list)> 0 and j['category'] not in cate_list:
      continue
    if 'chosen' in j['candidates'][0].keys() and j['candidates'][0]['chosen']==j['candidates'][1]['chosen']:
      continue
    if args.thres!=0:
      if int(j['candidates'][0]['chosen'])-int(j['candidates'][1]['chosen'])>=args.thres+1 or int(j['candidates'][0]['chosen'])-int(j['candidates'][1]['chosen'])<args.thres:
          continue
    human_score1=j['candidates'][0]['rm_score']
    human_score2=j['candidates'][1]['rm_score']
    total=total+1
    if human_score1>human_score2:
      count=count+1
      t.write(json.dumps(j,ensure_ascii=False)+'\n')
    else:
        nt.write(json.dumps(j,ensure_ascii=False)+'\n')
        #print(j)
  print(count)
  print(total)
  print(count/total,path,name)
  e.write(str(count/total)+path+name+'\n')
