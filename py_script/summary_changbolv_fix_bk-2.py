# -*- coding: utf-8 -*-
import numpy as np
import datetime
import sys
import math
import profile
from time import time
import os
import re
from multiprocessing import Pool
"""
@file: summary_changbolv.py
@author: zhoupeng
@time: 2021/5/6 下午6:45
-----------------------------------
Change Activity: 2021/5/6 下午6:45
统计每个直播间的长播率
长播率计算公式是：某一段时间内停留大于某一阈值的次数/某一段时间内进入的总次数, 其中一段时间可能是15秒，停留时间阈值可能是15秒、30秒、60秒等

输入数据格式：主播id，直播间id，直播间起始时间，直播间起始时间，粉丝个数，直播类型，直播内容类型，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 其中每个用户根据进入时间从小到大排序, 同一时刻可能进入多个用户
输出数据格式: 主播id，直播间id，直播间起始时间，直播间起始时间，粉丝个数，直播类型，直播内容类型，游戏名称，每分钟或者每15秒的长播率



"""
kLiveInfoLen = 8 #直播信息长度
kUserInfoLen = 4 #单用户的信息长度
kMinOnlineUserNum = 1 #直播间最小观看人数阈值

def ymd_to_int(date):
    date = date.rstrip(os.linesep)
    rep = re.compile(r'(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})')
    m = rep.match(date)
    res = int(datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6))).timestamp())
#    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res


def filename_construct(file,name):
    str_list = file.split('.')
    tmp = ''
    length = len(str_list)
    if length == 1 or (length == 2 and str_list[0] == ''):
        return file + '_' + name

    str_begin_flag = True
    split_str = ''
    for i in range(length):
        if i == length - 1:
            tmp = tmp + '_' + name
        tmp = tmp + split_str + str_list[i] 

        if str_begin_flag is True:
            str_begin_flag = False
            split_str = '.' 
    return tmp


def summary_changbolv(infile, duration, threshold, outfile):
    '''
    统计每个直播间的长播率
    :param infile:输入文件
    :param duration:长播率统计窗口，单位（秒）
    :param threshold:长播率停留时间阈值，单位（秒）
    :param outfile:输出文件
    :return:
    '''
    if duration < threshold:
        return
    wfile = open(outfile, 'w')
    with open(infile) as f:
        # 读取直播间的在线人数信息
        num_texts = 0
        num_texts_error = 0
        for text in f:
            num_texts += 1
            texts = text.strip().split('\t')
            texts_len = len(texts)
            if texts_len <= kLiveInfoLen:
                num_texts_error += 1
                continue
            live_start_timestamp = texts[2]
            live_start_timestamp_int = ymd_to_int(live_start_timestamp)
            live_end_timestamp = texts[3]
            live_end_timestamp_int = ymd_to_int(live_end_timestamp)
            user_id_2_online_list = dict()
            user_id_2_online_duration_list = dict()
            live_time_len = math.ceil((live_end_timestamp_int - live_start_timestamp_int) / duration)
            max_list_len = live_time_len
            #遍历本直播间的所有用户
            #小于最低观看人数的直播则过滤
            if texts_len -  kLiveInfoLen < kMinOnlineUserNum:
                continue
            for user_index in range(kLiveInfoLen,texts_len):
                user_info_str = texts[user_index]
                user_info_arr = user_info_str.strip().split(',')
                if len(user_info_arr) < kUserInfoLen:
                    num_texts_error += 1
                    continue
                user_id = user_info_arr[0]
                user_start_timestamp_int = ymd_to_int(user_info_arr[1].strip())
                user_end_timestamp_int = ymd_to_int(user_info_arr[2].strip())
                calc_online_time = live_start_timestamp_int + duration
                user_online_time_list = [0]*live_time_len    #用户在线分时段列表
                user_online_duration_time_list = [0]*live_time_len  #用户停留分时段列表
                #错误观看时间修正
                if user_start_timestamp_int < live_start_timestamp_int:
                    user_start_timestamp_int = live_start_timestamp_int
                if user_end_timestamp_int > live_end_timestamp_int:
                    user_end_timestamp_int = live_end_timestamp_int
                if user_end_timestamp_int < user_start_timestamp_int:
                    continue
                
                #构建某一用户的停留信息数组
                #用户观看前的时段填充0
                current_index = 0
                while calc_online_time <= user_start_timestamp_int:
                    calc_online_time += duration
                    current_index +=1
                #该时段同时发生用户观看及退出
                if calc_online_time >= user_end_timestamp_int and (calc_online_time - duration < user_start_timestamp_int or 
                        (calc_online_time - duration == user_start_timestamp_int and user_start_timestamp_int == user_end_timestamp_int)):
                    #print(live_start_timestamp_int,',',live_end_timestamp_int,',',user_start_timestamp_int,',',user_end_timestamp_int)
                    user_online_time_list[current_index] += 1
                    if user_start_timestamp_int + threshold <= user_end_timestamp_int:    #停留时长满足阈值
                        user_online_duration_time_list[current_index] += 1
                #用户观看时段填充1
                while calc_online_time < user_end_timestamp_int:
                    user_online_time_list[current_index] += 1
                    if (calc_online_time + threshold <= user_end_timestamp_int or
                        (calc_online_time - duration <= user_start_timestamp_int and
                        user_start_timestamp_int + threshold <= calc_online_time) or
                        (user_end_timestamp_int - user_start_timestamp_int >= threshold)) :        #停留时长满足阈值
                        user_online_duration_time_list[current_index] += 1
                    calc_online_time += duration
                    current_index +=1
                #用户在该时段退出且起始观看时间小于本时段下限，则本时段用户在线并判断是否满足停留时长   
                if user_start_timestamp_int <= calc_online_time - duration and user_start_timestamp_int != user_end_timestamp_int:
                    user_online_time_list[current_index] += 1
                    if (calc_online_time - duration + threshold <= user_end_timestamp_int or 
                        user_end_timestamp_int - user_start_timestamp_int >= threshold): #停留时长满足阈值
                      user_online_duration_time_list[current_index] += 1
                
                #同一用户的时段列表merge
                if user_id in user_id_2_online_list and user_id in user_id_2_online_duration_list:
                   # user_online_time_list_merged = []
                  #  user_online_duration_time_list_merged = []
                    user_last_online_time_list = user_id_2_online_list[user_id]
                    max_len = max(len(user_last_online_time_list),len(user_online_time_list))
                    user_last_online_time_list = user_last_online_time_list + [0]*(max_len - len(user_last_online_time_list))
                    user_online_time_list = user_online_time_list + [0]*(max_len - len(user_online_time_list))
                    #for i,j in zip(user_last_online_time_list,user_online_time_list):
                    #    user_online_time_list_merged.append(i + j)
                    user_online_time_list_merged = np.array(user_last_online_time_list) + np.array(user_online_time_list)
                    user_online_time_list_merged = user_online_time_list_merged.tolist()
                    user_last_online_duration_time_list = user_id_2_online_duration_list[user_id]
                    max_len = max(len(user_last_online_duration_time_list),len(user_online_duration_time_list))
                    user_last_online_duration_time_list = user_last_online_duration_time_list + [0]*(max_len - len(user_last_online_duration_time_list))
                    user_online_duration_time_list = user_online_duration_time_list + [0]*(max_len - len(user_online_duration_time_list))
                   # for i,j in zip(user_last_online_duration_time_list,user_online_duration_time_list):
                   #     user_online_duration_time_list_merged.append(i + j)
                    user_online_duration_time_list_merged = np.array(user_last_online_duration_time_list) + np.array(user_online_duration_time_list)
                    user_online_duration_time_list_merged = user_online_duration_time_list_merged.tolist()
                    user_online_time_list = user_online_time_list_merged
                    user_online_duration_time_list = user_online_duration_time_list_merged

                user_id_2_online_list[user_id] = user_online_time_list #dict存储用户在线分时段列表
                user_id_2_online_duration_list[user_id] = user_online_duration_time_list #dict存储用户停留分时段列表
                #debug info
                if len(user_online_time_list) < len(user_online_duration_time_list):
                    print("user online len:%d, user duration len:%d"% (len(user_online_time_list),len(user_online_duration_time_list)))
                #print("live id:%s, live start time:%s, live end time:%s, user id:%s, user start time:%s, user end time:%s,"
                #        % (texts[1],texts[2],texts[3],user_info_arr[0],user_info_arr[1],user_info_arr[2]),"user online list:",user_online_time_list,",user duration list:",user_online_duration_time_list)

            #数组累加并计算长播率
            live_online_user_num_arr = np.zeros(max_list_len)
            live_online_duration_user_num_arr = np.zeros(max_list_len)
            for key,value in user_id_2_online_list.items():
                value = value + [0]*(max_list_len - len(value))
                live_online_user_num_arr = live_online_user_num_arr + np.array(value)
            for key,value in user_id_2_online_duration_list.items():
                value = value + [0]*(max_list_len - len(value))
                live_online_duration_user_num_arr = live_online_duration_user_num_arr + np.array(value)
            changbolv = np.divide(live_online_duration_user_num_arr,live_online_user_num_arr,out=np.zeros_like(live_online_duration_user_num_arr), where=((live_online_user_num_arr!=0)|(live_online_duration_user_num_arr!=0)))
            for author_info_index in range(kLiveInfoLen):
                wfile.write(texts[author_info_index] + '\t')
            tmp = ''
            str_begin_flag = True
            split_str = ''
            for val in changbolv.flatten():
                tmp = tmp + split_str + str(val) 
                if str_begin_flag is True:
                    str_begin_flag = False
                    split_str = ',' 
            wfile.write(tmp)
            wfile.write('\n')
        wfile.close()

def mean_changbolv(infile, duration, outfile):
    '''
    计算每个直播间的长播率均值
    :param infile:输入文件
    :param duration:长播率统计窗口，单位（秒）
    :param outfile:输出文件
    :return:
    '''
    wfile = open(outfile, 'w')
    with open(infile) as f:
        # 读取直播间信息
        num_texts = 0
        num_texts_error = 0
        for text in f:
            num_texts += 1
            texts = text.strip().split('\t')
            if len(texts) <= kLiveInfoLen:
                num_texts_error += 1
                continue
            live_start_timestamp = texts[2]
            live_start_timestamp_int = ymd_to_int(live_start_timestamp)
            live_end_timestamp = texts[3]
            live_end_timestamp_int = ymd_to_int(live_end_timestamp)
            live_time_len = math.ceil((live_end_timestamp_int - live_start_timestamp_int) / duration)
            changbolv_str = texts[kLiveInfoLen]
            changbolv_list = changbolv_str.strip().split(',')
            changbolv_sum = 0
            changbolv_mean = 0.0
            for val in changbolv_list:
                changbolv_sum += float(val)
            if live_time_len != 0:
                changbolv_mean = changbolv_sum / live_time_len
            for author_info_index in range(kLiveInfoLen):
                wfile.write(texts[author_info_index] + '\t')
            #print('live time len:',live_time_len,',changbolv sum:',changbolv_sum)
            wfile.write(str(changbolv_mean))
            wfile.write('\n')
    wfile.close()


if __name__ == "__main__":
    p=Pool(2)
    files = ['/home/chenzhengzong/.jupyter/data/test_case.txt','/home/chenzhengzong/.jupyter/data_20210506/live_online_person_1w+_20210421_end_timestamp_sorted.txt']
    for f in files:
        changbolv_filename = filename_construct(f,'changbolv')
        changbolv_mean_filename = filename_construct(changbolv_filename,'mean')
        p.apply_async(summary_changbolv,args=(f,15,15,changbolv_filename,))
    p.close()
    p.join()
    '''
    length = len(sys.argv)
    if length >= 4:
        if length <6:
            changbolv_filename = filename_construct(sys.argv[1],'changbolv')
            changbolv_mean_filename = filename_construct(changbolv_filename,'mean')
        else:
            changbolv_filename = sys.argv[4]
            changbolv_mean_filename = sys.argv[5]
        t = time()
        summary_changbolv(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),changbolv_filename)
    #    profile.run("summary_changbolv(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),changbolv_filename)")
        print(time()-t)
        #mean_changbolv(changbolv_filename,int(sys.argv[2]),changbolv_mean_filename)
   # summary_changbolv('./data/live_online_person_1w+_20210421_1m_sorted.txt', 60, 15, 
   #                   './data/live_online_person_1w+_20210421_1m_changbolv.txt')

   '''
