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
import os
import sys
import tensorflow as tf
import logging
import numpy as np
import argparse
from sklearn.metrics import *
import tensorflow.compat.v1 as tf




if __name__ == '__main__':

    #!/usr/bin/env python
    # coding: utf-8
    
    # In[1]:
    
    
    
    #get_ipython().run_line_magic('matplotlib', 'inline')
    
    
    
    # print('Load data...')
    # df_train = pd.read_csv('data/train.csv')
    # df_test = pd.read_csv('data/test.csv')
    # 数据准备
    hive = Hive(username='chenzhengzong', group_id=28)
    #train_df= hive.query('''select * from ks_mmu.user_action_and_music_info where p_date = "20230107" and p_hourmin= "2100"''', smart=True)
    train_df= hive.query('''select * from ks_mmu.user_action_and_music_info where p_date = "20230107" and p_hourmin= "2100"''', smart=False)
    
    train_df = train_df.compute()
    
    
    train_df = train_df.fillna(0)
    train_df.replace([np.inf], 10000000, inplace=True)
    train_df.replace([-np.inf], 0, inplace=True)
    # 选择的特征
    fea=list(train_df.columns[0:6])
    fea=fea+['tab']+['hetu_cluster_id']
    print(fea)
    
    train_df['music_id'] = preprocessing.LabelEncoder().fit_transform(train_df['music_id'].astype(str))
    data_postive=train_df[train_df['is_like']==1]
    data_negative=train_df[train_df['is_like']==0]
    data_postive=data_postive.sample(n=100000,random_state=1)
    data_negative=data_negative.sample(n=100000,random_state=1)
    train_df=pd.concat([data_postive,data_negative])
    X = pd.DataFrame(train_df, columns = fea)
    y = pd.DataFrame(train_df, columns = ["is_like"])
    
    
    # X_train=X[0:1000000]
    # X_test=X[1000001:1200000]
    # y_train=y[0:1000000]
    # y_test=y[1000001:1200000]
    
    #print(y_test)
    #data split
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    
    
    # In[46]:
    
    
    y = pd.DataFrame(train_df, columns = ["is_like"])
    
    y['un_like']=y['is_like'].apply(lambda x:1 if x==0 else 0)
    #y = pd.concat([y, pd.DataFrame(y,columns=['is_like']).apply(lambda x:1 if x==0 else 1,axis=1)], sort=False)
    print(y)
    
    
    # In[47]:
    
    
    x_train, x_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.3)
    
    
    # In[48]:
    
    
    print(tf.shape(x_train))
    
    
    # In[49]:
    
    
    print(x_train)
    
    
    # In[50]:
    
    
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)
    #from util import *
    tf.compat.v1.reset_default_graph()
    class FM(object):
        def __init__(self, num_classes, k, lr, batch_size, feature_length, reg_l1, reg_l2):
            self.num_classes = num_classes
            self.k = k
            self.lr = lr
            self.batch_size = batch_size
            self.p = feature_length
            self.reg_l1 = reg_l1
            self.reg_l2 = reg_l2
    
        def add_input(self):
            self.X = tf.placeholder('float32', [None,self.p])
            self.y = tf.placeholder('float32', [None,self.num_classes])
            self.keep_prob = tf.placeholder('float32')
    
        def inference(self):
            with tf.variable_scope('linear_layer',reuse=tf.AUTO_REUSE):
                w0 = tf.get_variable('w0', shape=[self.num_classes],
                                    initializer=tf.zeros_initializer())
                self.w = tf.get_variable('w', shape=[self.p, num_classes],
                                     initializer=tf.truncated_normal_initializer(mean=0,stddev=0.01))
                self.linear_terms = tf.add(tf.matmul(self.X, self.w), w0)
    
            with tf.variable_scope('interaction_layer',reuse=tf.AUTO_REUSE):
                self.v = tf.get_variable('v', shape=[self.p, self.k],
                                    initializer=tf.truncated_normal_initializer(mean=0, stddev=0.01))
                self.interaction_terms = tf.multiply(0.5,
                                                     tf.reduce_mean(
                                                         tf.subtract(
                                                             tf.pow(tf.matmul(self.X, self.v), 2),
                                                             tf.matmul(self.X, tf.pow(self.v, 2))),
                                                         1, keep_dims=True))
            self.y_out = tf.add(self.linear_terms, self.interaction_terms)
            if self.num_classes == 2:
                self.y_out_prob = tf.nn.sigmoid(self.y_out)
            elif self.num_classes > 2:
                self.y_out_prob = tf.nn.softmax(self.y_out)
        def add_loss(self):
            if self.num_classes == 2:
                cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.y, logits=self.y_out)
            elif self.num_classes > 2:
                cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=self.y, logits=self.y_out)
            mean_loss = tf.reduce_mean(cross_entropy)
            self.loss = mean_loss
            tf.summary.scalar('loss', self.loss)
    
        def add_accuracy(self):
            # accuracy
            self.correct_prediction = tf.equal(tf.cast(tf.argmax(self.y_out,1), tf.float32), tf.cast(tf.argmax(self.y,1), tf.float32))
            self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))
            # add summary to accuracy
            tf.summary.scalar('accuracy', self.accuracy)
    
        def train(self):
            self.global_step = tf.train.get_or_create_global_step()
            optimizer = tf.train.FtrlOptimizer(self.lr, l1_regularization_strength=self.reg_l1,
                                               l2_regularization_strength=self.reg_l2)
            extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(extra_update_ops):
                self.train_op = optimizer.minimize(self.loss, global_step=self.global_step)
    
        def build_graph(self):
            self.add_input()
            self.inference()
            self.add_loss()
            self.add_accuracy()
            self.train()
    
    def train_model(sess, model, epochs=100, print_every=50):
        """training model"""
        # Merge all the summaries and write them out to train_logs
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter('train_logs', sess.graph)
        
        # get number of batches
        num_batches = len(x_train) // batch_size + 1
    
        for e in range(epochs):
            num_samples = 0
            losses = []
            for ibatch in range(num_batches):
                # batch_size data
                batch_x, batch_y = next(batch_gen)
                batch_y = np.array(batch_y).astype(np.float32)
                actual_batch_size = len(batch_y)
                # create a feed dictionary for this batch
                #print("debug----")
                #print(batch_x.shape[0],batch_x.shape[1])
                #print(model.X.shape[0],model.X.shape[1])
                feed_dict = {model.X: batch_x,
                             model.y: batch_y,
                             model.keep_prob:1.0}
    
    
                loss, accuracy,  summary, global_step, _ = sess.run([model.loss, model.accuracy,
                                                                     merged,model.global_step,
                                                                     model.train_op], feed_dict=feed_dict)
                # aggregate performance stats
                losses.append(loss*actual_batch_size)
                num_samples += actual_batch_size
                # Record summaries and train.csv-set accuracy
                train_writer.add_summary(summary, global_step=global_step)
                # print training loss and accuracy
                if global_step % print_every == 0:
                    logging.info("Iteration {0}: with minibatch training loss = {1} and accuracy of {2}"
                                 .format(global_step, loss, accuracy))
                    saver.save(sess, "checkpoints/model", global_step=global_step)
            # print loss of one epoch
            total_loss = np.sum(losses)/num_samples
            print("Epoch {1}, Overall loss = {0:.3g}".format(total_loss, e+1))
    
    def test_model(sess, model, print_every = 50):
        """training model"""
        # get testing data, iterable
        all_ids = []
        all_clicks = []
        # get number of batches
        num_batches = len(y_test) // batch_size + 1
    
        for ibatch in range(num_batches):
            # batch_size data
            batch_x, batch_y = next(test_batch_gen) 
            actual_batch_size = len(batch_y)
            # create a feed dictionary for this15162 batch
            feed_dict = {model.X: batch_x,
                         model.keep_prob:1}
            # shape of [None,2]
            y_out_prob = sess.run([model.y_out_prob], feed_dict=feed_dict)
            y_out_prob = np.array(y_out_prob[0])
    
            batch_clicks = np.argmax(y_out_prob, axis=1)
    
            batch_y = np.argmax(batch_y, axis=1)
    
            #print(confusion_matrix(batch_y, batch_clicks))
            ibatch += 1
            if ibatch % print_every == 0:
                logging.info("Iteration {0} has finished".format(ibatch))
    
    
    def shuffle_list(data):
        num = data[0].shape[0]
        p = np.random.permutation(num)
        return [d[p] for d in data]
    
    def batch_generator(data, batch_size, shuffle=True):
        if shuffle:
            data = shuffle_list(data)
    
        batch_count = 0
        while True:
            if batch_count * batch_size + batch_size > len(data[0]):
                batch_count = 0
    
                if shuffle:
                    data = shuffle_list(data)
    
            start = batch_count * batch_size
            end = start + batch_size
            batch_count += 1
            yield [d[start:end] for d in data]
    
    def check_restore_parameters(sess, saver):
        """ Restore the previously trained parameters if there are any. """
        ckpt = tf.train.get_checkpoint_state("checkpoints")
        if ckpt and ckpt.model_checkpoint_path:
            logging.info("Loading parameters for the my Factorization Machine")
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            logging.info("Initializing fresh parameters for the my Factorization Machine")
    
    
    # In[51]:
    
    
    tf.disable_v2_behavior()
    
    # if __name__ == '__main__':
    #     '''launching TensorBoard: tensorboard --logdir=path/to/log-directory'''
    # get mode (train or test)
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', help='train or test', type=str)
    # args = parser.parse_args()
    mode = 'train'
    # length of representation
    #x_train, y_train, x_test, y_test = load_dataset()
    # initialize the model
    num_classes = 2
    lr = 0.01
    batch_size = 128
    k = 40
    reg_l1 = 2e-2
    reg_l2 = 0
    feature_length = x_train.shape[1]
    # initialize FM model
    batch_gen = batch_generator([x_train,y_train],batch_size,shuffle=False)
    test_batch_gen = batch_generator([x_test,y_test],batch_size,shuffle=False)
    model = FM(num_classes, k, lr, batch_size, feature_length, reg_l1, reg_l2)
    # build graph for model
    model.build_graph()
    
    saver = tf.train.Saver(max_to_keep=5)
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        check_restore_parameters(sess, saver)
        if mode == 'train':
            print('start training...')
            print(sess.run(model.v)) 
    # In[52]:
    
    
    #b=model.w
    
    
    # In[54]:
    
    
    #print(sess.run(b))
    
    
    # In[ ]:
    
    
    
    
