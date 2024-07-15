import dask.dataframe as pd                    # for data handling
import numpy as np                     # for random selections, mainly
import matplotlib.pyplot as plt        # for plotting
from kmlutils.kml_hive import Hive
import faiss




if __name__ == '__main__':

    #!/usr/bin/env python
    # coding: utf-8
    
    # In[ ]:
    
    
    plt.rcParams['figure.figsize'] = 7,7   # graph dimensions
    plt.rcParams['font.size'] = 14         # graph font size
    # 数据准备
    hive = Hive(username='mmu', group_id=28)
    #hive = Hive(username='ad', group_id=99)
    train_df= hive.query('''select * from ks_mmu.item_info_emb where p_date="20220901" and size(emb_arr)!=1 ''', smart=False)
    
    
    # In[ ]:
    
    
    print(train_df)
    
    
    # In[ ]:
    
    
    train_df = train_df.compute()
    emb_arr=pd.DataFrame(train_df, columns = ['emb_arr'])
    item_id=pd.DataFrame(train_df, columns = ["item_id"])
    
    
    # In[ ]:
    
    
    item_id_np=item_id['item_id'].to_numpy
    #emb_arr_np=emb_arr['emb_arr'].to_numpy
    
    
    # In[ ]:
    
    
    emb_str=emb_arr['emb_arr'].str.rstrip(']').str.lstrip('[')
    emb = emb_str.str.split(',', expand=True)
    
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    emb=emb.astype('float32')
    flags=False
    for i,r in emb.iterrows():
        print(r[:])
        a=r[np.newaxis,:]
        if flags:
            emb_np=np.concatenate((emb_np,a),axis=0)
        else:
            emb_np=a
            flags=True
    
    
    # In[ ]:
    
    
    print(emb_np.shape)
    print(item_id_np)
    
    
    # In[ ]:
    
    
    # =========== kmeans =============
    # 聚类中心点
    ncentroids = 100
    # 训练轮数，默认25
    niter = 20
    verbose = True
    d = emb_np.shape[1] #向量维度
    nb = emb_np
    nq = 5000
    xb = nb
    print(xb.shape)
    
    
    # In[ ]:
    
    
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose)
    # gpu, 使用所有gpu
    # kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=True)
    # gpu, 使用三个gpu
    # kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=3)
    kmeans.train(xb)
    
    # 聚类后的聚类中心
    cluster_cents = kmeans.centroids
    # 聚类总的平方差
    cluster_wucha = kmeans.obj
    print('cluster_cents: ', len(cluster_cents), cluster_cents)
    print('cluster_wucha: ', len(cluster_wucha), cluster_wucha)
    
    
    
    
    # In[ ]:
    
    
    # D是距离值，I是索引
    D, I = kmeans.index.search(xb, 1)
    print('I', I[0:-1])
    
    
    # In[ ]:
    
    
    cluster=pd.DataFrame(I, columns = ['cluster'])
    print(cluster)
    d=pd.concat([item_id,cluster],axis=1)
    print(d)
    
    
    # In[ ]:
    
    
    name='ks_mmu.item_info_cluster'
    #hive.save_from_df(d,name,columns='auto',partition_cols=['20220901'],save_format='parquet',mode='ignore',sep=',',header=True,compression='default',schema='infer',is_check=True)
    hive.save_from_df(d,name,columns='auto',partition_cols=["p_date='20220901'"],save_format='parquet',mode='overwrite')
    
    
    # In[ ]:
    
    
    # # 如果需要查找xb中距离聚类中心最近的5个点，必须使用构建新的索引
    # index = faiss.IndexFlatL2(d)
    # index.add(xb)
    # D, I = index.search(kmeans.centroids, 5) #召回个数5；# 寻找相似向量， I表示相似用户ID矩阵， D表示距离矩阵
    # print('I', I[0:10])
    
    # # faiss使用write_index, read_index保存和加载索引
    # # faiss.write_index(index, 'faiss.index')
    # # new_index = faiss.read_index('faiss.index')
    
    # # =========== PCA =============
    # mt = np.random.rand(1000, 40).astype('float32')
    # mat = faiss.PCAMatrix(40, 10) #通过矩阵做降维，从40维到10维
    # print(mat.is_trained)
    # mat.train(mt)
    # print(mat.is_trained)
    # tr = mat.apply_py(mt)
    # print(type(tr))
    # # (1000, 10)
    # print(tr.shape)
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
