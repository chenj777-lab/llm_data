#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import re
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
            #prompt="The question: {quest} \n has two answer, please evaluate the answers and give a score between 0 and 10, and choose the best answer. We can use the following principle: \
            #    \n1.Accuracy of the information: Assess the accuracy of the information provided by the assistant. This includes checking if the information is factual, up-to-date, and relevant to the question asked. \
            #    \n2.Clarity and coherence: Evaluate the clarity and coherence of the answer. Does it provide a clear and concise explanation of the topic? Is it well-organized and easy to follow? \
            #    \n3.Usefulness: Assess the usefulness of the information provided by the assistant. Does it provide practical solutions or insights that can help the user in their decision-making process? \
            #    \n4.Personalization: Evaluate the personalization of the answer. Does it take into account the user's needs, preferences, and goals? \
            #    \n5.Engagement: Assess the engagement level of the answer. Does it encourage the user to ask further questions or seek more information? \
            #    \nanswer A: {ansa} \nanswer B: {ansb} \nanswer A score: \nanswer B score: \nthe best answer:"
            #prompt="The question: {quest} \n has four answer, please evaluate the answers and give a score between 0 and 10, and choose the best answer. We can use the following principle: \
            #    \n1.Accuracy of the information: Assess the accuracy of the information provided by the assistant. This includes checking if the information is factual, up-to-date, and relevant to the question asked. \
            #    \n2.Clarity and coherence: Evaluate the clarity and coherence of the answer. Does it provide a clear and concise explanation of the topic? Is it well-organized and easy to follow? \
            #    \n3.Usefulness: Assess the usefulness of the information provided by the assistant. Does it provide practical solutions or insights that can help the user in their decision-making process? \
            #    \n4.Personalization: Evaluate the personalization of the answer. Does it take into account the user's needs, preferences, and goals? \
            #    \n5.Engagement: Assess the engagement level of the answer. Does it encourage the user to ask further questions or seek more information? \
            #    \nanswer A: {ansa} \nanswer B: {ansb} \nanswer C: {ansc} \nanswer D: {ansd} \nanswer A score: \nanswer B score: \nanswer C score: \nanswer D score: \nthe best answer:"
            #prompt="[System]We would like to request your feedback on the performance of the assistant's responses to the user question displayed below. Please evaluate the answers and give a score between 0 and 10. We can use the following principle:\n1.Accuracy of the information: Assess the accuracy of the information provided by the assistant. This includes checking if the information is factual, up-to-date, and relevant to the question asked. \n2.Clarity and coherence: Evaluate the clarity and coherence of the answer. Does it provide a clear and concise explanation of the topic? Is it well-organized and easy to follow? \n3.Usefulness: Assess the usefulness of the information provided by the assistant. Does it provide practical solutions or insights that can help the user in their decision-making process? \n4.Personalization: Evaluate the personalization of the answer. Does it take into account the user's needs, preferences, and goals? \n5.Engagement: Assess the engagement level of the answer. Does it encourage the user to ask further questions or seek more information? Make sure the feedback strictly follow this format:Evaluation evidence: <your explanation of answer A here>Score: <score of answer A>Evaluation evidence: <your explanation of answer B here>Score: <score of answer B>Evaluation evidence: <your explanation of answer C here>Score: <score of answer C>Evaluation evidence: <your explanation of answer D here>Score: <score of answer D>\n[User Question] {quest}\n[Assistant’s Answer A]{ansa}\n[Assistant’s Answer B]{ansb}\n[Assistant’s Answer C]{ansc}\n[Assistant’s Answer D]{ansd}\n"
            
            #8input
            # prompt="[Question]{quest}\n[The Start of Assistant 1's Answer]{ansa}\n[The End of Assistant 1's Answer]\n[The Start of Assistant 2's Answer]{ansb}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{ansc}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{anse}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{anse}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{ansf}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{ansg}\n[The End of Assistant 2's Answer]\n[The Start of Assistant 2's Answer]{ansh}\n[The End of Assistant 2's Answer]\n[System]\nYou are a helpful and precise assistant for checking the quality of the answer. We would like to request your feedback on the performance of eight AI assistants in response to the user question displayed above.\nPlease rate the helpfulness, relevance, accuracy, level of details of their responses. Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.\nPlease first output a single line containing only eight values indicating the scores for Assistant 1,2,3,4,5,6,7 and 8, respectively. The eight scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.\n"
            #4input

            # prompt="【直播信息开始】\n{content}\n【直播信息结束】\n【结构化信息开始】\n{info}\n【结构化信息结束】\n请你严格按照如下步骤操作：\n步骤一：从【直播信息】中提取以'产品名称'、'类目'、'品牌'、'产品属性'、'产品价格'、'产品卖点'、'产品优势'为key的json格式内容，不用返回未提及的字段；\n步骤二：将步骤一提取的json内容，与【结构化信息】中json的key做完整对比，并以0到10分表示匹配程度，如果步骤一返回json'未提及'的则不用对比，如果步骤一提到了【结构化信息】中json未提到的/完全不匹配的则直接给0分；\n步骤三：给出0到10分的综合评分，并返回以'score'为key的json格式内容"
            # prompt="【直播信息开始】\n{content}\n【直播信息结束】\n【结构化信息开始】\n{info}\n【结构化信息结束】\n请你严格按照如下步骤操作：\n步骤一：从【直播信息】中提取以'产品名称'、'类目'、'品牌'、'产品属性'、'产品价格'、'产品卖点'、'产品优势'为key的json格式内容，不用返回未提及的字段；\n步骤二：将步骤一提取的json内容，与【结构化信息】中json的key做完整对比，并以0到10分表示匹配程度，仅需对步骤一提取的有效json字段做对比，如果步骤一返回'未提及'的则不用对比，如果步骤一提到了【结构化信息】中json未提到的/完全不匹配的则直接给0分；\n步骤三：给出0到10分的综合评分，并返回以'score'为key的json格式内容，注意，无法对比则返回None。"
            prompt="【直播信息开始】\n{content}\n【直播信息结束】\n【结构化信息开始】\n{info}\n【结构化信息结束】\n请你严格按照如下步骤操作：\n步骤一：从【直播信息】中提取以'产品名称'、'类目'、'品牌'、'产品属性'、'产品价格'、'产品卖点'、'产品优势'为key的json格式内容，不用返回未提及的字段；\n步骤二：将步骤一提取的json内容，与【结构化信息】中json的key做完整对比，并以0到10分表示匹配程度，仅需对步骤一提取的有效json字段做对比，如果【直播信息】'未提及'的则不用对比，如果【直播信息】提到了【结构化信息】中json未提到的/完全不匹配的则直接给0分；\n步骤三：给出0到10分的综合评分，并返回以'score'为key的json格式内容，注意，无法对比则返回None。"
            prompt="【直播信息开始】\n{content}\n【直播信息结束】\n【结构化信息开始】\n{info}\n【结构化信息结束】\n请你严格按照如下步骤操作：\n步骤一：从【直播信息】中提取以\'产品名称\'、\'类目\'、\'品牌\'、\'产品属性\'、\'产品价格\'、\'产品卖点\'、\'产品优势\'为key的json格式内容。注意，无法提取的则置空；\n步骤二：将步骤一提取有返回并有效的内容，与【结构化信息】中对应的key做对比，并以0到10分表示匹配程度；注意，步骤一未提取到的、空的（如：\"无\"、\"\"、\"未提及\"）属于无效内容，因此不需要给出分数；若步骤一返回的是有效内容，且步骤一返回的内容与【结构化信息】中不符合的则直接给0分；\n步骤三：根据步骤二给出的已提及的内容，给出0到10分的综合评分，并返回以\'score\'为key的json格式内容，注意，无法对比则返回None。\n最后，请你按照上述步骤分步操作。"
            request.session_id = str(query[id_key])  #注意对于多轮对话需要记历史的，那么一个对话一个 session_id
            request.req_id = str(query[id_key])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][2]['output'],ansd=query['candidates'][3]['output'])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][0]['output'],ansd=query['candidates'][1]['output'])
            
            #8input
            # request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'], \
            #         ansc=query['candidates'][0]['output'],ansd=query['candidates'][1]['output'], \
            #         anse=query['candidates'][0]['output'],ansf=query['candidates'][1]['output'], \
            #         ansg=query['candidates'][0]['output'],ansh=query['candidates'][1]['output'] )
            #4input
            input_info=re.findall(r"({.*})",query['data'][0]['question'],re.S)[0]
            request.query = prompt.format(content=query['answer'],info=input_info)
            
            #发起请求
            resp = grpc_client.Chat(request, timeout=time_out)
            resp = json.loads(MessageToJson(resp))
            if resp['status']['code'] != 'SUCESS':
                logger.info('%s 接口调用失败,重试 %d, status_code=%s', query[id_key], i+1, resp['status']['code'])
                time.sleep(random.randint(i*10, (i+1)*10))
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
    #biz = 'liupengli_699d56a9_gpt3.5'
    biz = 'zhaoyi07_60c690ac_gpt4'
    biz='chenzhengzong_a86b0661_gpt-35-turbo-1106'
    if gpt_version == 'gpt4':
        # biz = 'liupengli_699d56a9_gpt-4-0125-Preview'
        biz='fujiayi_cf674765_gpt-4-0125-Preview'
        # biz='chenzhengzong_a86b0661_gpt-4-0125-Preview'
    
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
            status, resp = process_with_retry(grpc_client, request, x, timeout, 5, id_key)  
            if status != 0:
                continue
            if resp['status']['code'] != 'SUCESS':
                logger.error('%s 接口调用失败, status_code=%s', x[id_key], resp['status']['code'])
                continue
            try:
                x['gpt4answer'] = resp['answer']
                json_str = json.dumps(x, ensure_ascii=False)
                fo.write(json_str + '\n')
                fo.flush()                
                logger.info(str(x[id_key]) + '\tdone')
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


