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

#找出标注的正确答案，并把当前infer的数据提取错误的答案
def filter_goodans(name):
    filter=defaultdict(dict)
    #标注的正确答案
    labeldata1=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/sft_infer_data2').readlines()]
    labeldata1+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0607/sft_infer_data1').readlines()]
    labeldata1+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0523/sft_sample_48k_0523.json').readlines()]
    #需要过滤正确答案的数据
    tofilterdata=[json.loads(x) for x in open('/aigc_sgply_ssd/rl/RM/sft_sample_0517/math/zh_math_ans_v2.json').readlines()]
    #人工书写的正确答案
    labeldata2=[json.loads(x) for x in open('/nlp_group/liupengli/workdir/openai-api/anno/res/writer_true_ans').readlines()]
    labeldata2+=[json.loads(x) for x in open('/nlp_group/liupengli/workdir/openai-api/anno/res/score_4.json').readlines()]
    for d in labeldata1:
        input={}
        input['input']=d['question']
        if input['input'] in filter.keys():
          continue

        else:
          if d['ans1_label']=='4':
            ans=d['answer1']
          elif d['ans2_label']=='4':
            ans=d['answer2']
          else:
            continue
          num=re.findall('([0-9]+)',ans,re.S)
          if len(num)==0:
            continue
          filter[input['input']]=num[-1]
    for d in labeldata2:
        if 'score' in d.keys() and d['score']!="4":
          continue
        input={}
        input['input']=d['question']
        if input['input'] in filter.keys():
          continue

        else:
          ans=d['answer']
          if ans is None:
            continue
          num=re.findall('([0-9]+)',ans,re.S)
          if len(num)==0:
            continue
          filter[input['input']]=num[-1]
    #infer的答案，待提取错误的结果
    with open(name,'w') as f:
      for jl in tofilterdata:
        input={}
        count=0
        #解决并非是数学的问题
        question_hasnum=re.findall('([0-9]+)',jl['input'],re.S)
        if len(question_hasnum)==0:
          continue
        if "1." in jl['input']:
          continue
        if len(question_hasnum)==1 and (str(question_hasnum[0])+"年" in jl['input'] or str(question_hasnum[0])+"岁" in jl['input']):
          continue
        num=filter.get(jl['input'])
        if num is None:
          continue
        for i,j in jl.items():
          if 'answer' not in i:
            input[i]=j
          else:
            infernum=re.findall('([0-9]+)',j,re.S)
            if len(infernum)==0:
              continue
            if num==infernum[-1]:
              continue
            elif len(infernum)>1 and num==infernum[0]:
              continue
            input['answer'+str(count)]=j
            count+=1
        f.write(json.dumps(input, ensure_ascii=False)+'\n')

def select_goodans(name):
    #tokenizer = LlamaTokenizer.from_pretrained('/aigc_sgply_ssd/chenzhengzong/pretrain_7B/')
    labeldata1=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0619/sft_infer_data2').readlines()]
    labeldata1+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0607/sft_infer_data1').readlines()]
    labeldata1+=[json.loads(x) for x in open('/nlp_group/chenzhengzong/rm_dataset/RM/labeler_0523/sft_sample_48k_0523.json').readlines()]

    labeldata2=[json.loads(x) for x in open('/nlp_group/liupengli/workdir/openai-api/anno/res/writer_true_ans').readlines()]
    labeldata2+=[json.loads(x) for x in open('/nlp_group/liupengli/workdir/openai-api/anno/res/score_4.json').readlines()]
    for d in labeldata1:
        prompt = {}
        candidates = []
        if d['answer1'] in  dct.keys():
            dct[d['answer1']].append(int(d['ans1_score']))
                # print(d['answer2'])
                # print(dct.get(d['answer1']))
                # print(d['ans2_score'])
        else:
            dct[d['answer1']]=[]
            dct[d['answer1']].append(int(d['ans1_score']))
        if d['answer2'] in  dct.keys():
            dct[d['answer2']].append(int(d['ans2_score']))
                # print(d['answer2'])
                # print(dct.get(d['answer1']))
                # print(d['ans2_score'])
        else:
            dct[d['answer2']]=[]
            dct[d['answer2']].append(int(d['ans2_score']))
    new_data = defaultdict(dict)
    for d in labeldata1:
        prompt = {}
        candidates = []
        key_list_score1=dct.get(d['answer1'])
        if key_list_score1 is None:
            print("not get",d['answer1'])
            continue
        mean_num1 = sum(key_list_score1)/len(key_list_score1)
        if mean_num1 <2:
            mean_num1 = 0
        elif mean_num1 < 4:
            mean_num1 = 2

        key_list_score2=dct.get(d['answer2'])
        if key_list_score2 is None:
            print("not get",d['answer2'])
            continue
        mean_num2 = sum(key_list_score2)/len(key_list_score2)
        if mean_num2 <2:
            mean_num2 = 0
        elif mean_num2 < 4:
            mean_num2 = 2
        if d['question'] not in new_data.keys():
          new_data[d['question']]=defaultdict(dict)

        if mean_num1==4 and d['answer1'] not in new_data[d['question']].keys():
          new_data[d['question']][d['answer1']]=4
        if mean_num2==4 and d['answer2'] not in new_data[d['question']].keys():
          new_data[d['question']][d['answer2']]=4

    for d in labeldata2:
        if 'score' in d.keys() and d['score']!=4:
          continue
        if d['question'] not in new_data.keys():
          new_data[d['question']]=defaultdict(dict)
        new_data[d['question']][d['answer']]=4

    with open(name,'w') as f:
        f.write(json.dumps(new_data, ensure_ascii=False)+'\n')

    return 

def pair_goodandfalse(badname,goodname):
  falses=[json.loads(x) for x in open(badname).readlines()]
  goods=[json.loads(x) for x in open(goodname).readlines()]
  dct={}
  with open('/aigc_sgply_ssd/rl/RM/sft_sample_0517/math/zh_math_ans_goodfilter_v23.json','w') as f:  
    for d in falses:
      good=goods[0].get(d['input'])
      id=d['id']
      if good is not None:
        for fk,fv in d.items():
          if 'answer' not in fk:
            continue
          q_a=d['input']+fv
          if q_a in dct.keys():
            continue
          ans1num=re.findall('([0-9]+)',fv,re.S)
          dct.update({q_a:ans1num[-1]})
          for gk,gv in good.items():
            q_a2=d['input']+gk
            if q_a2 in dct.keys():
              continue
            ans2num=re.findall('([0-9]+)',gk,re.S)
            if len(ans2num)==0:
              break
            dct.update({q_a2:ans2num[-1]})
            #避免错误的答案与正确的答案相同
            if ans2num[-1]==ans1num[-1]:
              break
            data={}
            candidates=[]
            data['input']=d['input']
            data['id']=id
            candidates.append({
                "output":gk,
                "source":"sft_infer_v2",
                "chosen":str(gv)
            })
            candidates.append({
                "output":fv,
                "source":"sft_infer_0718",
                "chosen":str(0)
            })
            data['candidates']=candidates
            f.write(json.dumps(data, ensure_ascii=False)+'\n')   
badname='/aigc_sgply_ssd/rl/RM/sft_sample_0517/math/zh_math_ans_filter_v23.json'
goodname='/aigc_sgply_ssd/rl/RM/sft_sample_0517/math/zh_math_ans_good_v23.json'
filter_goodans(badname)
select_goodans(goodname)
pair_goodandfalse(badname,goodname)
# match = SequenceMatcher(None, a, b).find_longest_match(0,len(a),0,len(b))
# print(a[match.a:match.a+match.size])
# 我不能坐得太靠近电视，因为这样会对我的眼睛和健康造成不良影响。电视屏幕发出的蓝光会损害视网膜，导致视力下降。此外，坐得太靠近电视还可能导致颈椎和腰椎疼痛，影响身体健康。因此，为了保护眼睛和身体健康，我们应该保持适当的观看距离。
# print(b[match.b:match.b+match.size])
