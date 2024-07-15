#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import logging
import time
from google.protobuf import text_format

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

def chat(grpc_client: GrpcClient, timeout: float):

    try:
        #构造request, biz需根据实际申请的进行修改
        biz = 'liupengli_699d56a9_gpt4'
        request = MmuChatGptRequest(biz=biz)
        request.session_id = 'test'
        request.req_id = '1000'
        #发起请求
        quest="If Lucy would give Linda $5, Lucy would have the same amount of money as Linda. If Lucy originally had $20, how much money did Linda have at the beginning?"
        ansa="1. If Lucy gives $5 to Linda, then Lucy would have $20 - $5 = $15 left.\n2. Because Lucy and Linda would have the same amount of money after the exchange, Linda must have started with $15 before she received the $5 from Lucy.\n3. Therefore, Linda originally had $15 - $5 = $10.\nThe answer is 10."
        ansb="If Lucy gives Linda $5, she would have $20 - $5 = $15 left. Since both Lucy and Linda would have the same amount of money after the transaction, that means Linda originally had $15.\nThe answer is 15."
        ansc="1. If Lucy gives $5 to Linda, then Lucy would have $20 - $5 = $15 left.\n2. Because Lucy and Linda would have the same amount of money after the exchange, Linda must have ended with $15 after she received the $5 from Lucy.\n3. Therefore, Linda originally had $15 - $5 = $10.\nThe answer is 10."
        prompt='question: {quest} has many answer, please give each answer a score between 0 and 10 from the following principle:\n\n1. Correctness of the solution: Check whether the answer is correct or not. Give a higher score for correct answers and lower for incorrect answers. Make sure to check all the calculations and steps.\n\n2. Completeness of the solution: Assess whether the answer includes all necessary steps, calculations, and explanations. Deduct points for missing information or incomplete solutions.\n\n3. Clarity of explanation: Evaluate how clearly and comprehensively the answer explains the solution. Does it use proper terminology and notation? Give a higher score for answers that are easy to understand and follow.\n\n4. Neatness and organization: Assess the presentation of the answer. Is it well-organized and neat? Give additional points for answers that are visually appealing and easy to read.\n\n5. Efficiency of the solution: Determine if the solution provided is the most efficient and optimal approach to solve the math problem. Give a higher score for answers that demonstrate an efficient method or shortcut.\n\nBased on these criteria, assign a score to each answer as follows:\n\nCriteria      | Score\n---------------|---------\nCorrectness    | 0-4\nCompleteness   | 0-2\nClarity        | 0-2\nNeatness       | 0-1\nEfficiency     | 0-1\n\nAdd the scores from each criterion to get a total score between 0 and 10. A higher score indicates a better answer, while a lower score indicates a less effective or incorrect solution. \n\nFor example, a perfect score of 10 would indicate a correct, complete, clear, neat, and efficient solution to the math problem. answer a: {ansa}, answer b: {ansb}, answer c: {ansc}, answer a score:, answer b score:, answer c score:'
        #prompt='question: {quest} has many answer, please give each answer a score between 0 and 10 from the aspect of correctness of solution, completeness of solution and clarity of explanation, answer a: {ansa}, answer b: {ansb}, answer c: {ansc}, answer a score:, answer b score:, answer c score:'
        #prompt='对于数学问题 {quest}，有如下多个答案，请从正确性、完整性和表达清晰度等方面做0-10打分，答案A: {ansa}，答案B: {ansb}，答案C: {ansc}，答案A得分：，答案B得分：，答案C得分：'
        #request.query='I have a math problem and many answer, please construct a principle to evaluate the answer and give a score between 0 and 10'
        request.query=prompt.format(quest=quest,ansa=ansa,ansb=ansb,ansc=ansc)
        print(request.query)
        resp = grpc_client.Chat(request, timeout=timeout)
        #打印结果
        logger.info(text_format.MessageToString(resp, as_utf8=True))

    except Exception as e:
        logger.error('发生异常, err: %s', e)


if __name__ == "__main__":

    #服务名不要改动
    client_option = ClientOption(
        biz_def='mmu',
        grpc_service_name='mmu-chat-gpt-service',
        grpc_stub_class=MmuChatGptServiceStub,
    )

    client = GrpcClient(client_option)
    chat(client, 2000)
    logger.info('call end')
