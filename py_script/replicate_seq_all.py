from datasets import load_dataset
import json
import re
import os
path='/cpfs01/rl/RM/labeler_0523'
filename='format_sft_sample_48k_0523.jl.cat.results.scp'
readfile=os.path.join(path,filename)
# allfilename=os.path.join(path,'seqreplicate_v2_'+filename)
# pairfilename=os.path.join(path,'seqreplicate_v2_pair_'+filename)
allfilename=os.path.join(path,'strrep_v2_'+filename)
pairfilename=os.path.join(path,'strrep_v2_pair_'+filename)

def replicate(readfile,allfilename):
  with open(readfile,encoding='utf-8') as f,open(allfilename,'w',encoding='utf-8') as w:
    while True:
      input={}
      line = f.readline()
      if not line:
        break
      j=json.loads(line)
      for key in j:
        if key != 'candidates':
          input[key]=j[key]
        else:
          input['candidates']=[]
          #input['candidates']=j.get('candidates')
          for i,o in enumerate(j['candidates']):
            j['candidates'][i].update({'source':j['candidates'][i]['source']+str(i)})
            input['candidates'].append(j['candidates'][i])
            for k in o:
              begin=""
              seq_str=""
              seq=[]
              can={}
              if k != 'output':
                can[k]=o[k]
              else:
                #step1 取出序号1的前面内容
                begin=re.findall('(^.*?)1\.',o['output'],re.S)
  
                #step2 取出各个序号的内容
                o1=o['output']
                for i in range(len(begin)):
                  o1=o1[len(begin[i]):]
                #seq=re.findall('([0-9]+\..*?\n\n)',o1,re.S)
                seq=re.findall('[0-9]+\.(.*?\n?\n)',o1,re.S)
                #end=re.findall('\n\n(.*?。)',o['output'],re.S
                #end=re.findall(r'\n\n(.*?。.*。?)',o['output'])
  
                #step3 取出序号尾部后的内容
                o2=o1
                for i in range(len(seq)):
                  o2=o2[len(seq[i])+2:]
                # end=re.findall(r'\n\n(.*?\n?\n?.*?$\n?)',o2)
                #end=re.findall(r'(.*?\n?\n?.*?$\n?)',o2)
                end_seq=re.findall('[0-9]+\.(.*\n?\n?)',o2,re.S)
                #end=re.findall(r'[0-9]+\.(.*?)',o2)
                
                o3=o2
                for i in range(len(end_seq)):
                  o3=o3[len(end_seq[i])+2:]

              #step4 把第一个需要做重复添加
              if len(seq)>0:
                if len(begin)>0:
                  seq_str=begin[0]
                else:
                  seq_str=""
                seq_str=seq_str+'1.'+seq[0]
                for i in range(len(seq)):
                  seq_str=seq_str+str(i+1)+'.'+seq[i]
                if len(end_seq)>0:
                  seq_str=seq_str+str(len(seq)+1)+'.'+end_seq[len(end_seq)-1]
                seq_str+=o3
                input['candidates'].append({'output':seq_str,'chosen':False,'source':'replicate_b1_'+o['source']})

              #step5 把第一、二个需要做重复添加
              if len(seq)>1:
                if len(seq)>0:
                  if len(begin)>0:
                    seq_str=begin[0]
                  else:
                    seq_str=""
                  seq_str=seq_str+'1.'+seq[0]+'2.'+seq[1]
                  for i in range(len(seq)):
                    seq_str=seq_str+str(i+1)+'.'+seq[i]
                  if len(end_seq)>0:
                    seq_str=seq_str+str(len(seq)+1)+'.'+end_seq[len(end_seq)-1]
                  seq_str+=o3
                  input['candidates'].append({'output':seq_str,'chosen':False,'source':'replicate_b1a2_'+o['source']})    
              
              #step6 对大于3个的序号，把倒数第一、二个做重复添加
              if len(seq)>3:
                if len(seq)>0:
                  if len(begin)>0:
                    seq_str=begin[0]
                  else:
                    seq_str=""
                  for i in range(len(seq)):
                    seq_str=seq_str+str(i+1)+'.'+seq[i]
                  #seq_str=seq_str+str(len(seq)+1)+'.'+seq[-1]
                  if len(end_seq)>0:
                    seq_str=seq_str+str(len(seq)+1)+'.'+end_seq[len(end_seq)-1]+str(len(seq)+2)+'.'+seq[-1]+str(len(seq)+3)+'.'+end_seq[len(end_seq)-1]
                  else:
                    seq_str=seq_str+str(len(seq)+1)+'.'+seq[-2]+str(len(seq)+2)+'.'+seq[-1]
                  seq_str+=o3
                  input['candidates'].append({'output':seq_str,'chosen':False,'source':'replicate_e1a2_'+o['source']})    
              
      input.update({'candidates_num':len(input['candidates'])})
      w.write(json.dumps(input,ensure_ascii=False)+'\n')

def pair(allfilename,pairfilename,string):
  with open(allfilename,'r',encoding='utf-8') as f,open(pairfilename,'w',encoding='utf-8') as w:
    while True:
        line = f.readline()
        if not line:
            break
        jl=json.loads(line)
        input={}
        
        for key in jl:
          if key != 'candidates':
            input[key]=jl[key]

        input['candidates_num']=2
        input['candidates']=[]
        l=jl['candidates']
        if len(l)<=2:
          continue
        for j in range(len(l)):
            for i in range(j+1,len(l)):
              j_flag=l[j]['chosen']
              if l[j]['chosen'] is False and string not in l[j]['source'] and l[j]['source'] in l[i]['source']:
                j_flag=True
              if j_flag==l[i]['chosen']:
                continue
              if l[i]['chosen'] is False and string not in l[i]['source']:
                continue
              can=[]
              can.append(l[j])
              can.append(l[i])
              input.update({'candidates':can})
              w.write(json.dumps(input,ensure_ascii=False)+'\n')

def strrepli(readfile,allfilename):
  with open(readfile,encoding='utf-8') as f,open(allfilename,'w',encoding='utf-8') as w:
    while True:
      input={}
      line = f.readline()
      if not line:
        break
      j=json.loads(line)
      for key in j:
        if key != 'candidates':
          input[key]=j[key]
        else:
          input['candidates']=[]
          #input['candidates']=j.get('candidates')
          for i,o in enumerate(j['candidates']):
            j['candidates'][i].update({'source':j['candidates'][i]['source']+str(i)})
            input['candidates'].append(j['candidates'][i])
            for k in o:
              begin=""
              seq_str=""
              seq=[]
              can={}
              if k != 'output':
                can[k]=o[k]
              else:
                #step1 取出。的前面内容
                begin=re.findall('(^.*)。',o['output'],re.S)
                end_sen=re.findall('^.*，(.*)。',o['output'],re.S)
                o1=o['output']
                for i in range(len(begin)):
                  o1=o1[len(begin[i])+1:] 
                #step2 拼接
                if len(begin)==0 or len(end_sen)==0:
                  continue
                seq_str=begin[0]+'，'+end_sen[0]+'，'+end_sen[0]+'，'+end_sen[0]+"。"
                #seq_str=begin[0]+'业业业业业业业业业业业业业业业业业业业业业业。'+o1
                input['candidates'].append({'output':seq_str,'chosen':False,'source':'strrep_sentence_'+o['source']})    
   
      input.update({'candidates_num':len(input['candidates'])})
      w.write(json.dumps(input,ensure_ascii=False)+'\n')



# path='/cpfs01/rl/RM/labeler_0523'
# filename='format_sft_sample_48k_0523.jl.cat.results.scp'
# d={'/cpfs01/rl/RM/labeler_0523':'format_sft_sample_48k_0523.jl.cat.results.scp','/cpfs01/rl/RM/labeler_0607/':'fix_t2f.txt.cat.results.scp','/cpfs01/rl/RM/labeler_0619/':'fix_t2f.txt.cat.results.scp','/cpfs01/rl/RM/labeler_0506/':'format_gpt4llm_zh_51k_0506.json.cat.results.scp_clean'}
d={'/cpfs01/rl/RM/labeler_0523':'format_sft_sample_48k_0523.jl.cat.results.scp'}
for path,filename in d.items():
  # readfile=os.path.join(path,filename)

  # allfilename=os.path.join(path,'seqreplicate_v2_'+filename)
  # pairfilename=os.path.join(path,'seqreplicate_v2_pair_'+filename)
  # replicate(readfile,allfilename)
  # pair(allfilename,pairfilename,'replicate_')

  allfilename=os.path.join(path,'strrep_v2_sentenct_'+filename)
  pairfilename=os.path.join(path,'strrep_v2_pair_sentence_'+filename)
  strrepli(readfile,allfilename)
  pair(allfilename,pairfilename,'strrep_sentence_')
