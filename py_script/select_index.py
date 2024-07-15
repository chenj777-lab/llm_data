import json
dct={}
file='/nlp_group/chenzhengzong/rm_dataset/RM/stanfordnlp_SHP/engineer_physics_science_askdocs.json'
cfile='/nlp_group/chenzhengzong/rm_dataset/RM/stanfordnlp_SHP/sample15w.json'
wfile='/nlp_group/chenzhengzong/rm_dataset/RM/stanfordnlp_SHP/sample15w.json_uniq'
data=[json.loads(x) for x in open(file).readlines()]
cdata=[json.loads(x) for x in open(cfile).readlines()]
for d in data:
    qa=d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']
    if qa not in dct.keys():
        dct.update({qa:True})
with open(wfile,'w') as w:
    for d in cdata:
        qa=d['input']+d['candidates'][0]['output']+d['candidates'][1]['output']
        if qa  in dct.keys():
            continue
        w.write(json.dumps(d, ensure_ascii=False)+'\n')
