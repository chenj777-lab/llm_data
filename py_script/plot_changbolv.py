import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def plot_changbolv(infile,num):
    '''
    绘出每个直播间的长播率
    :param infile:输入文件
    :param num:统计前几个直播的图
    :return:
    '''

    with open(infile) as f:
        # 读取直播间的在线人数信息
        num_texts = 0
        num_texts_error = 0
        for text in f:
            num_texts += 1
            texts = text.strip().split('\t')
            print("live id:",texts[1],"changbolv:",texts[7])
            changbolv = texts[7].strip().split(',')
            changbolv.pop(len(changbolv)-1)
            plt.plot(np.array(changbolv).astype(np.float32))
            plt.grid(True)
            plt.axis('tight')
            plt.title(texts[1])
            plt.show()
            tmp = str(num_texts) + '_' + texts[1] +  '_photo.png'
            plt.savefig(tmp)
            plt.close()
            if num_texts >= num:
                break

if __name__ == "__main__":
    plot_changbolv('./data/live_online_person_1w+_20210421_1m_changbolv.txt',5)
    
