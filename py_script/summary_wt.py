# -*- coding: utf-8 -*-
import collections
import datetime
import glob
import multiprocessing as mp
import numpy as np
import os
import time
import shutil
import sys
from collections import defaultdict
"""
@file: summary_lvtr.py
@author: zhoupeng
@time: 2021/5/11 上午10:28
-----------------------------------
Change Activity: 2021/5/11 上午10:28
统计每个直播间的每个时刻的观看时长
输出从直播开始到直播结束时间范围内，每个时刻的lvtr
每15秒算一个时刻
输入数据格式：主播id, 直播间id, 直播间起始时间，直播间结束时间，粉丝个数，直播类型（1:视频直播|2:语音直播|3:聊天室直播|-124:未知），直播内容类型(shop:电商，game:游戏,other:其他（优先级 电商 > 游戏 > 其他）)，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 
1059272464      7973122543      2021-04-21 20:43:04     2021-04-21 20:52:37     50506   1       other   UNKNOWN 1902243240, 2021-04-21 20:43:25, 2021-04-21 20:43:28, LS_FOLLOW 1506573680, 2021-04-21 20:43:29, 2021-04-21 20:43:37, LS_FOLLOW

输出：主播id, 直播间id, 直播间起始时间，直播间结束时间，粉丝个数，直播类型（1:视频直播|2:语音直播|3:聊天室直播|-124:未知），直播内容类型(shop:电商，game:游戏,other:其他（优先级 电商 > 游戏 > 其他）)，游戏名称，平均在线观看人数，平均观看时长，每个时刻的在线观看人数和长播率

"""


def ymd_to_int(date):
    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res


def wt(infile, threshold, outfile):
    wfile = open(outfile, 'w')
    threshold = int(threshold)
    with open(infile) as f:
        for text in f:
            texts = text.strip().split('\t')
            live_start_timestamp = ymd_to_int(texts[2])
            live_end_timestamp = ymd_to_int(texts[3])
            live_user_online_timestamp_min = ymd_to_int(texts[8].strip().split(', ')[1])  # 观众进入直播间的最早时间
            live_user_online_timestamp_max = live_user_online_timestamp_min
            if live_user_online_timestamp_min < live_start_timestamp:
                live_user_online_timestamp_min = live_start_timestamp
            timestamps = []
            for user_info in texts[8:]:
                u_id, u_start_timestamp, u_end_timestamp, u_source = user_info.strip().split(', ')
                u_start_timestamp = ymd_to_int(u_start_timestamp)
                u_end_timestamp = ymd_to_int(u_end_timestamp)
                if u_start_timestamp < live_start_timestamp:
                    u_start_timestamp = live_start_timestamp
                if u_end_timestamp > live_end_timestamp:
                    u_end_timestamp = live_end_timestamp
                if u_end_timestamp < live_start_timestamp:
                    continue
                timestamps.append([u_start_timestamp, u_end_timestamp])
                if u_end_timestamp > live_user_online_timestamp_max:  # 获取最大的用户离开直播间的时间
                    live_user_online_timestamp_max = u_end_timestamp
            if live_user_online_timestamp_max < live_start_timestamp:  # 如果最大的离开时间，小于直播开始时间，则丢弃该样本
                continue
            if live_user_online_timestamp_max > live_end_timestamp:
                live_user_online_timestamp_max = live_end_timestamp
            # print(timestamps)
            total_number_each_moment = defaultdict(list)
            # sub_number_each_moment = {}
            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                # print(i, live_start_timestamp, live_end_timestamp, threshold)
                j = i + threshold
                if j < live_user_online_timestamp_min:
                    continue
                if i > live_user_online_timestamp_max:
                    # print("此刻没有在线用户。。。")
                    break
                for times in timestamps:
                    if times[0] < i < times[1]:  # 在此时刻或之前进入，并且结束时刻大于当前时刻
                        d = times[1] - i
#                        if d >= threshold:
#                           d = threshold
                        total_number_each_moment[i].append(d)
                    elif times[0] == i == times[1]:
                        total_number_each_moment[i].append(0)
                    elif i <= times[0] < j:  # 在此时刻和下一时刻之间进入
                        d = times[1] - times[0]
#                        if d >= threshold:
#                            d = threshold
                        total_number_each_moment[i].append(d)
            for k, v in total_number_each_moment.items():
                print(k, v)
            print('\n')
            watch_times = []
            radios = []
            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                if i in total_number_each_moment:
                    ds = list(total_number_each_moment[i])
                    ds = np.array(ds)
                    ds_mean = round(ds.mean(), 2)
                    radio = round(ds_mean / threshold, 4)
                else:
                    ds_mean = 0.0
                    radio = 0.0
                watch_times.append(ds_mean)
                radios.append(radio)
            tmp = len(range(live_start_timestamp, live_end_timestamp, threshold))
            print(tmp)
            mean_online_persons = round(len(timestamps) / tmp, 2)
            mean_watch_times = round(np.array(watch_times).sum() / tmp, 2)
            mean_watch_times_radio = round(np.array(radios).sum() / tmp, 4)
            print(mean_online_persons, mean_watch_times_radio)
            watch_times = [str(r) for r in watch_times]
            radios = [str(r) for r in radios]
            print(watch_times)
            wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_watch_times) + '\t' + '\t'.join(watch_times) + '\n')
            # wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_watch_times) + '\t' + '\t'.join(radios) + '\n')
    wfile.close()


if __name__ == "__main__":
    wt('/share/zhoupeng05/highlight/data_20210506/live_online_7889170503_sorted.txt', 20, '/share/zhoupeng05/highlight/data_20210506/live_online_7889170503_sorted_wt.txt')
