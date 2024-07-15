from datasets import load_dataset
import json
import re
import os
filename='rm_single_raw_gpt4_96k_v3.json'
log_filename=os.path.join('./','replicate_pair_'+filename)
with open(filename,encoding='utf-8') as f:
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
        #input['candidates']=j.get('candidates')
        for i,o in enumerate(j['candidates']):
          input['candidates']=[]
          for k in o:
            begin=""
            seq_str=""
            seq=[]
            can={}
            if k != 'output':
              can[k]=o[k]
            else:
              begin=re.findall('(^.*)1\.',o['output'],re.S)
              seq=re.findall('([0-9]+\..*?\n\n)',o['output'],re.S)
              #end=re.findall('\n\n(.*?。)',o['output'],re.S
              #end=re.findall(r'\n\n(.*?。.*。?)',o['output'])
              end=re.findall(r'\n\n(.*?\n?\n?.*?$\n?)',o['output'])
            if len(seq)>0:
              if len(begin)>0:
                seq_str=begin[0]
              else:
                seq_str=""
              seq_str=seq_str+seq[0]
              for s in range(len(seq)):
                seq_str=seq_str+seq[s]
              if len(end)>0:
                seq_str=seq_str+end[len(end)-1]
              can.update({'output':seq_str,'chosen':"0",'source':'replicate_'+o['source']})
              input['candidates'].append(j['candidates'][i])
              input['candidates'].append(can)
              input.update({'candidates_num':len(input['candidates'])})

              with open(log_filename,'a',encoding='utf-8') as w:
                w.write(json.dumps(input,ensure_ascii=False)+'\n')
