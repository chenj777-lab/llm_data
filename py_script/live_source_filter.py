# -*- coding: utf-8 -*-
import numpy as np
import datetime
import sys
from collections import defaultdict

"""
@file: live_source_filter.py
@author: chenzhengzong
@time: 2021/5/8 下午14:45
-----------------------------------
Change Activity: 2021/5/8 下午14:45


输入数据格式：主播id，直播间id，直播间起始时间，直播间结束时间，粉丝个数，直播类型，直播内容类型，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 其中每个用户根据进入时间从小到大排序, 同一时刻可能进入多个用户


"""

kLiveInfoLen = 8 #直播信息长度
kUserInfoLen = 4 #单用户的信息长度
kMinOnlineUserNum = 1 #直播间最小观看人数阈值


def live_source_type_filter(infile, live_source_allow_str, outfile):
    '''
    统计每个直播间的长播率
    :param infile:输入文件
    :param live_source_allow_str:允许的直播来源类型，以","分割
    :param outfile:输出文件
    :return:
    '''
    live_id_user_info = defaultdict(list)  # 记录每个直播间id对应的用户信息
    live_source_allow_list = live_source_allow_str.strip().split(',')
    live_source_type_allow = dict.fromkeys(live_source_allow_list)

    with open(infile) as f, open(outfile, 'w') as wfile:
        num_texts = 0
        num_texts_error = 0
        for text in f:
            num_texts += 1
            texts = text.strip().split('\t')
            if len(texts) <= kLiveInfoLen:
                continue
            live_id = texts[1]
            for user_index in range(kLiveInfoLen,len(texts)):
                user_info_str = texts[user_index]
                user_info_arr = user_info_str.strip().split(',')
                if len(user_info_arr) < kUserInfoLen:
                    continue
                user_id = user_info_arr[0].strip()
                user_start_timestamp = user_info_arr[1].strip()
                user_end_timestamp = user_info_arr[2].strip()
                live_source_type = user_info_arr[3].strip()
                #对于不满足直播来源的用户过滤
                if live_source_type not in live_source_type_allow:
                    continue
                tmp = user_id + ', ' + user_start_timestamp + ', ' + user_end_timestamp + ', ' + live_source_type
                live_id_user_info[live_id].append(tmp)
            #无满足用户的直播则过滤
            if live_id not in live_id_user_info:
                continue

            for author_info_index in range(kLiveInfoLen):
                wfile.write(texts[author_info_index] + '\t')
            for u_info in live_id_user_info[live_id]:
                wfile.write(u_info + '\t')
            wfile.write('\n')

if __name__ == "__main__":
    live_source_type_filter(sys.argv[1],sys.argv[2],sys.argv[3])
