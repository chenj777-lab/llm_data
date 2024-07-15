# -*- coding: utf-8 -*-
import collections
import datetime
import sys
from collections import defaultdict

"""
拉取1万+粉丝的主播直播间实时在线人数，然后排序，用于统计长播率
1. 拉取数据
hive -e "select a.author_id, a.live_id, a.user_id, a.live_play_start_timestamp, a.live_play_end_timestamp, a.live_source_type, 
b.live_type, b.live_content_category, b.game_name, b.start_timestamp, b.fans_user_num from kscdm.dwd_ks_csm_play_live_di a 
join ksapp.ads_ks_live_aggr_1d b where a.p_date='20210421' and a.live_id = b.live_id and a.p_date = b.p_date and b.fans_user_num >= 10000" > live_online_person_1w+_20210421.txt
2. 过滤非当天开播的数据，然后对每个直播间按用户进入时间进行排序
输入字段：主播id，直播间id，用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …），直播类型（1:视频直播|2:语音直播|3:聊天室直播|-124:未知），
直播内容类型（shop:电商，game:游戏,other:其他（优先级 电商 > 游戏 > 其他）），游戏名称，直播间起始时间, 粉丝个数

因为进入日期是按天拉取的，只能拉取到当天的用户行为，因此对于非当天开播的直播间，长播率的变化跟当前开播的不太一样：
需要的话，可以根据日期，过滤掉非当天直播的直播间, 如果进入日期没有按天拆分，可以不用过滤非当天开播的直播间

输出字段：主播id，直播间id，直播间起始时间，粉丝个数，直播类型，直播内容类型，游戏名称，每个用户的信息（用户id，用户进入时间，用户退出时间，直播直接来源（音悦台台标|同城|热门|关注|直播订阅| …））, 并对每个用户根据进入时间从小到大排序

timestamp的时间格式是：2021-04-21 18:46:54.448, 去掉毫秒，变为2021-04-21 18:46:54
"""


def date_to_timestamp(date):
    # res = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").timestamp()
    res = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()
    return res


def sort_online(infile, in_date, outfile):
    '''
    过滤非当天开播和非当天结束的直播间，然后对每个直播间的用户按进入先后顺序进行排序
    :param infile:
    :param in_date: 日期，格式如: 2021-04-22, 或者为空，即不按日期过滤
    :param outfile:
    :return:
    '''
    # 读取直播间的在线人数
    num_texts = 0
    num_texts_error = 0
    num_live_id_in_date = 0  # 当天开播的直播间
    live_id_info = dict()  # 记录每个直播间id对应的信息
    live_id_user_info = defaultdict(lambda: defaultdict(list))  # 记录每个直播间id对应的用户信息
    with open(infile) as f:
        for text in f:
            num_texts += 1
            texts = text.strip().split('\t')
            if len(texts) != 12:
                num_texts_error += 1
                continue
            author_id = texts[0]
            live_id = texts[1]
            user_id = texts[2]
            user_start_timestamp = texts[3].split('.')[0]
            user_end_timestamp = texts[4].split('.')[0]
            user_source_type = texts[5]
            live_type = texts[6]
            live_content_category = texts[7]
            live_game_name = texts[8]
            live_start_timestamp = texts[9].split('.')[0]
            live_end_timestamp = texts[11].split('.')[0]
            author_fans_num = texts[10]
            if in_date:
                if in_date in live_start_timestamp and in_date in live_end_timestamp:  # 过滤非当天开播的直播间
                    num_live_id_in_date += 1
                    info = author_id + '\t' + live_id + '\t' + live_start_timestamp + '\t' + live_end_timestamp + '\t' + author_fans_num + '\t' + live_type + '\t' + live_content_category + '\t' + live_game_name
                    live_id_info[live_id] = info
                    tmp = user_id + ', ' + user_start_timestamp + ', ' + user_end_timestamp + ', ' + user_source_type
                    live_id_user_info[live_id][user_start_timestamp].append(tmp)
            else:
                info = author_id + '\t' + live_id + '\t' + live_start_timestamp + '\t' + live_end_timestamp + '\t' + author_fans_num + '\t' + live_type + '\t' + live_content_category + '\t' + live_game_name
                live_id_info[live_id] = info
                tmp = user_id + ', ' + user_start_timestamp + ', ' + user_end_timestamp + ', ' + user_source_type
                live_id_user_info[live_id][user_start_timestamp].append(tmp)
    if in_date:
        print("文件中样本个数是: {}, 不满足格式要求的个数是: {}, 直播间是当天开播的样本个数是: {}".format(num_texts, num_texts_error, num_live_id_in_date))
    else:
        print("文件中样本个数是: {}, 不满足格式要求的个数是: {}".format(num_texts, num_texts_error))
    wfile = open(outfile, 'w')
    for id, info in live_id_info.items():
        wfile.write(live_id_info[id] + '\t')
        user_info = live_id_user_info[id]
        # print(user_info)
        user_info = collections.OrderedDict(sorted(user_info.items(), key=lambda t: date_to_timestamp(t[0])))
        for u_id, u_info in user_info.items():
            tmp = '\t'.join(u_info)
            wfile.write(tmp + '\t')
        wfile.write('\n')
    wfile.close()


if __name__ == "__main__":
    sort_online(sys.argv[1], sys.argv[2], sys.argv[3])
    # sort_online('./data/live_online_person_1w+_20210421_end_timestamp_1m.txt', '2021-04-21',
    #             './data/live_online_person_1w+_20210421_end_timestamp_1m_sorted.txt', )

