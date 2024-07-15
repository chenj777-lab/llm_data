import lightgbm as lgb
import pandas as pd
import numpy as np
import pandas as pd                    # for data handling
import numpy as np                     # for random selections, mainly
import matplotlib.pyplot as plt        # for plotting
from kmlutils.kml_hive import Hive
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn import metrics
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns
from numpy import sqrt, argmax
from sklearn import metrics
from matplotlib import pyplot
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_recall_curve
from graphviz import Digraph
import pydotplus
import matplotlib.pylab as plt




if __name__ == '__main__':

    #!/usr/bin/env python
    # coding: utf-8
    
    # In[25]:
    
    
    
    
    
    
    
    # print('Load data...')
    # df_train = pd.read_csv('data/train.csv')
    # df_test = pd.read_csv('data/test.csv')
    # 数据准备 pandas dataframe
    hive = Hive(username='chenzhengzong', group_id=28)
    #train_df= hive.query('''select * from ks_mmu.user_action_and_music_info where p_date = "20230107" and p_hourmin= "2100"''', smart=True)
    train_df= hive.query('''select * from ks_mmu.user_action_and_music_info where p_date = "20230107" and p_hourmin= "2300"''', smart=False)
    
    
    # In[26]:
    
    
    train_df = train_df.compute()
    
    
    train_df = train_df.fillna(0)
    train_df.replace([np.inf], 10000000, inplace=True)
    train_df.replace([-np.inf], 0, inplace=True)
    # 选择的特征
    fea=list(train_df.columns[0:6])
    fea=fea+['tab']+['hetu_cluster_id']
    print(fea)
    
    train_df['music_id'] = preprocessing.LabelEncoder().fit_transform(train_df['music_id'].astype(str))
    
    #正负样本构造
    data_postive=train_df[train_df['is_like']==1]
    data_negative=train_df[train_df['is_like']==0]
    data_postive=data_postive.sample(n=2500000,random_state=1)
    data_negative=data_negative.sample(n=2500000,random_state=1)
    train_df=pd.concat([data_postive,data_negative])
    X = pd.DataFrame(train_df, columns = fea)
    y = pd.DataFrame(train_df, columns = ["is_like"])
    
    
    # X_train=X[0:1000000]
    # X_test=X[1000001:1200000]
    # y_train=y[0:1000000]
    # y_test=y[1000001:1200000]
    
    #print(y_test)
    
    #data split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    
    
    # In[27]:
    
    
    print(X_train)
    
    
    # In[28]:
    
    
    print(y_test.sum(axis=0))
    print(y_train.sum(axis=0))
    print(len(y_test))
    print(train_df['music_id'])
    
    
    # In[29]:
    
    
    pred_emb=False
    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
    
    params = {
        'task': 'train',
        'boosting_type': 'gbdt',
        'objective': 'binary',
        'metric': {'binary_logloss'},
        'num_leaves': 64,
        'num_trees': 100,
        'learning_rate': 0.01,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0,
        'max_depth':3  #overfitting
    }
    
    # number of leaves,will be used in feature transformation
    num_leaf = 64
    
    print('Start training...')
    # train
    gbm = lgb.train(params,
                    lgb_train,
                    num_boost_round=100,
                    valid_sets=lgb_train,early_stopping_rounds=50)
    
    print('Save model...')
    # save model to file
    gbm.save_model('model.txt')
    
    print('Start predicting...')
    # predict and get data on leaves, training data
    y_pred = gbm.predict(X_train, pred_leaf=pred_emb)
    
    print(np.array(y_pred).shape)
    print(y_pred[:10])
    
    
    # In[30]:
    
    
    #y_pred = [list(x).index(max(x)) for x in y_pred]
    print(accuracy_score(y_train, y_pred[:]>0.5))
    
    
    # In[31]:
    
    
    #plot roc curve
    
    
    fpr, tpr, thresholds = metrics.roc_curve(y_train, y_pred)
    #TPR = TP/ (TP + FN);FPR = FP / (FP+TN)
    #https://blog.csdn.net/u014264373/article/details/80487766
    #precision=tp/(tp+fp);recall=tp/(tp+fn)
    
    # calculate the g-mean for each threshold
    gmeans = sqrt(tpr * (1-fpr))
    # locate the index of the largest g-mean
    ix = argmax(gmeans)
    print('Best Threshold=%f, G-Mean=%.3f' % (thresholds[ix], gmeans[ix]))
    
    # plot the roc curve for the model
    pyplot.plot([0,1], [0,1], linestyle='--', label='No Skill')
    pyplot.plot(fpr, tpr, marker='.', label='Lgbm')
    pyplot.scatter(fpr[ix], tpr[ix], marker='o', color='black', label='Best')
    # axis labels
    pyplot.xlabel('False Positive Rate')
    pyplot.ylabel('True Positive Rate')
    pyplot.legend()
    # show the plot
    pyplot.show()
    
    
    # In[32]:
    
    
    #plot pr curve
    precision, recall, pr_threshold = precision_recall_curve(y_train, y_pred)
    
    pyplot.plot(precision, recall, marker='.', label='Lgbm')
    i=np.argwhere(pr_threshold>thresholds[ix])[0]
    print(i)
    print('best_precision:',precision[i],'best_recall:',recall[i])
    
    
    # In[33]:
    
    
    print(y_train)
    
    
    # In[34]:
    
    
    #eval accuracy
    y_pred_eval = gbm.predict(X_test, pred_leaf=pred_emb)
    #y_pred_eval = [list(x).index(max(x)) for x in y_pred_eval]
    print(accuracy_score(y_test, y_pred_eval[:]>thresholds[ix]))
    
    
    # In[35]:
    
    
    print(len(y_pred_eval))
    print(y_pred_eval.sum(axis=0))
    print(len(y_train))
    print(y_train.sum(axis=0))
    
    
    # In[36]:
    
    
    #LR
    if pred_emb:
        print('Writing transformed training data')
        transformed_training_matrix = np.zeros([len(y_pred), len(y_pred[0]) * num_leaf],
                                               dtype=np.int64)  # N * (num_tress * num_leafs)
        for i in range(0, len(y_pred)):
            temp = np.arange(len(y_pred[0])) * num_leaf + np.array(y_pred[i])
            transformed_training_matrix[i][temp] += 1 #转化为矩阵中对应偏移位置一
    
    
        y_pred = gbm.predict(X_test, pred_leaf=True) #True:产出预估值,False:emb
        print('Writing transformed testing data')
        transformed_testing_matrix = np.zeros([len(y_pred), len(y_pred[0]) * num_leaf], dtype=np.int64)
        for i in range(0, len(y_pred)):
            temp = np.arange(len(y_pred[0])) * num_leaf + np.array(y_pred[i])
            transformed_testing_matrix[i][temp] += 1
    
    
        lm = LogisticRegression(penalty='l2',C=0.05) # logestic model construction
        lm.fit(transformed_training_matrix,y_train)  # fitting the data
        y_pred_test = lm.predict_proba(transformed_testing_matrix)   # Give the probabilty on each label
    
        print(y_pred_test)
    
        # NE = (-1) / len(y_pred_test) * sum(((1+y_test)/2 * np.log(y_pred_test[:,1]) +  (1-y_test)/2 * np.log(1 - y_pred_test[:,1])))
        # print("Normalized Cross Entropy " + str(NE))
    
    
    # In[37]:
    
    
    if pred_emb:
        y_pred_label=lm.predict(transformed_testing_matrix)
        print(y_pred_label)
        print(accuracy_score(y_test, y_pred_label))
        y_pred_eval = gbm.predict(X_test,num_iteration=gbm.best_iteration_,pred_leaf=pred_emb)
        #y_pred_eval = [list(x).index(max(x)) for x in y_pred_eval]
        print(accuracy_score(y_test, y_pred_eval[:]>0.5))
    
    
    # In[38]:
    
    
    #feature importance 
    gbm.feature_importance(importance_type='split', iteration=None)
    
    lgb.create_tree_digraph(gbm, tree_index=0, show_info=['split_gain'], precision=3, orientation='horizontal')
    plt.figure(figsize=(12,6))
    lgb.plot_importance(gbm, max_num_features=30)
    plt.title("Feature_importances")
    plt.show()
                                                                                                                                            
                                                                                                                                            
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
