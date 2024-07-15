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
"""


def ymd_to_int(date):
    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res


def lvtr(infile, threshold, outfile):
    wfile = open(outfile, 'w')
    threshold = int(threshold)
    with open(infile) as f:
        for text in f:
            texts = text.strip().split('\t')
            live_start_timestamp = ymd_to_int(texts[2])
            live_end_timestamp = ymd_to_int(texts[3])
            live_user_online_timestamp_min = ymd_to_int(texts[8].strip().split(', ')[1])  # 观众进入直播间的最早时间
            live_user_online_timestamp_max = ymd_to_int(texts[-1].strip().split(', ')[1])  # 观众离开直播间的最早时间
            if live_user_online_timestamp_min < live_start_timestamp:
                live_user_online_timestamp_min = live_start_timestamp
            if live_user_online_timestamp_max > live_end_timestamp:
                live_user_online_timestamp_max = live_end_timestamp

            timestamps = []
            for user_info in texts[8:]:
                u_id, u_start_timestamp, u_end_timestamp, u_source = user_info.strip().split(', ')
                u_start_timestamp = ymd_to_int(u_start_timestamp)
                u_end_timestamp = ymd_to_int(u_end_timestamp)
                if u_start_timestamp < live_start_timestamp:
                    u_start_timestamp = live_start_timestamp
                if u_end_timestamp > live_end_timestamp:
                    u_end_timestamp = live_end_timestamp
                timestamps.append([u_start_timestamp, u_end_timestamp])
            print(timestamps)
            total_number_each_moment = {}
            sub_number_each_moment = {}
            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                print(i, live_start_timestamp, live_end_timestamp, threshold)
                j = i + threshold

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
                    # elif i < times[0] and times[0] == times[1]:
                    #     total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1


            radios = []
            for i in range(live_start_timestamp, live_end_timestamp, threshold):
                total = total_number_each_moment.get(i, 0)
                if i in sub_number_each_moment:
                    sub = sub_number_each_moment[i]
                else:
                    sub = 0
                print(i, sub, total)
                if sub:
                    radio = round(sub / total * 100, 2)
                else:
                    radio = 0.0
                radios.append(radio)
            tmp = len(range(live_start_timestamp, live_end_timestamp, threshold))
            mean_online_persons = round(np.array(list(total_number_each_moment.values())).sum() / tmp, 2)
            mean_lvtr = round(np.array(radios).sum() / tmp, 2)
            print(mean_online_persons, mean_lvtr)
            radios = [str(r) for r in radios]
            wfile.write('\t'.join(texts[:8]) + '\t' + str(mean_online_persons) + '\t' + str(mean_lvtr) + '\t' + '\t'.join(radios) + '\n')
    wfile.close()


def combine_files(infolder, outfile):
    time_start = time.time()
    with open(outfile, 'w') as wfile:
        infolder = infolder + '/'
        for filename in glob.glob(os.path.join(infolder + '*.txt')):
            if filename == outfile:
                continue
            print(filename)
        with open(filename, 'r') as readfile:
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
        if live_user_online_timestamp_min < live_start_timestamp:
            live_user_online_timestamp_min = live_start_timestamp
        if live_user_online_timestamp_max > live_end_timestamp:
            live_user_online_timestamp_max = live_end_timestamp

        timestamps = []
        for user_info in texts[8:]:
            u_id, u_start_timestamp, u_end_timestamp, u_source = user_info.strip().split(', ')
            u_start_timestamp = ymd_to_int(u_start_timestamp)
            u_end_timestamp = ymd_to_int(u_end_timestamp)
            if u_start_timestamp < live_start_timestamp:
                u_start_timestamp = live_start_timestamp
            if u_end_timestamp > live_end_timestamp:
                u_end_timestamp = live_end_timestamp
            timestamps.append([u_start_timestamp, u_end_timestamp])
        total_number_each_moment = {}
        sub_number_each_moment = {}
        for i in range(live_start_timestamp, live_end_timestamp, threshold):
            j = i + threshold
            for times in timestamps:
                if times[0] <= i < times[1]:  # 在此时刻或之前进入，并且结束时刻大于当前时刻
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                    if times[1] >= j:
                        sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
                elif times[0] == i == times[1]:
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                elif i < times[0] < j:  # 在此时刻和下一时刻之间进入
                    total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
                    if times[1] >= times[0] + threshold:
                        sub_number_each_moment[i] = sub_number_each_moment.get(i, 0) + 1
                # elif i < times[0] and times[0] == times[1]:
                #     total_number_each_moment[i] = total_number_each_moment.get(i, 0) + 1
        radios = []
        total_numbers = []
        for i in range(live_start_timestamp, live_end_timestamp, threshold):
            total = total_number_each_moment.get(i, 0)
            if i in sub_number_each_moment:
                sub = sub_number_each_moment[i]
            else:
                sub = 0
            if sub:
                radio = round(sub / total * 100, 2)
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
        mean_lvtr = round(np.array(radios).sum() / tmp, 2)
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
    # lvtr('./data/tmp.txt', 60, './data/tmp_out.txt')
    #lvtr('./data/test_case(1).txt', 15, './data/test_case_out.txt')
    lvtr('./data/test_case.txt', 15, './data/tmp_out.txt')
    # summary_lvtr('./data/tmp.txt', 1, 60, './data/tmp_.txt')
    # summary_lvtr(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
