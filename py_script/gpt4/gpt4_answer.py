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


def process_with_retry(grpc_client: GrpcClient, request, query, time_out, n_times, id_key, seed):
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
            request.session_id = str(query[id_key])  #注意对于多轮对话需要记历史的，那么一个对话一个 session_id
            request.req_id = str(query[id_key])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][2]['output'],ansd=query['candidates'][3]['output'])
            #request.query = prompt.format(quest=query['input'],ansa=query['candidates'][0]['output'],ansb=query['candidates'][1]['output'],ansc=query['candidates'][0]['output'],ansd=query['candidates'][1]['output'])
            request.query = query['input']
            
            #config
            request.config['output_len']="-1"
            # request.config['temperature']="0.5"
            #default seed=122
            request.config['random_seed']=str(seed)
            # request.config['temperature']="0.5"
            

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


def chat(grpc_client: GrpcClient, timeout: float, in_fn, out_fn, gpt_version, seed, id_key='id'):
    #构造request, biz需根据实际申请的进行修改
    assert gpt_version in ['gpt3', 'gpt3.5', 'gpt4', '66B']
    biz = 'zhaoyi07_60c690ac_gpt4'
    #biz = 'liupengli_699d56a9_gpt3.5'
    biz='liupengli_699d56a9_gpt-4-0125-Preview'

    #if gpt_version == 'gpt4':
    #    biz = 'liupengli_699d56a9_gpt4'
    if gpt_version=='66B':
        biz='luoyunkun_dee719d0_base_66b'
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
            id_key=id_key if 'id_key' in x.keys() else 'id'
            id=x[id_key]+'_'+seed
            if id in done_cases:
                continue
            status, resp = process_with_retry(grpc_client, request, x, timeout, 5, id_key, seed)  
            if status != 0:
                continue
            if resp['status']['code'] != 'SUCESS':
                logger.error('%s 接口调用失败, status_code=%s', id, resp['status']['code'])
                continue
            try:
                x['answer'] = resp['answer']
                x['source'] = gpt_version
                x['id_key'] = id
                json_str = json.dumps(x, ensure_ascii=False)
                fo.write(json_str + '\n')
                fo.flush()                
                logger.info(str(id) + '\tdone')
            except Exception as e:
                logger.error('发生异常 %s\t%s', id, e)
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
    chat(client, 160, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], id_key='id') #输入文件的id字段在这儿配置
    logger.info('call end')


