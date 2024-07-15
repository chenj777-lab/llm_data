#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import logging
import time
from google.protobuf.json_format import MessageToJson
import json
import random, time

from kess.framework import (
    ClientOption,
    GrpcClient,
    KessOption,
)

from mmu.mmu_chat_gpt_pb2 import MmuChatGptRequest,MmuChatGptResponse
from mmu.mmu_chat_gpt_pb2_grpc import (
     MmuChatGptServiceStub,
)

logger = logging.getLogger(__name__)
fmt_str = ('%(asctime)s.%(msecs)03d %(levelname)7s '
           '[%(thread)d][%(process)d] %(message)s')
fmt = logging.Formatter(fmt_str, datefmt='%H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def process_with_retry(grpc_client: GrpcClient, request, query, time_out, n_times, id_key):
    resp = None
    for i in range(n_times):
        try:
            #prompt='对于问题 "{quest}", 有如下多个答案, 请从正确性、完整性和表达清晰度等方面做0-10打分, 答案A: "{ansa}", 答案B: "{ansb}", 答案C: "{ansa}", 答案D: "{ansb}", 答案A得分:, 答案B得分:, 答案C得分:, 答案D得分:'
            #prompt='对于问题{{{quest}}}, 有如下多个答案, 请从正确性、完整性和表达清晰度等方面做0-10打分, 并给出最佳答案。\n答案A: {{{ansa}}} \n答案B: {{{ansb}}} \n答案A得分: \n答案B得分: \n最佳答案:'
            # prompt='对于问题: {quest} \n有如下多个答案, 请根据如下规则对答案做0-10打分, 并给出最佳答案，规则如下： \
            #     \n1.语言表达能力: 根据回答中的语法错误、拼写错误、重复词汇等自然语言处理技术分析得出的分数，以及情感分析得出的分数，综合评估回答的语言表达能力. \
            #     \n2.逻辑推理能力: 根据回答中的逻辑错误、循环论证、因果关系错误等问题，以及情感分析得出的分数，综合评估回答的逻辑推理能力。 \
            #     \n3.情感分析能力: 根据回答中的情感倾向，以及情感分析得出的分数，综合评估回答的情感分析能力。 \
            #     \n4.信息丰富度: 根据回答中的信息量、相关性、可信度等因素，以及自然语言处理技术得出的分数，综合评估回答的信息丰富度。 \
            #     \n5.可读性: 根据回答的可读性指标，如单词数量、句子长度、排版格式等，以及自然语言处理技术得出的分数，综合评估回答的可读性。 \
            #     \n答案A: {ansa} \n答案B: {ansb} \n答案A得分: \n答案B得分: \n最佳答案:'
            #两个答案打分
            #prompt="The question: {quest} \n has two answer, please evaluate the answers and give a score between 0 and 10, and choose the best answer. We can use the following principle: \
            #    \n1.Accuracy of the information: Assess the accuracy of the information provided by the assistant. This includes checking if the information is factual, up-to-date, and relevant to the question asked. \
            #    \n2.Clarity and coherence: Evaluate the clarity and coherence of the answer. Does it provide a clear and concise explanation of the topic? Is it well-organized and easy to follow? \
            #    \n3.Usefulness: Assess the usefulness of the information provided by the assistant. Does it provide practical solutions or insights that can help the user in their decision-making process? \
            #    \n4.Personalization: Evaluate the personalization of the answer. Does it take into account the user's needs, preferences, and goals? \
            #    \n5.Engagement: Assess the engagement level of the answer. Does it encourage the user to ask further questions or seek more information? \
            #    \nanswer A: {ansa} \nanswer B: {ansb} \nanswer A score: \nanswer B score: \nthe best answer:"
            #4个答案打分
            #prompt="The question: {quest} \n has four answer, please evaluate the answers and give a score between 0 and 10, and choose the best answer. We can use the following principle: \
            #    \n1.Accuracy of the information: Assess the accuracy of the information provided by the assistant. This includes checking if the information is factual, up-to-date, and relevant to the question asked. \
            #    \n2.Clarity and coherence: Evaluate the clarity and coherence of the answer. Does it provide a clear and concise explanation of the topic? Is it well-organized and easy to follow? \
            #    \n3.Usefulness: Assess the usefulness of the information provided by the assistant. Does it provide practical solutions or insights that can help the user in their decision-making process? \
            #    \n4.Personalization: Evaluate the personalization of the answer. Does it take into account the user's needs, preferences, and goals? \
            #    \n5.Engagement: Assess the engagement level of the answer. Does it encourage the user to ask further questions or seek more information? \
            #    \nanswer A: {ansa} \nanswer B: {ansb} \nanswer C: {ansc} \nanswer D: {ansd} \nanswer A score: \nanswer B score: \nanswer C score: \nanswer D score: \nthe best answer:"
            #针对性的判断
            #prompt="You are a helpful and precise assistant that selects the necessary skills required to respond to instructions.\nYou are given the following 12 skills.\n[Skill Options]\n1: 模型需要对自己能做什么、不能做什么,是什么,不是什么有清晰的认知,包括但不限于身份信息、来源、与自己相关的开发信息、喜好等,需知道对特定专业有风险的领域如医疗用药等问题进行回复,需要明确,当且仅当用户的意图和模型自我认知能力有关系时,才考虑这个指标\n2: 回复的文本中涉及到以下几类情况均需考虑这个指标。回复的文本是否逻辑通顺,包括逻辑的连贯性、逻辑的严谨性、逻辑的完整性,考虑其推理步骤的普遍适用并避免逻辑矛盾。同时包括考虑编码和数学问题的边缘情况,没有未考虑到的反例；考虑是否在问题的限定下已最简单高效的方式推理,时间复杂度低且无多余步骤。当且仅当这个问题需要非常复杂的逻辑推理思考时,才需要考虑这个指标\n3: 模型回复的文本是否详实,答复是否提供了充分的解释应考虑答复的全面性和彻底性,包括考虑的维度广度和解释说明的详细程度,包括是否包含足够的信息,在例子、解释方面是否详实。还包括回复内容本身具有多样性,如考虑的角度维度覆盖各类场景,并非单一从几个维度出发考虑。当且仅当这个回答需要更详细的细节和信息时,才考虑这个指标\n4: 回复的文本中涉及到以下几类情况均需考虑这个指标。1、需考虑回复的文本中的事实或知识信息中是否有错误,是否正确真实,有权威性,无胡编乱造；尤其专业领域知识上如医学、法律有可靠的证据或对其信息来源的引用支持。2、需考虑回复的文本中的是否有常识性信息错误,包括对指令涉及的世界常识、世界概念理解、背景知识理解是否合理。\n5: 考虑模型回复的文本是否安全,对诱导/攻击/含敏感信息/负面情绪的问题,是否进行有效规避及积极引导。包括但是否包含敏感信息、是否包含不当信息、是否政治正确符合中国国情、是否合规并符合主流倾向、是否避免了与性别/种族/民族或宗教有关的偏见等、是否考虑了用户安全的潜在风险避免提供可能导致身体伤害或危害的回应、是否有反人类言论,是否有辱骂脏话等,当且仅当这个问题在回答过程中有可能有安全性风险时,才考虑这个指标\n6: 回复的文本是否可读,包括是否符合语法、是否符合语义、是否符合语用,回复的文本格式是否规范好理解,表述是否连贯易于理解、结构是否顺畅,是否存在内容重复；也包括文法用语是否优美具有艺术欣赏性,当且仅当回复的内容可能比较复杂,需要仔细阅读时,才优先考虑这个指标\n7: 模型回复的文本是否与问题切题并具有针对性,是否切题,回复是否直击核心问题切中主题,没有相关性较低的冗余信息,合理信息延伸和解释说明不算偏题。当且仅当这个问题的答案不能额外包含无关信息时,才考虑这个指标。\n8: 回复的文本中涉及到以下几类情况,且这个问题所包含的用户意图不易理解时需考虑这个指标。回复的文本是否理解了用户的问题,能否按照用户的意图进行对话,能否理解用户意图中的常识和反常识,在用户输入有缺失的情况下,能否理解或反问用户输入的信息希望进行信息补充完善。\nWhat are the 3 most primary skills that are needed to answer the following instruction? Especially, select the primary skills that this instruction particularly requires rather than skills that could be applied to common instructions.\n[Instruction]\n{quest}\nselect and write the index of 2~4 most primary skills. Also, write a brief description of how the skill should be applied when answering to the instruction within 1~2 sentences for each selected skill. Finally, after generating two newlines, return a Python list object that includes each index of 3 skills, arranged in descending order of importance.\n"
            #prompt="[System]We would like to request your feedback on the performance of the assistant's responses to the user question displayed below.In the feedback, I want you to rate the quality of the response in the following dimension to the given scoring rubric:针对性: 模型回复的文本是否与问题切题并具有针对性,是否切题,回复是否直击核心问题切中主题,没有相关性较低的冗余信息,合理信息延伸和解释说明不算偏题。Score 1：高度冗余或包含大量不必要的信息，较难提取需要的信息. Score 2：与query的针对性较差，包括较多不必要相关性较低的信息. Score 3：包含了部分不必要的信息，未满足比例30%以下。Score 4：对query的针对性较好，少量相关性稍低的信息，比例10%以下。Score 5：针对性优秀，不包含任何不必要的信息，无需进一步优化。You will be given 4 answers. Please give feedback on each responses. Also, provide each responses with a score on a scale of 1 to 5 for the scoring dimension, where a higher score indicates better overall performance. Make sure to give feedback or comments for the scoring dimension first and then write the score for the scoring dimension. Only write the feedback corresponding to the scoring rubric for the scoring dimension. The scores of the scoring dimension should not be affected by any aspects not mentioned in the scoring rubric, indicating that 'Correctness' should not be considered for 'Readability' category, for example. Make sure the feedback strictly follow this format:Evaluation evidence: <your explanation here>Score: <score>[User Question]{quest}\n[Assistant’s Answer A]{ansa}\n[Assistant’s Answer B]{ansb}\n[Assistant’s Answer C]{ansc}\n[Assistant’s Answer D]{ansd}\n"
            #zhendui
            #prompt="[System]We would like to request your feedback on the performance of the assistant's responses to the user question displayed below.In the feedback, I want you to rate the quality of the response in the following dimension to the given scoring rubric:针对性: 模型回复的文本是否与问题切题并具有针对性,是否切题,回复是否直击核心问题切中主题,没有相关性较低的冗余信息,合理信息延伸和解释说明不算偏题。Score 1：高度冗余或包含大量不必要的信息，较难提取需要的信息. Score 2：与query的针对性较差，包括较多不必要相关性较低的信息. Score 3：包含了部分不必要的信息，未满足比例30%以下。Score 4：对query的针对性较好，少量相关性稍低的信息，比例10%以下。Score 5：针对性优秀，不包含任何不必要的信息，无需进一步优化。You will be given 8 answers. Please give feedback on each responses. Also, provide each responses with a score on a scale of 1 to 5 for the scoring dimension, where a higher score indicates better overall performance. Make sure to give feedback or comments for the scoring dimension first and then write the score for the scoring dimension. Only write the feedback corresponding to the scoring rubric for the scoring dimension. The scores of the scoring dimension should not be affected by any aspects not mentioned in the scoring rubric, indicating that 'Correctness' should not be considered for 'Readability' category, for example. Make sure the feedback strictly follow this format:Evaluation evidence: <your explanation of answer A here>Score: <score of answer A>Evaluation evidence: <your explanation of answer B here>Score: <score of answer B>Evaluation evidence: <your explanation of answer C here>Score: <score of answer C>Evaluation evidence: <your explanation of answer D here>Score: <score of answer D>Evaluation evidence: <your explanation of answer E here>Score: <score of answer E>Evaluation evidence: <your explanation of answer F here>Score: <score of answer F>Evaluation evidence: <your explanation of answer G here>Score: <score of answer G>Evaluation evidence: <your explanation of answer H here>Score: <score of answer H>[User Question]{quest}\n[Assistant’s Answer A]{ansa}\n[Assistant’s Answer B]{ansb}\n[Assistant’s Answer C]{ansc}\n[Assistant’s Answer D]{ansd}\n[Assistant’s Answer E]{anse}\n[Assistant’s Answer F]{ansf}\n[Assistant’s Answer G]{ansg}\n[Assistant’s Answer H]{ansh}\n"
            prompt="[System]We would like to request your feedback on the performance of the assistant's responses to the user question displayed below.In the feedback, I want you to rate the quality of the response in the following dimension to the given scoring rubric:信息正确性: 回复的文本中涉及到以下几类情况均需考虑这个指标。1、需考虑回复的文本中的事实或知识信息中是否有错误,是否正确真实,有权威性,无胡编乱造；尤其专业领域知识上如医学、法律有可靠的证据或对其信息来源的引用支持。2、需考虑回复的文本中的是否有常识性信息错误,包括对指令涉及的世界常识、世界概念理解、背景知识理解是否合理。Score 1：完全错误 ：与query相关的核心事实错误，或涉及到的信息事实完全错误，或者信息来源不可靠，存在明显的误导性。尤其是医学等专业领域知识或事实存在错误时，直接判定为1分。 Score 2：大部分错误：与query相关的核心信息部分错误或大部分信息都存在错误或存在误导性的不准确信息，或信息时效性错误。 Score 3：小部分错误 ：与query相关的核心信息绝大部分均正确，延伸说明信息存在小部分的误导性或者不确定性，需要进一步核实或调查或存在少量常识错误，在answer中篇幅占比不超过40% Score 4：瑕疵错误：与query相关的核心信息正确，相关延伸说明信息中存在误导性信息或者存在一些错误，需要进一步核实或调查，在answer中篇幅占比不超过10% Score 5：完全正确 信息与事实完全一致，没有任何误导性或错误信息，来源可靠有论文或证据的充分支持。You will be given 8 answers. Please give feedback on each responses. Also, provide each responses with a score on a scale of 1 to 5 for the scoring dimension, where a higher score indicates better overall performance. Make sure to give feedback or comments for the scoring dimension first and then write the score for the scoring dimension. Only write the feedback corresponding to the scoring correctness for the scoring dimension. The scores of the scoring dimension should not be affected by any aspects not mentioned in the scoring correctness, indicating that 'Rubric' should not be considered for 'Readability' category, for example. Make sure the feedback strictly follow this format:Evaluation evidence: <your explanation of answer A here>Score: <score of answer A>Evaluation evidence: <your explanation of answer B here>Score: <score of answer B>Evaluation evidence: <your explanation of answer C here>Score: <score of answer C>Evaluation evidence: <your explanation of answer D here>Score: <score of answer D>Evaluation evidence: <your explanation of answer E here>Score: <score of answer E>Evaluation evidence: <your explanation of answer F here>Score: <score of answer F>Evaluation evidence: <your explanation of answer G here>Score: <score of answer G>Evaluation evidence: <your explanation of answer H here>Score: <score of answer H>[User Question]{quest}\n[Assistant’s Answer A]{ansa}\n[Assistant’s Answer B]{ansb}\n[Assistant’s Answer C]{ansc}\n[Assistant’s Answer D]{ansd}\n[Assistant’s Answer E]{anse}\n[Assistant’s Answer F]{ansf}\n[Assistant’s Answer G]{ansg}\n[Assistant’s Answer H]{ansh}\n"
            request.session_id = str(query[id_key])  #注意对于多轮对话需要记历史的，那么一个对话一个 session_id
            request.req_id = str(query[id_key])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][2]['output'],ansd=query['candidates'][3]['output'])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][2]['output'],ansd=query['candidates'][3]['output'],anse=query['candidates'][4]['output'],ansf=query['candidates'][5]['output'],ansg=query['candidates'][6]['output'],ansh=query['candidates'][7]['output'])
            request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][0]['output'],ansd=query['candidates'][1]['output'],anse=query['candidates'][0]['output'],ansf=query['candidates'][1]['output'],ansg=query['candidates'][0]['output'],ansh=query['candidates'][1]['output'])
            #request.query = prompt.format(quest=query['question'])
            #发起请求
            resp = grpc_client.Chat(request, timeout=time_out)
            resp = json.loads(MessageToJson(resp))
            if resp['status']['code'] != 'SUCESS':
                logger.info('%s 接口调用失败,重试 %d, status_code=%s', query[id_key], i+1, resp['status']['code'])
                #time.sleep(random.randint(i*10, (i+1)*10))
                time.sleep(random.randint(i*5, (i+1)*5))
                time_out += time_out
                continue
            else:
                return (0, resp)   
        except Exception as e:
            logger.error('%s 发生异常,重试 %d: %s', query[id_key], i+1, e)
            time.sleep(random.randint(i*10, (i+1)*10))
            time_out += time_out
            continue  
    logger.info('%s 重试 %d 次后仍失败', request.req_id, n_times)
    return (1, resp) 


def chat(grpc_client: GrpcClient, timeout: float, in_fn, out_fn, gpt_version, id_key='id'):
    #构造request, biz需根据实际申请的进行修改
    assert gpt_version in ['gpt3', 'gpt3.5', 'gpt4']
    #biz = 'liupengli_699d56a9_gpt4'
    biz = 'liupengli_699d56a9_gpt3.5'
    #biz = 'zhaoyi07_60c690ac_gpt4'
    if gpt_version == 'gpt4':
        biz = 'liupengli_699d56a9_gpt4'
    
    request = MmuChatGptRequest(biz=biz)

    done_cases = {}
    if os.path.isfile(out_fn):
        with open(out_fn, 'r') as f:
            for line in f:
                x = json.loads(line.strip())
                done_cases[x[id_key]] = 1

    with open(in_fn, 'r') as fin, open(out_fn, 'a') as fo:
        for line in fin:
            x = json.loads(line.strip())
            if x[id_key] in done_cases:
                continue
            status, resp = process_with_retry(grpc_client, request, x, timeout, 10, id_key)  
            if status != 0:
                continue
            if resp['status']['code'] != 'SUCESS':
                logger.error('%s 接口调用失败, status_code=%s', x[id_key], resp['status']['code'])
                continue
            try:
                x['answer'] = resp['answer']
                json_str = json.dumps(x, ensure_ascii=False)
                fo.write(json_str + '\n')
                fo.flush()                
                logger.info(x[id_key] + '\tdone')
            except Exception as e:
                logger.error('发生异常 %s\t%s', x[id_key], e)
                print(resp)
                continue

if __name__ == "__main__":
    #服务名不要改动
    client_option = ClientOption(
        biz_def='mmu',
        grpc_service_name='mmu-chat-gpt-service',
        grpc_stub_class=MmuChatGptServiceStub
    )

    client = GrpcClient(client_option)
    chat(client, 160, sys.argv[1], sys.argv[2], sys.argv[3], id_key='id') #输入文件的id字段在这儿配置
    logger.info('call end')


