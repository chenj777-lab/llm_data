import json
import math
import re
def clean():
   with open('/cpfs01/rl/RM/webgpt_comparisons/train.json.cat.results.scp') as r,open('/cpfs01/rl/RM/webgpt_comparisons/train.json.cat.results.scp_clean','w') as w:
     data=[json.loads(x) for x in open('/cpfs01/rl/RM/webgpt_comparisons/train.json.cat.results.scp').readlines()]
     for i in data:
       if i['candidates'][0]['chosen'] == i['candidates'][1]['chosen'] :
         continue
       i['candidates'].sort(key=lambda x: x.get('chosen'),reverse=True)
       w.write(json.dumps(i, ensure_ascii=False)+'\n')

def re_clean():
   with open('/cpfs01/rl/RM/webgpt_comparisons/split_test_clean.json','w') as w:
     data=[json.loads(x) for x in open('/cpfs01/rl/RM/webgpt_comparisons/split_test.json').readlines()]
     for i in data:
      for j in range(len(i['candidates'])):
        o=i['candidates'][j]['output']
        #处理小数
        o_clean=re.sub('\[[0-9].*?\]','',o)
        i['candidates'][j].update({'output':o_clean})
      w.write(json.dumps(i, ensure_ascii=False)+'\n')

re_clean()

#sed 's/\[[0-9]\]//g'
