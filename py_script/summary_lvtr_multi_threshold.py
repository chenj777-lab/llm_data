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
"""
@file: summary_lvtr.py
@author: zhoupeng
@time: 2021/5/11 上午10:28
-----------------------------------
Change Activity: 2021/5/11 上午10:28
统计每个直播间的lvtr
输出从直播开始到直播结束时间范围内，每个时刻的lvtr
每15秒算一个时刻
输入数据格式：主播id, 直播间id, 直播间起始时间，直播间结束时间，粉丝个数，直播类型（1:视频直播|2:语音直播|3:聊天室直播|-124:未知），直播内容类型(shop:电商，game:游戏,other:其他（优先级 电商 > 游戏 > 其他）)，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 
1059272464      7973122543      2021-04-21 20:43:04     2021-04-21 20:52:37     50506   1       other   UNKNOWN 1902243240, 2021-04-21 20:43:25, 2021-04-21 20:43:28, LS_FOLLOW 1506573680, 2021-04-21 20:43:29, 2021-04-21 20:43:37, LS_FOLLOW

输出：主播id, 直播间id, 直播间起始时间，直播间结束时间，粉丝个数，直播类型（1:视频直播|2:语音直播|3:聊天室直播|-124:未知），直播内容类型(shop:电商，game:游戏,other:其他（优先级 电商 > 游戏 > 其他）)，游戏名称，平均在线观看人数，平均长播率，每个时刻的在线观看人数和长播率

如果文件较小，可使用lvtr函数, 只输出长播率
如果文件较大，可使用summary_lvtr跑动多进程 , 同时输出在线人数和长播率

对一个特定长度的片段，如threshold=20秒，统计20秒，30秒，60秒的长播率, 这里设置多个不同的取值，同时统计
"""


def ymd_to_int(date):
    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res


def lvtr(infile, threshold, durations, outfile):
    '''
    统计当前时刻不同数值的长播率
    :param infile: 每个直播间每个用户的进出时间
    :param threshold: 20秒
    :param durations: 20秒的倍数，比如'1,2,3'
    :param outfile:
    :return:
    '''
    wfile = open(outfile, 'w')
    threshold = int(threshold)
    durations = [int(d) for d in durations.strip().split(',')]

    with open(infile) as f:
        for text in f:
            texts = text.strip().split('\t')
            live_start_timestamp = ymd_to_int(texts[2])
            live_end_timestamp = ymd_to_int(texts[3])
            live_user_online_timestamp_min = ymd_to_int(texts[8].strip().split(', ')[1])  # 观众进入直播间的最早时间
            live_user_online_timestamp_max = live_user_online_timestamp_min  # 假设用户最晚离开时间等于最早进入时间，后面再详细判断、赋值
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
            total_number_each_moment = {}
            sub_number_each_moment = {}
            sub_number_each_moment_1 = {}
            sub_number_each_moment_2 = {}

            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                # print(i, live_start_timestamp, live_end_timestamp, threshold)
                j = i + threshold
                if j < live_user_online_timestamp_min:
                    continue
                if i > live_user_online_timestamp_max+threshold:
                    # print("此刻没有在线用户。。。")
                    break
                for times in timestamps:
                    print(i,times)
                    if times[0] < i < times[1]:  # 在此时刻或之前进入，并且结束时刻大于当前时刻
                        total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                        if times[1] >= j:
                            sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
                        if times[1] >= i + threshold * durations[1]:
                            sub_number_each_moment_1[i] = sub_number_each_moment_1.get(i, 0) + 1
                        if times[1] >= i + threshold * durations[2]:
                            sub_number_each_moment_2[i] = sub_number_each_moment_2.get(i, 0) + 1
                    elif times[0] == i == times[1]:
                        total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                    elif i <= times[0] < j:  # 在此时刻和下一时刻之间进入
                        total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                        if times[1] >= times[0] + threshold:
                            sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
                        if times[1] >= i + threshold * durations[1]:
                            sub_number_each_moment_1[i] = sub_number_each_moment_1.get(i, 0) + 1
                        if times[1] >= i + threshold * durations[2]:
                            sub_number_each_moment_2[i] = sub_number_each_moment_2.get(i, 0) + 1
            radios = []
            radios_1 = []
            radios_2 = []
            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                # durations 0
                total = total_number_each_moment.get(i, 0)
                sub = sub_number_each_moment.get(i, 0)
                if sub:
                    radio = round(sub / total, 4)
                else:
                    radio = 0.0
                radios.append(radio)

                # durations 1
                sub_1 = sub_number_each_moment_1.get(i, 0)
                if sub_1:
                    radio_1 = round(sub_1 / total, 4)
                else:
                    radio_1 = 0.0
                radios_1.append(radio_1)

                # durations 2
                sub_2 = sub_number_each_moment_2.get(i, 0)
                if sub_2:
                    radio_2 = round(sub_2 / total, 4)
                else:
                    radio_2 = 0.0
                radios_2.append(radio_2)

            tmp = len(range(live_start_timestamp, live_end_timestamp, threshold))
            mean_online_persons = round(np.array(list(total_number_each_moment.values())).sum() / tmp, 2)
            mean_lvtr = round(np.array(radios).sum() / tmp, 4)
            mean_lvtr_1 = round(np.array(radios_1).sum() / tmp, 4)
            mean_lvtr_2 = round(np.array(radios_2).sum() / tmp, 4)
            # print(mean_online_persons, mean_lvtr)
            radios = [str(r) for r in radios]
            radios_1 = [str(r) for r in radios_1]
            radios_2 = [str(r) for r in radios_2]
            wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_lvtr_1) + '\t' +
                        str(mean_lvtr_2) + '\t' + str(mean_lvtr) + '\t\t' + '\t'.join(radios) + '\t\t' +
                        '\t'.join(radios_1) + '\t\t' + '\t'.join(radios_2) + '\n')
    wfile.close()


def combine_files(infolder, outfile):
    time_start = time.time()
    with open(outfile, 'w') as wfile:
        filenames = os.listdir(infolder)
        for filename in filenames:
            if filename.endswith('.txt'):
                infile = os.path.join(infolder, filename)
                with open(infile, 'r') as readfile:
                    shutil.copyfileobj(readfile, wfile)
    print("combining file took time: {} s".format(time.time()-time_start))


def _lvtr(thread_num, num_thread, chunk_size, infile, threshold, outfile, queue):
    time_start = time.time()
    fin = open(infile, 'r', errors='ignore')
    est_start = chunk_size * thread_num
    est_end = chunk_size * (thread_num + 1)
    fin.seek(est_start, 0)
    if thread_num != 0:
        fin.readline()
    n_lines = 0
    wfile = open(outfile, 'w')
    n_write = 0
    while True:
        text = fin.readline()
        if not text:
            break
        n_lines += 1
        texts = text.strip().split('\t')
        if len(texts) <= 9:
            continue
        live_start_timestamp = ymd_to_int(texts[2])
        live_end_timestamp = ymd_to_int(texts[3])
        live_user_online_timestamp_min = ymd_to_int(texts[8].strip().split(', ')[1])  # 观众进入直播间的最早时间
        live_user_online_timestamp_max = ymd_to_int(texts[-1].strip().split(', ')[1])  # 观众离开直播间的最早时间
        if live_user_online_timestamp_max < live_start_timestamp or live_user_online_timestamp_min > live_end_timestamp:  # 如果最大的离开时间，小于直播开始时间，则丢弃该样本
            continue
        if live_user_online_timestamp_min < live_start_timestamp:
            live_user_online_timestamp_min = live_start_timestamp
        if live_user_online_timestamp_max > live_end_timestamp:
            live_user_online_timestamp_max = live_end_timestamp

        timestamps = []
        for user_info in texts[8:]:
            u_id, u_start_timestamp, u_end_timestamp, u_source = user_info.strip().split(', ')
            u_start_timestamp = ymd_to_int(u_start_timestamp)
            u_end_timestamp = ymd_to_int(u_end_timestamp)
            if u_end_timestamp < live_start_timestamp:  # 如果用户离开时间小于直播开播时间，则丢弃
                continue
            if u_start_timestamp < live_start_timestamp:  # 如果用户进入时间小于直播开播时间，则替换为直播开播时间
                u_start_timestamp = live_start_timestamp
            if u_end_timestamp > live_end_timestamp:  # 如果用户离开时间大于直播开播时间，则替换为直播结束时间
                u_end_timestamp = live_end_timestamp
            timestamps.append([u_start_timestamp, u_end_timestamp])
        total_number_each_moment = {}
        sub_number_each_moment = {}
        for i in range(live_start_timestamp, live_end_timestamp, threshold):
            j = i + threshold
            if i < live_user_online_timestamp_min:
                continue
            if i > live_user_online_timestamp_max:
                break
            for times in timestamps:
                if times[0] < i < times[1]:  # 在此时刻或之前进入，并且结束时刻大于当前时刻
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                    if times[1] >= j:
                        sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
                elif times[0] == i == times[1]:
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                elif i <= times[0] < j:  # 在此时刻和下一时刻之间进入
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                    if times[1] >= times[0] + threshold:
                        sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
        radios = []
        total_numbers = []
        for i in range(live_start_timestamp, live_end_timestamp, threshold):
            total = total_number_each_moment.get(i, 0)
            if i in sub_number_each_moment:
                sub = sub_number_each_moment[i]
            else:
                sub = 0
            if sub:
                radio = round(sub / total, 4)
            else:
                radio = 0.0
            radios.append(radio)
            total_numbers.append(total)
        # 合并每一时刻的在线观看人数和长播率
        assert len(radios) == len(total_numbers)
        number_radio = []
        for n, r in zip(total_numbers, radios):
            n_r = str(n) + ', ' + str(r)
            number_radio.append(n_r)
        # 统计一整场直播的平均在线观看人数和长播率
        tmp = len(range(live_start_timestamp, live_end_timestamp, threshold))
        mean_online_persons = round(np.array(list(total_number_each_moment.values())).sum() / tmp, 2)
        mean_lvtr = round(np.array(radios).sum() / tmp, 4)
        # 写到输出文件中
        # radios = [str(r) for r in radios]
        # wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_lvtr) + '\t' + '\t'.join(radios) + '\n')
        wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_lvtr) + '\t' + '\t'.join(number_radio) + '\n')
        n_write += 1
        if n_lines % 1000 == 0:
            print("Processing {} sentences took time：{} s".format(n_lines, time.time() - time_start))
        chunk_end = fin.tell()
        if thread_num != int(num_thread) - 1 and chunk_end > est_end:
            break
    wfile.close()
    queue.put(n_write)
    fin.close()


def summary_lvtr(infile, num_thread, threshold, outfile):
    time_start = time.time()
    num_thread = int(num_thread)
    threshold = int(threshold)
    stat_info = os.stat(infile)
    file_size = stat_info.st_size  # 文件大小，以字节为单位
    chunk_size = int(file_size / int(num_thread))
    processes = []
    queue = mp.Manager().Queue()
    output_dir = os.path.split(outfile)[0]
    target_dir = os.path.join(output_dir, 'tmp_lvtr')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for i in range(num_thread):
        out_sub_filename = os.path.join(target_dir, str(i) + '.txt')
        p = mp.Process(target=_lvtr, args=(i, num_thread, chunk_size, infile, threshold, out_sub_filename, queue))
        processes.append(p)
        p.start()
    line_counts = []
    for j in range(len(processes)):
        line_count = queue.get(True)
        line_counts.append(line_count)

    for p in processes:
        p.join()
    print("number of sentences wrote to file is ：{}".format(np.array(line_counts).sum()))
    print("number of sentences wrote to file is ：{}".format(np.array(line_counts).sum()))
    print("number of sentences wrote to file is ：{}".format(np.array(line_counts).sum()))
    print("summary lvtr took time: {} s".format(time.time() - time_start))
    combine_files(infolder=target_dir, outfile=outfile)
    # 删除文件夹
    shutil.rmtree(target_dir)
    print("program took time: {} s".format(time.time() - time_start))


if __name__ == "__main__":
    lvtr('./data/test_case.txt', 15, '1, 2, 3', './data/test_case_out_bk.txt')
    # summary_lvtr('./data/test_case_sorted.txt', 1, 15, './data/tmp_.txt')
    # summary_lvtr(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # combine_files('./for_labeling/data', './tmp_com.txt')
