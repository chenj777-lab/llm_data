#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by MaxFu
from pathlib import Path
import json
from google.protobuf.json_format import MessageToDict
import time
import os
from argparse import ArgumentParser
from collections import defaultdict
import re
import random
import string
from kess.framework import ClientOption, GrpcClient
import protos.mmu_kuaiyi_chat_pb2 as mmu_kuaiyi_chat_pb2
from protos.mmu_kuaiyi_chat_pb2_grpc import KuaiYiChatServiceStub
from google.protobuf.json_format import MessageToDict
import sys
grpc_service_name = "mmu-kuaiyi-chat-service"
sys.path.append('/home/chenzhengzong/from_nlp_group/rm_dataset/gpt4_api')

client_option = ClientOption(
    biz_def='infra',
    grpc_service_name=grpc_service_name,
    grpc_stub_class=KuaiYiChatServiceStub,
)
client = GrpcClient(client_option)

# from utils import load_jsonl, dump_jsonl, get_lines_from_file, write_lines_to_file



def __show_model_list(biz):
    stub = client.get_stub()
    req = mmu_kuaiyi_chat_pb2.KuaiYiChatModelsRequest()
    req.key = biz
    modelRsp = stub.Models(req)
    print(modelRsp)


def __cmd( in_fn, out_fn):
    """命令行参数."""
    # parser = ArgumentParser(description="")
    # args = parser.parse_args()


    # sys_msg = mmu_kuaiyi_chat_pb2.MessageInfo()
    # sys_msg.role = "system"
    # sys_msg.content = "我是「快意」。"
    # req.messages.append(sys_msg)
    prompt_livev2="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。注意，询问或留下联系方式代表用户具有意图，比如询问加微信、电话号码。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度。\n<examples>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意只有表情符无法判断意图。\n\n<user input>\n{car}\n \n<your reply>\n"
    prompt_decov2="<background>\n你现在是一位家具建材方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【装修】目的和需求。注意，询问或留下联系方式代表用户具有意图，比如询问加微信、电话号码。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【装修】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【装修】意图或兴趣，总结【装修】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【装修】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表装修意图的强度。\n<examples>\ninput：100平米落地多少钱，我家刚买了新房，怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：全国各地都能来施工吗？吉林有吗？吉林有店吗？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：设计方案挺好的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：真的假的reply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：看着不错啊\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\n\ninput：门框怎么卖\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：[玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n\ninput：.......近期的话，绿=律\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\n\ninput：有屁用还吹，赚你妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：双击支持，真情传递，红心点亮，支持友友一路长虹[火][赞🐎🐘🌾🌴\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：你们公司在哪？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 80}`\n\ninput：买一瓶可以吗？春节发货吗？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与装修无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问装修相关信息>也属于有意图。\n注意<用户提供相关信息>也属于有意图。\n注意请在最后给出你的原因。\n\n<user input>\n{car}\n\n<your reply>\n"
    prompt_carv2="<background>\n你现在是一位汽车方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【购买汽车】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户购车需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【购买汽车】意图，总结【购买汽车】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【购买汽车】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表购买意图的强度。\n<examples>\ninput：店铺在哪，给个联系电话，询问汽车型号，价格多少，多少钱/米\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：地址在哪\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 70}`\n \ninput：怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：这车不错，一汽奥迪豪华大气上档次[赞][赞][赞]\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n \ninput：可以，好的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：美女/帅哥讲的不错\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：你好，不客气，早上好，哈工李军陌陌摸摸\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n \ninput：[玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：放屁，我买了不好用，不要买\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n input：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：@广汽传祺好车，值得拥有支持国产车\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：wky7799888\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：有175-60-15的轮胎吗？多少钱一个\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：我要是有钱买你那车？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：不要。就是看一下视频\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与汽车无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问汽车品牌相关信息>也属于有意图。\n注意请在最后给出你的原因。\n\n\n<user input>\n{car}\n \n<your reply>\n"
    prompt_livev2="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度。\n<examples>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与服务无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意请在最后给出你的原因。\n\n<user input>\n {car}\n \n<your reply>\n"
    prompt_carv2="<background>\n你现在是一位汽车方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【购买汽车】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户购车需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【购买汽车】意图，总结【购买汽车】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【购买汽车】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表购买意图的强度。\n<examples开始>\ninput：店铺在哪，给个联系电话，询问汽车型号，价格多少，多少钱/米\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：地址在哪\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 70}`\n \ninput：怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：这车不错，一汽奥迪豪华大气上档次[赞][赞][赞]\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n \ninput：可以，好的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：美女/帅哥讲的不错\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：你好，不客气，早上好，哈工李军陌陌摸摸\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n \ninput：[玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：放屁，我买了不好用，不要买\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n input：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：@广汽传祺好车，值得拥有支持国产车\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：wky7799888\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：有175-60-15的轮胎吗？多少钱一个\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：我要是有钱买你那车？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：不要。就是看一下视频\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<example结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<[赞][赞][赞]>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与汽车无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问汽车品牌、活动相关信息>也属于有意图。\n注意<表情符>无法判断意图。\n注意<[666]>无法判断意图。\n注意请在最后给出你的原因，无关信息请直接判断无意图。\n\n\n<user input>\n{car}\n<your reply>\n"
    prompt_livev2_debug="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度，60分以上为有意图。\n<examples开始>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<examples结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与服务无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意无关信息请直接判断无意图，请在最后给出你的原因。\n\n<user input开始>\n{car}\n<user input结束>\n \n<your reply>"
    prompt_livev2="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度，60分以上为有意图。\n<examples开始>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<examples结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<只有表情符>无法判断意图。\n注意<用户提供了手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与服务无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意除了上面提到的，无关信息请直接判断无意图，请在最后给出你的原因，并返回格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n \n<your reply>\n"
    prompt_livev2="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度，60分以上为有意图。\n<examples开始>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<examples结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<只有表情符>无法判断意图。\n注意<用户提供了手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与服务无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意除了上面提到的，无关信息请直接判断无意图，请在最后给出你的原因，并返回标准格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n \n<your reply>\n"
    prompt_decov2="<background>\n你现在是一位家具建材方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【装修】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【装修】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【装修】意图或兴趣，总结【装修】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【装修】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表装修意图的强度，60分以上为有意图。\n<examples开始>\ninput：100平米落地多少钱，我家刚买了新房，怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：全国各地都能来施工吗？吉林有吗？吉林有店吗？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：设计方案挺好的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：看着不错啊\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\n\ninput：门框怎么卖\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n\ninput：.......近期的话，绿=律\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\n\ninput：有屁用还吹，赚你妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：双击支持，真情传递，红心点亮，支持友友一路长虹[火][赞🐎🐘🌾🌴\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：你们这是哪里的呀？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 80}`\n\ninput：买一瓶可以吗？春节发货吗？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：朱女士\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<examples结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<用户提供了手机号、微信等联系方式>表示具有意图。\n注意<与装修无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问装修相关信息>也属于有意图。\n注意<用户提供房屋地址、尺寸等相关信息>也属于有意图。\n注意<用户询问公司/厂家/门店地址、位置等所在地>表示有装修的打算，直接判断有意图。\n注意<表情符、乱码>无法判断意图。\n注意除了上面提到的，无关信息请直接判断无意图，请在最后给出你的原因。\n\n\n<user input开始>\n{car}\n<user input结束>\n\n\n<your reply>\n"
    prompt_carv2="<background>\n你现在是一位汽车方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【购买汽车】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户购车需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【购买汽车】意图，总结【购买汽车】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【购买汽车】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表购买意图的强度。\n<examples开始>\ninput：店铺在哪，给个联系电话，询问汽车型号，价格多少，多少钱/米\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：地址在哪\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 70}`\n \ninput：怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：这车不错，一汽奥迪豪华大气上档次[赞][赞][赞]\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n \ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：好的/是呀/看了/在\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：美女/帅哥讲的不错\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：你好，不客气，早上好，哈工李军陌陌摸摸\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n \ninput：放屁，我买了不好用，不要买\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n input：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：@广汽传祺好车，值得拥有支持国产车\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：wky7799888\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：有175-60-15的轮胎吗？多少钱一个\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：我要是有钱买你那车？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：不要。就是看一下视频\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<example结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<[赞][赞][赞]>无法判断意图。\n注意<用户提供了手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问汽车品牌、活动相关信息>也属于有意图。\n注意<表情符、乱码>无法判断意图。\n注意<[666]>无法判断意图。\n注意无关信息请直接判断无意图，请在最后给出你的原因，并返回标准格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n\n<your reply>\n"
    prompt_carv2="<background>\n你现在是一位汽车方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【购买汽车】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户购车需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【购买汽车】意图，总结【购买汽车】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【购买汽车】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表购买意图的强度。\n<examples开始>\ninput：多少钱/米\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：地址在哪\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 70}`\n \ninput：怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：这车不错，一汽奥迪豪华大气上档次[赞][赞][赞]\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n \ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：好的/是呀/看了/在\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：美女/帅哥讲的不错\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：你好，不客气，早上好，哈工李军陌陌摸摸\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n \ninput：放屁，我买了不好用，不要买\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n input：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：@广汽传祺好车，值得拥有支持国产车\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：wky7799888\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：有175-60-15的轮胎吗？多少钱一个\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：我要是有钱买你那车？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：不要。就是看一下视频\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<example结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<[赞][赞][赞]>无法判断意图。\n注意<用户提供手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问汽车品牌、活动相关信息>也属于有意图。\n注意<表情符、乱码>无法判断意图。\n注意<[666]>无法判断意图。\n注意无关信息请直接判断无意图，请在最后给出你的原因，并返回标准格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n\n<your reply>"
    prompt_carv2_debug="<background>\n你现在是一位汽车方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【购买汽车】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户购车需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【购买汽车】意图，总结【购买汽车】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【购买汽车】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表购买意图的强度。\n<examples开始>\ninput：多少钱/米\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：地址在哪\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 70}`\n \ninput：怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n \ninput：这车不错，一汽奥迪豪华大气上档次[赞][赞][赞]\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n \ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：好的/是呀/看了/在\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：美女/帅哥讲的不错\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：你好，不客气，早上好，哈工李军陌陌摸摸\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n \ninput：放屁，我买了不好用，不要买\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n input：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：@广汽传祺好车，值得拥有支持国产车\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：wky7799888\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：有175-60-15的轮胎吗？多少钱一个\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：我要是有钱买你那车？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：不要。就是看一下视频\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<example结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<[赞][赞][赞]>无法判断意图。\n注意<用户提供手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<咨询是否真实有效>属于有意图。\n注意<用户询问汽车品牌、活动相关信息>也属于有意图。\n注意<表情符、乱码>无法判断意图。\n注意无关信息请直接判断无意图，请在最后给出你的原因，并返回标准格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n\n<your reply>"
    prompt_livev2="<background>\n你现在是一位生活服务方面的专家，能够通过用户在短视频、直播下评论或咨询中准确提取客户是否存在【到店接受服务】目的和需求。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【到店接受服务】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【到店接受服务】意图，总结【到店接受服务】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【到店接受服务】意图，其中如果是电商需求类，无需到店接受服务的判定为无意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表【到店】接受服务意图的强度，60分以上为有意图。\n<examples开始>\ninput：可以祛痘吗？费用多少？效果真实吗？\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\ninput：确实不错，值得信赖。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：是出生就有，是血管瘤，在眼晴和鼻子傍边，小时侯烤电，现在剩下很少。你们是在那里。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：真的假的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：可以\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\ninput：能不能出个纹身的过程视频看看\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 30}`\n\ninput:50度的烧酒多少钱一瓶\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput: [玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n \ninput：有屁用还吹，赚你\n妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n<examples结束>\n上面是一些示例，下面请做出你的判断，并遵循如下规则：\n注意<只有表情符>无法判断意图。\n注意<用户提供了手机号、微信等联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与服务无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意除了上面提到的，无关信息请直接判断无意图，请在最后给出你的原因，并返回标准格式化内容。\n\n<user input开始>\n{car}\n<user input结束>\n \n<your reply>"
    with open(in_fn, 'r') as fin, open(out_fn, 'a') as fo:
        for line in fin:
                
            stub = client.get_stub()
            req = mmu_kuaiyi_chat_pb2.KuaiYiChatCompletionRequest()
            req.key = "fuyan05_dee719d0_base_v2"

            # 打印模型
            # __show_model_list(req.key)

            # 根据第一步中的可见模型
            # req.model = "kuaiyi-66B"
            req.model = "kuaiyi-66B"
            req.stream = False
            req.n = 1
            req.max_tokens = 2048
            req.repetition_penalty = 1.01
            req.temperature = 0.7
            req.top_p = 0.9
            req.random_seed = 122

            start_time = time.time()
            query = json.loads(line.strip())
            if query['first_industry_name']=='交通' or query['first_industry_name']=='汽车':
                prompt=prompt_carv2_debug
            elif query['first_industry_name']=='家居建材':
                prompt=prompt_decov2
            elif query['first_industry_name']=='生活服务':
                prompt=prompt_livev2

            msg1 = mmu_kuaiyi_chat_pb2.MessageInfo()
            
            msg1.role = "user"
            # msg1.content = '你现在是一个客服人员，是一个真实的人类，你的任务是回答用户问题。在对话中，你只需简洁明了的回答问题，回答风格尽可能口语化，尽量用短句，回答不要超过10个字。\n请遵循以下原则：\n1.你始终需要保持客服的身份，用客服的身份与用户进行对话。记住你不是虚拟助手。\n2.你的所在地就是招聘要求中的工作地点。\n3.你的任务只是针对性回答问题，此外没有任何任务。不需要引导用户报名，也不需要反问用户，也不需要主动向用户提供帮助。\n4.如果用户问到无法理解的问题，不回答用户的问题。\n5.如果用户问你的联系方式，可以回复公司要求不能发送联系方式，回复"稍等下"。\n6.用户有报名或者其他诉求，你告诉他们"稍等下"。\n7.用户如果说你好或者打招呼，回复"稍等下"。\n\n岗位介绍：岗位名称：操作工\n工作内容：在工厂完成上级安排的工作\n工作地点：北京市-海淀区-中关村街道\n工作时间：早九晚五\n薪资福利：每月5000-8000\n你的招聘要求是：性别要求：男性\n年龄要求：20-50岁\n所在地要求：北京\n请根据以上指导原则用客服的身份进行对话，用10个字以内的文本为求职者答疑。\n'
            # msg1.content = "我是「快意」，是一款由快手AI团队打造的大规模语言模型。我基于海量数据和知识持续迭代进化，拥有广泛的多领域知识和创作才能，具备出色的语言理解和生成能力，能够理解并高效执行各类任务。我擅长知识问答、文案创作、文字翻译、数学逻辑、代码理解和编写等任务，致力于全方位帮助用户解决各种问题，期待能够为你提供更智能、轻快的互动体验 。 问题: <background>\n你现在是一位家具建材方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【装修】目的和需求。注意，询问或留下联系方式代表用户具有意图，比如询问加微信、电话号码。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【装修】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【装修】意图或兴趣，总结【装修】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【装修】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表装修意图的强度。\n<examples>\ninput：100平米落地多少钱，我家刚买了新房，怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：全国各地都能来施工吗？吉林有吗？吉林有店吗？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：设计方案挺好的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：真的假的\u000breply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：看着不错啊\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\n\ninput：门框怎么卖\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：[玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n\ninput：.......近期的话，绿=律\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\n\ninput：有屁用还吹，赚你妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：双击支持，真情传递，红心点亮，支持友友一路长虹[火]\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：你们公司在哪？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 80}`\n\ninput：买一瓶可以吗？春节发货吗？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与装修无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<���户询问装修相关信息>也属于有意图。\n注意<用户提供相关信息>也属于有意图。\n注意请在最后给出你的原因。\n\n<user input>\n[玫瑰][玫瑰][玫瑰][赞][赞][赞]\n\n<your reply>\n 答案: "
            # msg1.content = "<background>\n你现在是一位家具建材方面的专家，能够通过用户在短视频、直播下评论或者咨询中准确提取客户的【装修】目的和需求。注意，询问或留下联系方式代表用户具有意图，比如询问加微信、电话号码。\n<instruction>\n在任何情况下都不要破坏角色。\n表达要简洁明了，避免多余的描述性文字。\n提供详实的客户【装修】需求。\n严格遵守提供准确信息的原则。\n<workflow>\n用户输入一段评论, 你只会判断用户是否具有【装修】意图或兴趣，总结【装修】意图的程度，不用做任何推测和揣摩\n- 输出内容中必须包含以下内容，且以markdown格式输出\n1. 是否具有【装修】意图：\n1）`{\"intent\": true}`\n2）`{\"intent\": false}`\n2. 意图程度\n- `{\"intent_score\": <score>}`\n其中 `<score>` 是一个介于 0 到 100 之间的整数，代表装修意图的强度。\n<examples>\ninput：100平米落地多少钱，我家刚买了新房，怎么联系\nreply: `{\"intent_to_purchase\": true}``{\"intent_score\": 90}`\n\ninput：全国各地都能来施工吗？吉林有吗？吉林有店吗？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：联系我，你电话多少？或者我加你微信。\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：设计方案挺好的\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 70}`\n\ninput：真的假的\u000breply: `{\"intent_to_purchase\": true }``{\"intent_score\": 60}`\n\ninput：看着不错啊\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 50}`\n\n\ninput：门框怎么卖\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 30}`\n\ninput：[玫瑰][玫瑰][玫瑰][赞][赞][赞]\nreply: `{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n\ninput：.......近期的话，绿=律\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：123456\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：15911137891\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 90}`\n\n\ninput：@૮₍ ˶•-•˶₎ა(O639511218)\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 40}`\n\n\ninput：有屁用还吹，赚你妈，坑比，全是骗人的\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\n\ninput：双击支持，真情传递，红心点亮，支持友友一路长虹[火]\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n\ninput：你们公司在哪？\nreply: `{\"intent_to_purchase\": true }``{\"intent_score\": 80}`\n\ninput：买一瓶可以吗？春节发货吗？\nreply: `{\"intent_to_purchase\": false }``{\"intent_score\": 0}`\n注意<只有表情符>无法判断意图。\n注意<提供了联系方式>表示具有意图。\n注意<用户询问店铺或者公司等线下地址>属于具有意图。\n注意<与装修无关内容>无法判断意图。\n注意<咨询是否真实有效>属于有意图。\n注意<���户询问装修相关信息>也属于有意图。\n注意<用户提供相关信息>也属于有意图。\n注意请在最后给出你的原因。\n\n<user input>\n[玫瑰][玫瑰][玫瑰][赞][赞][赞]\n\n<your reply>\n "
            msg1.content=prompt.replace("{car}",str(query['input']))
            req.messages.append(msg1)
            query['prompt_input']=msg1.content

            msg2 = mmu_kuaiyi_chat_pb2.MessageInfo()
            msg2.role = "assistant"
            # msg2.content = "{'assistant': '`{\"intent_to_purchase\": false}``{\"intent_score\": 0}`\n\n原因：该用户输入的电话号码与装修无关，无法判断其具有装修意图。'}"
            req.messages.append(msg2)
            
            # msg3 = mmu_kuaiyi_chat_pb2.MessageInfo()
            # msg3.role = "user"
            # msg3.content = '为什么'
            # req.messages.append(msg3)
            
            # msg4 = mmu_kuaiyi_chat_pb2.MessageInfo()
            # msg4.role = "assistant"
            # req.messages.append(msg4)

            # ! 调用Chat
            response = stub.Chat(req)
            output = ""
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("程序耗时：{:.2f}秒".format(elapsed_time))
            
            print(MessageToDict(response))
            print(MessageToDict(req))
            if(len(response.choices) > 0):
                output = response.choices[0].message["assistant"]
            query['answer'] = output
            fo.write(json.dumps(query,ensure_ascii=False)+'\n')


    # print(output)


if __name__ == "__main__":
    __cmd(sys.argv[1], sys.argv[2])