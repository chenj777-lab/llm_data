import json
import re
import os

def str_clean(input):
    clean_numstr=input.replace("（1）","").replace("（2）","").replace("（3）","").replace("（4）","").replace("（5）","")
    clean_numstr2=clean_numstr.replace("1. ","").replace("2. ","").replace("3. ","").replace("4. ","").replace("5. ","")
    clean_numstr3=clean_numstr2.replace("1、 ","").replace("2、 ","").replace("3、 ","").replace("4、 ","").replace("5、 ","")
    return clean_numstr3

def clean_from_labeler(r_f,w_f):
    with open(w_f,'w') as f:
        fix={}
        true_dct={}
        d=[json.loads(x) for x in open(r_f).readlines()]
        l=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_label/0901_rm_zz.json').readlines()]
        for i in l:
            if "答案错误" in i['result']:
                fix[i['a']]=False
                continue
            #仅对非确保正确的答案做过滤
            if "答案正确" in i['result']:
                true_dct[i['a']]=True
        for i in d:
            if i['candidates'][0]['output'] in fix.keys():
                continue
            # if i['candidates'][0]['output'] not in true_dct.keys():
            #     continue
            f.write(json.dumps(i, ensure_ascii=False)+'\n')

def readf_selfconsis(savefile,file):
  data=[json.loads(x) for x in open(file).readlines()]
  with open(savefile,'w') as f:
    for d in data:
      for j in range(1,1000):
        input={}
        if 'answer'+str(j) not in d.keys():
          continue
        input['index']=d['index']+"_"+str(j)
        input['question']=d['question']
        input['answer']=d['answer'+str(j)]['content']
        input['other']=d['answer'+str(j)]
        f.write(json.dumps(input,ensure_ascii=False)+'\n')
      
def decodef_selfconsis(real_ans_f,file,savefile):
  real_dict={}
  real_data=[json.loads(x) for x in open(real_ans_f).readlines()]
  real_data+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag.jsonl').readlines()]
  data=[json.loads(x) for x in open(file).readlines()]
  for i in real_data:
    real_ans=i['real_ans'].replace(',',"")
    num=re.findall('([0-9]+)',str_clean(real_ans),re.S)
    real_dict.update({i['question']:num[-1]})
  with open(savefile,'w') as f:
    for i in data:
      ans_str=i['extract_answer'].replace(',',"")
      num=re.findall('([0-9]+)',ans_str,re.S)
      if len(num)>0:
        ans=float(num[-1])
        real_ans=float(real_dict.get(i['question']))
        if real_ans is not None:
          i['real_ans']=real_ans
          if ans==real_ans:
            i['flag']=True
          else:
            i['flag']=False
      else:
        i['flag']=None
      f.write(json.dumps(i,ensure_ascii=False)+'\n')
      

def clean_from_sc(totag_file,fixfile,toclean_file):
    with open(fixfile,'w') as f:
        fix={}
        d=[json.loads(x) for x in open(toclean_file).readlines()]
        l=[json.loads(x) for x in open(totag_file).readlines()]
        for i in l:
            if i['flag']==False:
                fix[i['answer']]=False
        print("len(fix):",len(fix))
        for i in d:
            if i['candidates'][0]['output'] in fix.keys():
                continue
            f.write(json.dumps(i, ensure_ascii=False)+'\n')

def clean_from_fjy(tofilter_index,tofilter_file,fix_file):
    filter_data=[x for x in open(tofilter_index).readlines()]
    tofilter_data=[json.loads(x) for x in open(tofilter_file).readlines()]
    math_data=[json.loads(x)['idx'] for x in open('/nlp_group/fujiayi/data/math_base/afanti_train/merge_math_0904.json').readlines()]
    with open(fix_file,'w') as f:
        for i in tofilter_data:
            if i['id'] in filter_data:
                continue
            if i['id'] not in math_data:
                continue
            f.write(json.dumps(i, ensure_ascii=False)+'\n')


#功能2:清洗sc返回数据
# screturn_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_selfconsis/sc_exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag_extract-answer.jsonl'
# totag_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_selfconsis/sc_exp10_0816_infer10_test.jsonl_new.jsonl_with_id.json_add_tag.jsonl_repeat5.json_merged_extract-answer_tag.json'
# real_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0816_infer10_test.jsonl_new.jsonl_with_id.json_add_tag.jsonl_repeat5.json_merged.json'
# toclean_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/goodbad_exp102ppo_infer_gsm8k_new.jsonl_splited.json_with_id.json'
# fix_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbad_exp102ppo_infer_gsm8k_new.jsonl_splited.json_with_id.json'
# # decodef_selfconsis(real_file,screturn_file,totag_file)
# clean_from_sc(totag_file,fix_file,toclean_file)



#功能1:清洗非数学及标注返回数据
# f=['/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230830/fix_shuffle_5w_merge1456_1500_math_ambiguous_num.json','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/fix_goodbadv2_exp10_0816_infer10_小学数学188.json_with_id.json_repeat5.json_add_tag.jsonl_merged.json']
# filterid_f=['/nlp_group/chenzhengzong/rm_dataset/RM/for_math/filterid_exp10_0817_infer10_afanti-math-all-train_infer_data.json_1.json_2_3.json_add_tag.jsonl','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230830/filterid_fix_shuffle_5w_merge1456_1500_math_ambiguous_num.json','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/filterid_fix_goodbadv2_exp10_0816_infer10_小学数学188.json_with_id.json_repeat5.json_add_tag.jsonl_merged.json']
f=['/nlp_group/chenzhengzong/rm_dataset/RM/for_math/merge/20230918/merge1637']

for i in range(len(f)):
    path=os.path.dirname(f[i])
    file_basename=os.path.basename(f[i])
    fix_f=os.path.join(path,'fix_'+file_basename)
    filter_f=os.path.join(path,'filterid_fix_'+file_basename)
    clean_from_labeler(f[i],fix_f)
    clean_from_fjy('/nlp_group/fujiayi/data/for_pengli/afanti/bad_qid.txt',fix_f,filter_f)


