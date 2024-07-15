from datasets import load_dataset
import json

data=load_dataset('openai/summarize_from_feedback',name='comparisons')
train_d=data['train']
valid_d=data['validation']

log_trainfilename='/cpfs01/rl/RM/summarize_from_feedback/train.json'
log_testfilename='/cpfs01/rl/RM/summarize_from_feedback/valid.json'

with open(log_trainfilename,'w',encoding='utf-8') as w, open(log_testfilename,'w',encoding='utf-8') as t:
    for d in train_d:
        info={}
        info['id']=d['info']['id']
        info['input']=d['info']['post']
        info['candidates']=[]
        info['candidates'].append({
            'output':d['summaries'][0]['text'],
            'source':'openai/summarize_from_feedback',
            'chosen':d['choice']==0,
            })
        info['candidates'].append({
            'output':d['summaries'][1]['text'],
            'source':'openai/summarize_from_feedback',
            'chosen':d['choice']==1,
            })
        info['candidates'].sort(key= lambda x:x['chosen']==True, reverse = True)
        w.write(json.dumps(info,ensure_ascii=False)+'\n')   

    for d in valid_d:
        info={}
        info['id']=d['info']['id']
        info['input']=d['info']['post']
        info['candidates']=[]
        info['candidates'].append({
            'output':d['summaries'][0]['text'],
            'source':'openai/summarize_from_feedback',
            'chosen':d['choice']==0,
            })
        info['candidates'].append({
            'output':d['summaries'][1]['text'],
            'source':'openai/summarize_from_feedback',
            'chosen':d['choice']==1,
            })
        info['candidates'].sort(key= lambda x:x['chosen']==True, reverse = True)
        t.write(json.dumps(info,ensure_ascii=False)+'\n')   

def __init__(self, split="train", mode="sft", conf_threshold=-1, max_comparison_per_sample=5) -> None:
        super().__init__()
        assert split in ("train", "valid1", "valid2", "test")
        assert mode in ("sft", "rm", "rl")
        self.mode = mode
        summaries = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2summary = {}
        self.max_comparison_per_sample = max_comparison_per_sample
        major_split = split if "train" == split else "validation"
        dataset = load_dataset("openai/summarize_from_feedback", "comparisons")[major_split]
        for data in dataset:
            if (
                "extra" in data
                and "confidence" in data["extra"]
                and data["extra"]["confidence"] is not None
                and conf_threshold > data["extra"]["confidence"]
            ):
                print("skipping {}".format(data["info"]["id"]))
                continue

            if split != "train" and split != data["split"]:
                continue

            if "article" in data["info"] and data["info"]["article"] is not None:
                context = data["info"]["article"]
            elif "post" in data["info"]:
                context = data["info"]["post"]

            if context not in self.index2summary:
                self.index2summary[len(self.index2summary)] = context

            if context not in summaries:
                summaries[context] = []

            pos, neg = (0, 1) if data["choice"] == 0 else (1, 0)
            summaries[context].append((data["summaries"][pos]["text"].strip(), data["summaries"][neg]["text"].strip()))

        ranked_summaries = {}
        for context, summary_comparison_pairs in summaries.items():
            ranks = self.get_sorted_ranks(summary_comparison_pairs)
            ranked_summaries[context] = ranks
        self.summaries = ranked_summaries
