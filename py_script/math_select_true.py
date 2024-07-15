#sft infer数据的样本筛选并构造pair
from difflib import SequenceMatcher
import json
import os
from collections import defaultdict
import re

#对哪一类样本做pair构造及筛选
dirname='./math/'
filename='zh_math_ans.json'
dct={}
ans_source={}
ans_score={}
source_key='sft_infer_exp10'
ans_source2={}
cate_level1={'./math/':"逻辑类",'./changshituili/':"逻辑类",'./common_knowledge/':"知识类"}
cate_level2={'./math/':"数学计算",'./changshituili/':"常识推理",'./common_knowledge/':"常识"}

#此处对于数学、常识包含id、input等前俩key,因此设置为2;通用知识包含input一个key，因此设置为1
prefix_keynums={'./math/':2,'./changshituili/':1,'./common_knowledge/':2}

#从sft回答的哪一行开始及哪一行结束
#begin_index=501
#end_index=3500
begin_index=3501
end_index = 6000
log_filename=os.path.join(dirname,'uniq_'+str(begin_index)+'_'+str(end_index)+filename)
pair_filename=os.path.join(dirname,'pair_uniq_'+str(begin_index)+'_'+str(end_index)+filename)

prefix_keynum=prefix_keynums[dirname] #此处对于常识类包含id、input等前俩key,因此设置为2;
pair_index=1
same_pct=0.6

kv=[5,6,7,8,10,11,12,13,14,15]
def readf_v2(savefile,file):
  data=[json.loads(x) for x in open(file).readlines()]
  with open(savefile,'w') as f:
    for d in data:
      if not d.get('is_200_test') or d['exp5得分']=='':
        continue
      input={}
      input['index']=d['index']
      input['question']=d['question_x']
      input['real_ans']=d["参考答案"] if d.get("参考答案") is not None else d['real_ans']
      ans_source.update({input['real_ans']:'real_ans'})
      for i in range(len(kv)):
        input['answer'+str(i)]={'content':d['exp'+str(kv[i])+'_answer'],'tag':str(5*int(not d["is_exp"+str(kv[i])+"_badcase"]))+'/5'}
        before=None
        before=ans_source.get(d['exp'+str(kv[i])+'_answer'])
        ans_source.update({d['exp'+str(kv[i])+'_answer']:'sft_infer_exp'+str(kv[i]) if before is None else before+"_"+'sft_infer_exp'+str(kv[i])})
      input['metas']={}
      input['metas']['一级类目']=d['level1']
      input['metas']['二级类目']=d['level2']
      f.write(json.dumps(input,ensure_ascii=False)+'\n')

def readf(savefile,file):
  data=[json.loads(x) for x in open(file).readlines()]
  with open(savefile,'w') as f:
    for d in data:
      if not d.get('is_200_test') or d['exp5修正']=='':
        continue
      input={}
      input['index']=d['index']
      input['question']=d['question_x']
      input['real_ans']=d["参考答案"] if d.get("参考答案") is not None else d['real_ans']
      input['answer1']={'content':d['exp5_answer'],'tag':str(int(d["exp5修正"]))+'/5'}
      input['answer2']={'content':d['exp6_answer'],'tag':str(int(d["exp6修正"]))+'/5'}
      input['answer3']={'content':d['exp7_answer'],'tag':str(int(d["exp7修正"]))+'/5'}
      input['answer4']={'content':d['exp8_answer'],'tag':str(int(d["exp8修正"]))+'/5'}
      input['answer5']={'content':d['exp10_answer2'],'tag':str(int(d["answer2修正"]))+'/5'}
      ans_source.update({input['real_ans']:'real_ans'})
      before=ans_source.get(d['exp5_answer'])
      ans_source.update({d['exp5_answer']:'sft_infer_exp5' if before is None else before+"_"+'sft_infer_exp5'})
      before=None
      before=ans_source.get(d['exp6_answer'])
      ans_source.update({d['exp6_answer']:'sft_infer_exp6' if before is None else before+"_"+'sft_infer_exp6'})
      before=None
      before=ans_source.get(d['exp7_answer'])
      ans_source.update({d['exp7_answer']:'sft_infer_exp7' if before is None else before+"_"+'sft_infer_exp7'})
      before=None
      before=ans_source.get(d['exp8_answer'])
      ans_source.update({d['exp8_answer']:'sft_infer_exp8' if before is None else before+"_"+'sft_infer_exp8'})
      before=None
      before=ans_source.get(d['exp10_answer2'])
      ans_source.update({d['exp10_answer2']:'sft_infer_exp10' if before is None else before+"_"+'sft_infer_exp10'})
      f.write(json.dumps(input,ensure_ascii=False)+'\n')


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
      
    

#对多个相似的回答做过滤
def filter_repeat():
  with open(dirname+filename,encoding='utf-8') as f,open(pair_filename,'w',encoding='utf-8') as p, open(log_filename,'w',encoding='utf-8') as w:
    count_line=0
    while True:
      line = f.readline()
      count_line+=1
      if not line or count_line>end_index: #取出需要拆解的行信息
        break
      if count_line<begin_index:
        continue
      jl=json.loads(line)
      common_key={}
      input={}
      count=0
      for i,j in enumerate(jl):
        if i>=len(jl)-prefix_keynum: #此处对于常识类包含id、input等前俩key,因此设置为2，
          continue
        key1="answer"+str(i)
        for k in range(i+1,len(jl)-prefix_keynum): #此处包含id、input等前俩key
          case1=jl[key1]
          key2="answer"+str(k)
          case2=jl[key2]
          match = SequenceMatcher(None, case1, case2).find_longest_match(0,len(case1),0,len(case2))
          if match.size >= len(case1)*same_pct: #此处决定60%以上相似则舍弃
            common_key[key1]=1
            break
          elif match.size >= len(case2)*same_pct:
            common_key[key2]=1
        input['input']=jl['input']
        
        if common_key.get(key1)==None:
          count+=1
          pair={}
          for k,v in enumerate(input):
            if v=='input':
              continue
            pair['input']=jl['input']
            pair['id']=pair_index
            pair['ans1']=jl[key1]
            pair['ans2']=input[v]
            pair['cate_level1']=cate_level1[dirname]
            pair['cate_level2']=cate_level2[dirname]
            pair_index+=1
            #with open(pair_filename,'a',encoding='utf-8') as w:
            p.write(json.dumps(pair,ensure_ascii=False)+'\n')
          input["answer"+str(count)]=jl[key1]
          

      #with open(log_filename,'a',encoding='utf-8') as w:
      w.write(json.dumps(input,ensure_ascii=False)+'\n')

# a="我不能坐得太靠近电视，因为这样会对我的眼睛和健康造成不良影响。电视屏幕发出的蓝光会损害视网膜，导致视力下降。此外，坐得太靠近电视还可能导致颈椎和腰椎疼痛，影响身体健康。因此，为了保护眼睛和身体健康，我们应该保持适当的观看距离。"
# b="我不能坐得太靠近电视，因为这样会对我的眼睛和健康造成不良影响。电视屏幕发出的蓝光会损害视网膜，导致视力下降。此外，坐得太靠近电视还可能导致颈椎和腰椎疼痛，影响身体健康。因此，为了保护眼睛和身体健康，我们应该保持适当的观看距离。一般来说，观看距离应与屏幕尺寸成比例，例如，观看50英寸的电视时，观看距离应保持在3米左右。"

def str_clean(input):
    clean_numstr=input.replace("（1）","").replace("（2）","").replace("（3）","").replace("（4）","").replace("（5）","")
    clean_numstr2=clean_numstr.replace("1. ","").replace("2. ","").replace("3. ","").replace("4. ","").replace("5. ","")
    clean_numstr3=clean_numstr2.replace("1、 ","").replace("2、 ","").replace("3、 ","").replace("4、 ","").replace("5、 ","")
    return clean_numstr3

#找出标注的正确答案，并把当前infer的数据提取错误的答案
def filter_goodans(name,file):
    # if os.path.exists(name):
    #   return
    # file='/nlp_group/bufordyang/llmbenchmark/data_infer/exp10_0816_infer10_小学数学188.json_with_id.json_repeat5.json_add_tag.jsonl_merged.json'
    filter=defaultdict(dict)
    #需要过滤正确答案的数据
    tofilterdata=[json.loads(x) for x in open(file).readlines()]
    with open(name,'w') as f:
        for d in tofilterdata:
            count=0
            input={}
            input['id']=d['index'] if 'index' in d.keys() else d['id']
            input['input']=d['question']
            if 'real_ans'  in d.keys():
                ans=d['real_ans']
            if ans is None:
                continue
            num=re.findall('([0-9]+)',str_clean(ans),re.S)
            for i in range(1,1000):
                if 'answer'+str(i) not in d.keys():
                  break
                #print(d.get('answer'+str(i)))
            # for i in range(len(kv)):
                #i=i+1
                #print(d)
                score_str=d['answer'+str(i)]['tag']
                score=100
                if score_str=='5/5':
                    score=4
                elif score_str=='4/5':
                    score=4
                elif score_str=='3/5':
                    score=4
                elif score_str=='2/5':
                    score=float(2)
                elif score_str=='1/5':
                    score=float(2*0.5)
                elif score_str=='0/5':
                    score=float(2*0)
                elif score_str=='3/3':
                    score=4
                elif score_str=='2/3':
                    score=4
                elif score_str=='1/3':
                    score=float(2)
                elif score_str=='0/3':
                    score=float(2*0)
                elif score_str=='1/1':
                    score=4
                elif score_str=='0/1':
                    score=2
                elif score_str=='4/4':
                    score=4
                elif score_str=='3/4':
                    score=4
                elif score_str=='2/4':
                    score=2
                elif score_str=='1/4':
                    score=0
                elif score_str=='0/4':
                    score=0
                #get infer num,gpt打低且数字不匹配的才作为负样本
                infernum=re.findall('([0-9]+)',str_clean(d['answer'+str(i)]['content']),re.S)
                if (len(infernum)>0 and len(num)>0 and num[-1]==infernum[-1]) or (len(infernum)>1 and len(num)>0 and num[-1]==infernum[0]) and score==2:
                    score=4
                    #print(d,'#########good num',i)
                if score!=4 and score!=100:
                    input['answer'+str(count)]=d['answer'+str(i)]['content']
                    ans_score.update({d['question']+d['answer'+str(i)]['content']:score})
                    ans_source.update({d['question']+d['answer'+str(i)]['content']:d['answer'+str(i)]['source'] if 'source' in d['answer'+str(i)].keys() else  source_key})
                    ans_source2.update({d['question']+d['answer'+str(i)]['content']:source_key})
                    count+=1
            f.write(json.dumps(input, ensure_ascii=False)+'\n')


def select_goodans(name,file):
    # if os.path.exists(name):
    #   return
    #dct={}
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    labeldata1=[json.loads(x) for x in open(file).readlines()]
    filter=defaultdict(dict)

    for d in labeldata1:
        #get true num
        if 'real_ans'  in d.keys():
          ans=d['real_ans']
          if ans is None:
            continue
          num=re.findall('([0-9]+)',str_clean(ans),re.S)
        #   if len(num)==0:
        #     continue
          if len(num)>0:
            filter[d['question']]=num[-1]

        for i in range(1,1000):
            if 'answer'+str(i) not in d.keys():
              break
            score_str=d['answer'+str(i)]['tag']
            score=0
            if score_str=='5/5':
                score=4
            elif score_str=='4/5':
                score=2
            elif score_str=='3/5':
                score=2
            elif score_str=='2/5':
                score=2
            elif score_str=='1/5':
                score=2
            elif score_str=='0/5':
                score=2
            elif score_str=='3/3':
                score=4
            elif score_str=='2/3':
                score=2
            elif score_str=='1/3':
                score=2
            elif score_str=='0/3':
                score=2
            elif score_str=='1/1':
                score=4
            elif score_str=='0/1':
                score=2
            elif score_str=='4/4':
                score=4
            elif score_str=='3/4':
                score=2
            elif score_str=='2/4':
                score=2
            elif score_str=='1/4':
                score=2
            elif score_str=='0/4':
                score=2
            #get infer num,gpt打高且数字匹配的才作为正样本
            infernum=re.findall('([0-9]+)',str_clean(d['answer'+str(i)]['content']),re.S)
            if (len(infernum)>0 and len(num)>0 and num[-1]!=infernum[-1]) and (len(infernum)>1 and len(num)>0 and num[-1]!=infernum[0]) and score==4:
              score=2
              #print(d,'#########mistake num',i)

            #对每一个好坏样本，记录分数
            if d['question']+d['answer'+str(i)]['content'] in  dct.keys():
                dct[d['question']+d['answer'+str(i)]['content']].append(score)
            else:
                dct[d['question']+d['answer'+str(i)]['content']]=[]
                dct[d['question']+d['answer'+str(i)]['content']].append(score)

    new_data = defaultdict(dict)
    for d in labeldata1:
        for i in range(1,1000):
            if 'answer'+str(i) not in d.keys():
                break
            score_str=d['answer'+str(i)]['tag']
            key_list_score1=dct.get(d['question']+d['answer'+str(i)]['content'])
            if key_list_score1 is None:
                #print("not get",d['answer'+str(i)])
                continue
            mean_num1 = sum(key_list_score1)/len(key_list_score1)
            if mean_num1 <2:
                mean_num1 = 0
            elif mean_num1 < 4:
                mean_num1 = 2

            if d['question'] not in new_data.keys():
                new_data[d['question']]=defaultdict(dict)

            if mean_num1==4 and d['answer'+str(i)]['content'] not in new_data[d['question']].keys():
                new_data[d['question']][d['answer'+str(i)]['content']]=4
                ans_source.update({d['question']+d['answer'+str(i)]['content']:d['answer'+str(i)]['source'] if 'source' in d['answer'+str(i)].keys() else  source_key})
                ans_source2.update({d['question']+d['answer'+str(i)]['content']:source_key})
                ans_score.update({d['question']+d['answer'+str(i)]['content']:4})
    if 'ppo' not in file:
      for d in labeldata1:
          if 'real_ans' not in d.keys():
            continue
          input={}
          input['input']=d['question']
          if d['question'] not in new_data.keys():
            new_data[d['question']]=defaultdict(dict)
          new_data[d['question']][d['real_ans']]=4
          ans_source.update({d['question']+d['real_ans']:'sft_realans'})
          ans_source2.update({d['question']+d['real_ans']:'sft_realans'})
          ans_score.update({d['question']+d['real_ans']:4})
        
        

    with open(name,'w') as f:
        f.write(json.dumps(new_data, ensure_ascii=False)+'\n')
    return 

def pair_goodandfalse(badname,goodname,file):
  falses=[json.loads(x) for x in open(badname).readlines()]
  goods=[json.loads(x) for x in open(goodname).readlines()]
  #dct={}
  with open(file,'w') as f:  
    for d in falses:
      good=goods[0].get(d['input'])
      id=d['id']
      if good is not None:
        for fk,fv in d.items():
          if 'answer' not in fk:
            continue
          q_a=d['input']+fv
          # if q_a in dct.keys():
          #   print(q_a)
          #   continue
        #   ans1num=re.findall('([0-9]+)',fv,re.S)
        #   dct.update({q_a:ans1num[-1]})
          for gk,gv in good.items():
            q_a2=d['input']+gk
            # if q_a2 in dct.keys():
            #   continue
            # ans2num=re.findall('([0-9]+)',gk,re.S)
            # if len(ans2num)==0:
            #   break
            # dct.update({q_a2:ans2num[-1]})
            #避免错误的答案与正确的答案相同
            # if ans2num[-1]==ans1num[-1]:
            #   break
            data={}
            candidates=[]
            data['input']=d['input']
            data['id']=id
            candidates.append({
                "output":gk,
                "source":ans_source.get(data['input']+gk),
                "chosen":ans_score.get(data['input']+gk)
            })
            candidates.append({
                "output":fv,
                "source":ans_source.get(data['input']+fv),
                "chosen":ans_score.get(data['input']+fv)
            })
            data['candidates']=candidates
            f.write(json.dumps(data, ensure_ascii=False)+'\n')   
#rdfile='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp5-15.json'
# file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0817_infer10_afanti-math-all-train_infer_data.json_3.json_2.json_add_tag.jsonl'
# badname='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/bad_exp10_0817_infer10_afanti-math-all-train_infer_data.json_3.json_2.json_add_tag.jsonl'
# goodname='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/good_exp10_0817_infer10_afanti-math-all-train_infer_data.json_3.json_2.json_add_tag.jsonl'
# #readf_v2(file,rdfile)
# filter_goodans(badname,file)
# select_goodans(goodname,file)
# pair_goodandfalse(badname,goodname)
# match = SequenceMatcher(None, a, b).find_longest_match(0,len(a),0,len(b))
# print(a[match.a:match.a+match.size])
# 我不能坐得太靠近电视，因为这样会对我的眼睛和健康造成不良影响。电视屏幕发出的蓝光会损害视网膜，导致视力下降。此外，坐得太靠近电视还可能导致颈椎和腰椎疼痛，影响身体健康。因此，为了保护眼睛和身体健康，我们应该保持适当的观看距离。
# print(b[match.b:match.b+match.size])

file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0817_infer10_afanti-other-math-0812_infer_data.jsonl_5.json_add_tag.jsonl'
ppo_file='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/ppo_infer_gsm8k_new.jsonl_splited.json_with_id.json'
path=os.path.dirname(file)
file_basename=os.path.basename(file)
badname=os.path.join(path,'bad_'+file_basename)
goodname=os.path.join(path,'good_'+file_basename)
gbname=os.path.join(path,"goodbad_"+file_basename)
#goodname='/nlp_group/chenzhengzong/rm_dataset/RM/for_math/good_ppo_infer_gsm8k_new.jsonl_splited.json_with_id.json'
#readf_v2(file,rdfile)

filter_goodans(badname,file)
select_goodans(goodname,file)
pair_goodandfalse(badname,goodname,gbname)

####
# readf_selfconsis('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_selfconsis/sc_exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag.jsonl','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_infer10_gsm8k_train_format.jsonl_new.jsonl_with_id.json_infer_data.json_add_tag.jsonl')



#decodef_selfconsis('/nlp_group/chenzhengzong/rm_dataset/RM/for_math/exp10_0816_infer10_test.jsonl_new.jsonl_with_id.json_add_tag.jsonl_repeat5.json_merged.json','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_selfconsis/sc_ppo_infer_gsm8k_new.jsonl_splited.json_with_id_extract-answer.json','/nlp_group/chenzhengzong/rm_dataset/RM/for_math/for_selfconsis/sc_ppo_infer_gsm8k_new.jsonl_splited.json_with_id_extract-answer_tag.json')
