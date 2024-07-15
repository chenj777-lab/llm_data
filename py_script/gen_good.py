import pandas
import json
import re
import os
from openpyxl.styles.colors import WHITE, RGB

__old_rgb_set__ = RGB.__set__


def __rgb_set_fixed__(self, instance, value):
    try:
        __old_rgb_set__(self, instance, value)
    except ValueError as e:
        if e.args[0] == 'Colors must be aRGB hex values':
            __old_rgb_set__(self, instance, WHITE)  # Change default color here


RGB.__set__ = __rgb_set_fixed__


# log_filename=os.path.join('/cpfs01/rl/RM/sft_simple_badcase/', '70B.json')
# df=pandas.read_excel('/cpfs01/rl/RM/sft_simple_badcase/70Bv0625、33Bv0607数据对比详情.xlsx',header=0,engine='openpyxl')
# with open(log_filename,'w',encoding='utf-8') as f:

#    for val in df.values:
#       input={}

#       j=val
#       input['id']=j[0]
#       input['metas']={}
#       input['metas']['一级类目']=j[2]   
#       input['metas']['二级类目']=j[3]
#       input['input']=j[5]
#       input['candidates']=[]
#       print(j)
#       input['candidates'].append({'output':j[6],'source':'reference','chosen':5})
#       input['candidates'].append({'output':j[7],'source':'v0607_'+str(j[14]),'chosen':j[11]})
#       input['candidates'].append({'output':j[8],'source':'v0625_a1_'+str(j[21-1]),'chosen':j[18-1]})
#       input['candidates'].append({'output':j[9],'source':'v0625_a2_'+str(j[25-1]),'chosen':j[22-1]})
#       input['candidates'].append({'output':j[10],'source':'v0625_a3_'+str(j[29-1]),'chosen':j[26-1]})

#       f.write(json.dumps(input,ensure_ascii=False)+'\n')

# log_filename=os.path.join('/cpfs01/rl/RM/sft_simple_badcase/', '13B.json')
# df=pandas.read_excel('/cpfs01/rl/RM/sft_simple_badcase/13B_v0629、33B_v0607数据详情.xlsx',header=0,engine='openpyxl')
# with open(log_filename,'w',encoding='utf-8') as f:

#    for val in df.values:
#       input={}

#       j=val
#       input['id']=j[0]
#       input['metas']={}
#       input['metas']['一级类目']=j[2]   
#       input['metas']['二级类目']=j[3]
#       input['input']=j[5]
#       input['candidates']=[]
#       print(j)
#       input['candidates'].append({'output':j[6],'source':'reference','chosen':5})
#       input['candidates'].append({'output':j[7],'source':'v0607_'+str(j[14+2]),'chosen':j[10+2]})
#       input['candidates'].append({'output':j[8],'source':'v0625_a1_'+str(j[21-1+3]),'chosen':j[18-1+2]})
#       input['candidates'].append({'output':j[9],'source':'v0625_a2_'+str(j[25-1+4]),'chosen':j[22-1+3]})
#       input['candidates'].append({'output':j[10],'source':'v0625_a3_'+str(j[29+4]),'chosen':j[26-1+4]})

#       f.write(json.dumps(input,ensure_ascii=False)+'\n')

log_filename=os.path.join('/cpfs01/rl/RM/sft_simple_badcase/', 'from_badcase.json')
df=pandas.read_excel('/cpfs01/rl/RM/sft_simple_badcase/21676_0628.xlsx',header=0,engine='openpyxl')
with open(log_filename,'w',encoding='utf-8') as f:

   for val in df.values:
      input={}

      j=val
      input['id']=j[0]
      input['metas']={}
      input['input']=j[2]
      input['candidates']=[]
      print(j)
      input['candidates'].append({'output':j[3],'source':'v1_a1_'+str(j[8]),'chosen':j[6]})
      input['candidates'].append({'output':j[9],'source':'v1_a2_'+str('nan'),'chosen':j[12]})
      input['candidates'].append({'output':j[15],'source':'v1_a3_'+str(j[20]),'chosen':j[18]})
      input['candidates'].append({'output':j[21],'source':'v2_a1_'+str(j[26]),'chosen':j[24]})
      input['candidates'].append({'output':j[27],'source':'v2_a2_'+str(j[32]),'chosen':j[30]})
      input['candidates'].append({'output':j[33],'source':'v1_a3_'+str(j[38]),'chosen':j[36]})

      f.write(json.dumps(input,ensure_ascii=False)+'\n')

# log_filename=os.path.join('/cpfs01/rl/RM/sft_simple_badcase/', 'from_badcase.json')
# df=pandas.read_excel('/cpfs01/rl/RM/sft_simple_badcase/21677_0628.xlsx',header=0,engine='openpyxl')
# with open(log_filename,'a',encoding='utf-8') as f:

#    for val in df.values:
#       input={}

#       j=val
#       input['id']=j[0]
#       input['metas']={}
#       input['input']=j[2]
#       input['candidates']=[]
#       print(j)
#       input['candidates'].append({'output':j[3],'source':'v1_a1_'+str(j[10]),'chosen':j[6]})
#       input['candidates'].append({'output':j[11],'source':'v1_a2_'+str('nan'),'chosen':j[7]})
#       input['candidates'].append({'output':j[16],'source':'v1_a3_'+str('nan'),'chosen':j[8]})
#       input['candidates'].append({'output':j[21],'source':'v2_a1_'+str(j[26]),'chosen':j[24]})
#       input['candidates'].append({'output':j[27],'source':'v2_a2_'+str(j[32]),'chosen':j[30]})
#       input['candidates'].append({'output':j[33],'source':'v1_a3_'+str(j[38]),'chosen':j[36]})

#       f.write(json.dumps(input,ensure_ascii=False)+'\n')

# log_filename=os.path.join('/cpfs01/rl/RM/sft_simple_badcase/', '13B0627.json')
# df=pandas.read_excel('/cpfs01/rl/RM/sft_simple_badcase/13B_v0627、chatgpt、33B_v0607数据详情汇总.xlsx',header=0,engine='openpyxl')
# with open(log_filename,'w',encoding='utf-8') as f:

#    for val in df.values:
#       input={}

#       j=val
#       input['id']=j[0]
#       input['metas']={}
#       input['metas']['一级类目']=j[2]   
#       input['metas']['二级类目']=j[3]
#       input['input']=j[5]
#       input['candidates']=[]
#       print(j)
#       input['candidates'].append({'output':j[7],'source':'chatgpt_'+str(j[16]),'chosen':j[12]})
#       input['candidates'].append({'output':j[8],'source':'v0627_'+str(j[21])+str(j[22]),'chosen':j[17]})
#       input['candidates'].append({'output':j[9],'source':'v0607_'+str(j[24]),'chosen':j[23]})


#       f.write(json.dumps(input,ensure_ascii=False)+'\n')
