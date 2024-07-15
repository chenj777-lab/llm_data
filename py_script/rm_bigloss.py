#删除人工筛选的分类错误的
#for i in `seq 1 30`;do c=`head -${i} ddd|tail -1`; for i in `grep -F -n "${c}\", \"source\": \"amb" /cpfs01/rl/RM/labeler_0619/merge_from_num_calc_v2.json|cut -d ":" -f 1|sort -r -n `;do sed -i "${i}d" /cpfs01/rl/RM/labeler_0619/merge_from_num_calc_v2.json;done;done

#删除在本份数据中误分类的
# cat  0607merge_from_num_calc_v2.jsontestbigloss|cut -d "\"" -f 26  >ambigu.tmp
# while read line;do grep -F "${line}\", \"source\": \"sft_infer_v2" /cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json|cut -d "\"" -f 14 >>mis_ambigu.tmp;done<ambigu.tmp
# while read line;do for i in `grep -F -n "${line}\", \"source\": \"ambiguous_pair" /cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json|cut -d ":" -f 1|sort -n -r`;do sed -i "${i}d" /cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json  ;done;done<mis_ambigu.tmp

# #删除在其他数据中误分类的
# cat  /cpfs01/rl/RM/labeler_0619/merge_from_num_calc_v2.json|cut -d "{" -f 4|cut -d "\"" -f 4  >ambigu.tmp4
# #根据每一个文件找出被误分类的case
# for i in `ls /cpfs01/rl/RM/labeler_0619|grep json |grep -v "math_sourcet2f\.json"|grep -v "f2z\.json" |grep -v "merge_source_t2f\.json"|grep -v "merge_math_source_t2f\.json"`
# do
# for j in `seq 1 15124`
# do
# line=`head -${j} ambigu.tmp4|tail -1`
# grep -F "\"${line}\", \"source\": \"sft_infer_v2\"" /cpfs01/rl/RM/labeler_0619/$i >>mis_ambigu.tmp4
# done
# done

#在原始文件中删除被误分的
# for j in `seq 1 20000`
# do
# line= `head -${j} mis_ambigu.tmp|tail -1`
# for i in `grep -F -n "${line}\", \"source\": \"ambiguous_pair" /cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json|cut -d ":" -f 1|sort -n -r`;do sed -i "${i}d" /cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json  ;done
# done




#step1  去除异常json
# #python3
# #以读入文件为例:
import json
def readfile():
    f = open("mis_ambigu.tmp", "rb") #二进制格式读文件
    count=0
    while True:
        line = f.readline()
        count+=1
        if not line:
            break
        else:
            try:
                # print(line.decode('utf8'))
                c=json.loads(line)
                with open('fix_format_uniq_mis_ambigu.tmp', 'a') as dd:
                    dd.write(json.dumps(c, ensure_ascii=False)+'\n')
            except:
                print(str(line))
                print(count)

#step2  把匹配的路文件
import json
dct={}
def select_false():
  data=[json.loads(x) for x in open('fix_format_uniq_mis_ambigu.tmp')]
  for d in data:
    if d['candidates'][0]['source']=='sft_infer_v2':
        c=d['candidates'][0]['output']
        dct.update({c:True})
        
        # with open('ans1_fix_format_uniq_mis_ambigu.tmp2', 'a') as dd:
        #     dd.write(json.dumps(c, ensure_ascii=False)+'\n')
  data2=[json.loads(x) for x in open('/cpfs01/rl/RM/labeler_0607/merge_from_num_calc_v2.json')]
  for d in data2:
    if d['candidates'][1]['source']=='ambiguous_pair' and d['candidates'][1]['output'] in dct.keys():
      print(d['candidates'][1]['output'])
      continue
    with open('/cpfs01/rl/RM/labeler_0607/fix_merge_from_num_v6_8.json_merge2', 'a') as dd:
      dd.write(json.dumps(d, ensure_ascii=False)+'\n') 

readfile()
select_false()