# -*- coding: utf-8 -*-
import numpy as np
import datetime
"""
@file: summary_changbolv.py
@author: zhoupeng
@time: 2021/5/6 下午6:45
-----------------------------------
Change Activity: 2021/5/6 下午6:45
统计每个直播间的长播率
长播率计算公式是：某一段时间内停留大于某一阈值的次数/某一段时间内进入的总次数, 其中一段时间可能是15秒，停留时间阈值可能是15秒、30秒、60秒等

输入数据格式：主播id，直播间id，直播间起始时间，粉丝个数，直播类型，直播内容类型，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 其中每个用户根据进入时间从小到大排序, 同一时刻可能进入多个用户
输出数据格式: 主播id，直播间id，直播间起始时间，粉丝个数，直播类型，直播内容类型，游戏名称，每分钟或者每15秒的长播率



"""
def ymd_to_int(date):
    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res


def summary_changbolv(infile, duration, threshold, outfile):
    '''
    统计每个直播间的长播率
    :param infile:输入文件
    :param duration:长播率统计窗口，单位（秒）
    :param threshold:长播率停留时间阈值，单位（秒）
    :param outfile:输出文件
    :return:
    '''
    live_info_len = 7 #直播信息长度
    user_info_len = 4 #单用户的信息长度
    min_online_user_num = 1 #直播间最小观看人数阈值
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
            if len(texts) <= live_info_len:
                num_texts_error += 1
                continue
            live_start_timestamp = texts[2]
            live_start_timestamp_int = ymd_to_int(live_start_timestamp)
            user_id_2_online_list = dict()
            user_id_2_online_duration_list = dict()
            max_list_len = 0
            #遍历本直播间的所有用户
            #小于最低观看人数的直播则过滤
            if len(texts) -  live_info_len < min_online_user_num:
                continue
            for user_index in range(live_info_len,len(texts)):
                user_info_str = texts[user_index]
                user_info_arr = user_info_str.strip().split(',')
                if len(user_info_arr) < user_info_len:
                    num_texts_error += 1
                    continue
                user_id = user_info_arr[0]
                user_start_timestamp_int = ymd_to_int(user_info_arr[1].strip())
                user_end_timestamp_int = ymd_to_int(user_info_arr[2].strip())
                calc_online_time = live_start_timestamp_int + duration
                user_online_time_list = []    #用户在线分时段列表
                user_online_duration_time_list = []  #用户停留分时段列表
                #错误观看时间修正
                if user_end_timestamp_int < live_start_timestamp_int:
                    continue
                if user_start_timestamp_int < live_start_timestamp_int:
                    user_start_timestamp_int = live_start_timestamp_int
                
                #构建某一用户的停留信息数组
                #用户观看前的时段填充0
                while calc_online_time <= user_start_timestamp_int:
                    user_online_time_list.append(0)
                    user_online_duration_time_list.append(0)
                    calc_online_time += duration
                    print(1)
                #该时段同时发生用户观看及退出
                if calc_online_time >= user_end_timestamp_int and calc_online_time - duration < user_start_timestamp_int:
                    #if calc_online_time != user_end_timestamp_int: 
                    user_online_time_list.append(1)
                    print(2)
                    if user_start_timestamp_int + threshold < user_end_timestamp_int:    #停留时长满足阈值
                        user_online_duration_time_list.append(1)
                #用户观看时段填充1
                while calc_online_time < user_end_timestamp_int:
                    user_online_time_list.append(1)
                    if (calc_online_time + threshold < user_end_timestamp_int or
                        (calc_online_time - duration <= user_start_timestamp_int and
                        user_start_timestamp_int + threshold < calc_online_time) or
                        (user_end_timestamp_int - user_start_timestamp_int >= threshold)) :        #停留时长满足阈值
                        user_online_duration_time_list.append(1)
                    calc_online_time += duration
                    print(3)
                #用户在该时段退出且起始观看时间小于本时段下限，则本时段用户在线并判断是否满足停留时长   
                if user_start_timestamp_int <= calc_online_time - duration and user_start_timestamp_int != user_end_timestamp_int:
                    user_online_time_list.append(1)
                    if (calc_online_time - duration + threshold <= user_end_timestamp_int or 
                        user_end_timestamp_int - user_start_timestamp_int >= threshold): #停留时长满足阈值
                      user_online_duration_time_list.append(1)
                    print(4)
                
                #同一用户的时段列表merge
                if user_id in user_id_2_online_list and user_id in user_id_2_online_duration_list:
                    user_online_time_list_merged = []
                    user_online_duration_time_list_merged = []
                    user_last_online_time_list = user_id_2_online_list[user_id]
                    max_len = max(len(user_last_online_time_list),len(user_online_time_list))
                    user_last_online_time_list = user_last_online_time_list + [0]*(max_len - len(user_last_online_time_list))
                    user_online_time_list = user_online_time_list + [0]*(max_len - len(user_online_time_list))
                    for i,j in zip(user_last_online_time_list,user_online_time_list):
                        user_online_time_list_merged.append(i + j)
                    user_last_online_duration_time_list = user_id_2_online_duration_list[user_id]
                    max_len = max(len(user_last_online_duration_time_list),len(user_online_duration_time_list))
                    user_last_online_duration_time_list = user_last_online_duration_time_list + [0]*(max_len - len(user_last_online_duration_time_list))
                    user_online_duration_time_list = user_online_duration_time_list + [0]*(max_len - len(user_online_duration_time_list))
                    for i,j in zip(user_last_online_duration_time_list,user_online_duration_time_list):
                        user_online_duration_time_list_merged.append(i + j)
                    user_online_time_list = user_online_time_list_merged
                    user_online_duration_time_list = user_online_duration_time_list_merged

                user_id_2_online_list[user_id] = user_online_time_list #dict存储用户在线分时段列表
                user_id_2_online_duration_list[user_id] = user_online_duration_time_list #dict存储用户停留分时段列表
                max_list_len = max(max_list_len,len(user_online_time_list),len(user_online_duration_time_list))  #保留本直播间各用户的时间段最大长度
                #debug info
                if len(user_online_time_list) < len(user_online_duration_time_list):
                    print("user online len:%d, user duration len:%d"% (len(user_online_time_list),len(user_online_duration_time_list)))
                print("live id:%s, live start time:%s, user id:%s, user start time:%s, user end time:%s,"
                        % (texts[1],texts[2],user_info_arr[0],user_info_arr[1],user_info_arr[2]),"user online list:",user_online_time_list,",user duration list:",user_online_duration_time_list)

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
            for author_info_index in range(live_info_len):
                wfile.write(texts[author_info_index] + '\t')
            tmp = ''
            for val in changbolv.flatten():
                tmp = tmp + str(val) + ','
            wfile.write(tmp)
            wfile.write('\n')
        wfile.close()

if __name__ == "__main__":
    summary_changbolv('./data/live_online_person_1w+_20210421_1m_sorted.txt', 60, 15, 
                      './data/live_online_person_1w+_20210421_1m_changbolv.txt')
