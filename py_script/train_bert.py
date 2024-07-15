# -*- coding: utf-8 -*-
import argparse
import os
import pickle
import shutil
import time
import torch
import torch.nn as nn
from utils.config import load_hyperparam
from utils.dataloader import process_file_chunk, train_batch
from utils.load_vocab import load_vocab
from utils.load_label import load_label
# from models.transformers import AdamW
from transformers.optimization import AdamW
from transformers import BertForSequenceClassification, BertConfig
"""
@file: train_bert.py
@author: zhoupeng
@time: 2021/4/22 下午4:02
-----------------------------------
Change Activity: 2021/4/22 下午4:02
"""

def save_checkpoint(state, model_path, epoch):
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    # save model dict
    torch.save(state, os.path.join(model_path, 'checkpoint_' + str(epoch+1) + '.pth.tar'))
    shutil.copyfile(os.path.join(model_path, 'checkpoint_' + str(epoch+1) + '.pth.tar'), os.path.join(model_path, 'model_best.pth.tar'))


def clip_gradient(model, clip_value):
    params = list(filter(lambda p: p.grad is not None, model.parameters()))
    for p in params:
        p.grad.data.clamp_(-clip_value, clip_value)


def train(model, optimizer, epoch, piece_num, x_train, y_train, max_length, batch_size, loss_fn):
    total_train_loss = 0
    total_train_acc = 0
    if torch.cuda.is_available():
        model.cuda()
    model.train()
    steps = 0
    time_start = time.time()
    total_loss = 0.
    total_acc = 0.
    for x, m, y in train_batch(x_train, y_train, max_length, batch_size, 1):
        target = torch.autograd.Variable(y).long()
        if torch.cuda.is_available():
            x = x.cuda()
            m = m.cuda()
            target = target.cuda()

        optimizer.zero_grad()
        # todo: 在使用bert、att可视化时才用mask
        output = model(x, attention_mask=m, labels=target)
        loss = output.loss
        prediction = output.logits
        # loss = loss_fn(prediction, target)  # , weight=torch.Tensor([1.0,1.0,1.0])
        prediction = torch.nn.Softmax(dim=1)(prediction)
        num_corrects = (torch.argmax(prediction, 1).view(target.size()).data == target.data).float().sum()
        acc = 100.0 * num_corrects/len(x)  # 也可以求平均
        steps += 1
        if torch.cuda.device_count() > 1:
            loss = torch.mean(loss)

        loss.backward()
        # todo: 修改此处，只有lstm、att才用
        # lstm: gradient explosion
        clip_gradient(model, 1e-1)

        optimizer.step()
        total_loss += loss.item()
        total_acc += acc
        if steps % 100 == 0:
            print("Piece {} of epoch: {}: \t\tIdx: {}, \t\tTrain Loss: {:.2f}, \t\t"
                  "Train Acc: {:.2f}, \t\t Took time: {:.2f} s".format(piece_num, epoch+1, steps, total_loss / 100, total_acc / 100, time.time()-time_start))
            total_loss = 0.
            total_acc = 0.

        total_train_loss += loss.item()
        total_train_acc += acc.item()

    return total_train_loss / steps, total_train_acc / steps


def evaluate(model, x_valid, y_valid, max_length, batch_size, loss_fn):
    total_valid_loss = 0
    total_valid_acc = 0
    if torch.cuda.is_available():
        model.cuda()
    model.eval()
    steps = 0
    time_start = time.time()
    total_loss = 0.  # total loss
    total_acc = 0.
    with torch.no_grad():
        for x, m, y in train_batch(x_valid, y_valid, max_length, batch_size, 1):
            target = torch.autograd.Variable(y).long()
            if torch.cuda.is_available():
                x = x.cuda()
                m = m.cuda()
                target = target.cuda()

            output = model(x, attention_mask=m, labels=target)
            loss = output.loss
            prediction = output.logits
            prediction = torch.nn.Softmax(dim=1)(prediction)
            num_corrects = (torch.argmax(prediction, 1).view(target.size()).data == target.data).float().sum()
            acc = 100.0 * num_corrects/len(x)
            steps += 1
            if torch.cuda.device_count() > 1:
                loss = torch.mean(loss)
            total_loss += loss.item()

            total_valid_loss += loss.item()
            total_valid_acc += acc.item()
            total_acc += acc
            if steps % 100 == 0:
                print("Valid steps: {}, \t\tValid Loss: {:.2f}, \t\t"
                      "Valid Acc: {:.2f}, \t\t Took time: {:.2f} s".format(steps, total_loss / 100, total_acc / 100, time.time()-time_start))
                total_loss = 0.
                total_acc = 0.

    return total_valid_loss / steps, total_valid_acc / steps


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='bert', help='Model name')
    parser.add_argument('--vocab_path', type=str, default='./data/vocab.txt', help='Path of vocab')
    parser.add_argument('--train_path', type=str, default='./examples/douban_book_review/dev_seg.tsv', help='Path of train dataset')
    parser.add_argument('--dev_path', type=str, default='./examples/douban_book_review/dev_seg.tsv', help='Path of development dataset')

    parser.add_argument('--pretrained_model_path', type=str, default='./examples/douban_book_review/model_pretrained/bert/', help='Path of embedding')
    parser.add_argument('--num_pieces', type=int, default=1, help='Number of pieces')
    parser.add_argument('--num_epoch', type=int, default=10, help='Number of epoch')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('--seq_length', type=int, default=512, help='Max length of sequence')
    parser.add_argument('--learning_rate', type=float, default=1e-5, help='Max length of sequence')

    parser.add_argument('--resume', type=int, default=0, help='reuse or not')
    parser.add_argument('--output_model_path', type=str, default='./examples/douban_book_review/model_pretrained', help='Path of the output model')
    # parser.add_argument('--output_model_path', type=str, default='./tmp/model_pretrained', help='Path of the output model')
    args = parser.parse_args()
    # args = load_hyperparam(args)
    output_model_path = args.output_model_path
    model_name = args.model_name
    seq_length = args.seq_length
    num_pieces = args.num_pieces
    batch_size = args.batch_size
    pretrained_model_path = args.pretrained_model_path


    # read vocab
    word2id, id2word = load_vocab(args.vocab_path)

    # train and valid filename
    print("read train and valid corpus")
    train_filename = args.train_path
    valid_filename = args.dev_path
    # read label
    label2id, id2label = load_label(train_filename)
    args.number_class = len(id2label)
    config = BertConfig.from_pretrained(pretrained_model_path, num_labels=args.number_class)
    model = BertForSequenceClassification.from_pretrained(pretrained_model_path, config=config)
    print("hyper-parameter in this model...")
    for key in vars(args).keys():
        print("{}: {}\n".format(key, vars(args)[key]))

    # number of parameters
    total_params = sum(p.numel() for p in model.parameters())
    print("total number of parameters in this model：{}".format(total_params))
    # number of parameters that will be updated
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("total number of parameters that will be updated in this model：{}".format(total_params))

    for var_name, p in zip(model.state_dict(), model.parameters()):
        print("name: {}, shape: {}, number: {}".format(var_name, p.shape, p.numel()))

    # optimizer
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, eps=1e-8)
    # loss function
    args.loss_fn = torch.nn.functional.cross_entropy
    # args.loss_fn = FocalLoss()

    print("saving parameters in this model...")
    model_dir = os.path.join(output_model_path, model_name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    # saving parameters
    output_params = os.path.join(model_dir, 'params.pkl')
    pickle.dump((word2id, label2id, args), open(output_params, 'wb'), -1)

    if args.resume:
        print("load pretrained model parameters...")
        if os.path.isfile(os.path.join(model_dir, 'pytorch_model.bin')):
            print("=> loading checkpoint '{}'".format(model_dir))
            checkpoint = torch.load(os.path.join(model_dir, 'pytorch_model.bin'))
            model.load_state_dict(checkpoint)
        else:
            print("=> no checkpoint found at '{}'".format(args.resume))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.device_count() > 1:
        print("{} GPUs are available. Let's use them.".format(torch.cuda.device_count()))
        model = nn.DataParallel(model)  # device_ids=[0,1]

    model = model.to(device)
    print("training start...")
    best_valid_acc = 0.
    best_valid_epoch = 0
    for epoch in range(args.num_epoch):
        # 分批读取训练样本进行训练
        time_start = time.time()
        piece_num = 0
        total_train_loss = 0.0
        total_train_acc = 0.0
        for x_train, y_train in process_file_chunk(train_filename, word2id, label2id, seq_length, 0, num_pieces):
            train_loss, train_acc = train(model, optimizer, epoch, piece_num, x_train, y_train, seq_length, batch_size, args.loss_fn)
            total_train_loss += train_loss
            total_train_acc += train_acc
            piece_num += 1
        print("Epoch: {}: \t\tTrain Loss: {:.2f}, \t\t Train Acc: {:.2f} %, \t\t Took Time: {:.2f}".format(epoch+1, total_train_loss / num_pieces, total_train_acc / num_pieces, time.time()-time_start))
        # 读取全部的验证进行验证
        total_valid_loss = 0.0
        total_valid_acc = 0.0
        for x_valid, y_valid in process_file_chunk(valid_filename, word2id, label2id, seq_length, 0, num_pieces):
            valid_loss, valid_acc = evaluate(model, x_valid, y_valid, seq_length, batch_size, args.loss_fn)
            total_valid_loss += valid_loss
            total_valid_acc += valid_acc
        valid_acc = total_valid_acc / num_pieces
        valid_loss = total_valid_loss / num_pieces
        print("Epoch: {}: \t\tValid Loss: {:.2f}, \t\t Valid Acc: {:.2f} %, \t\t Took Time: {:.2f}".format(epoch+1, valid_loss, valid_acc, time.time()-time_start))
        print("========================================================")
        # save model dict
        if hasattr(model, 'module'):
            torch.save(model.module.state_dict(), os.path.join(model_dir, 'checkpoint_' + str(epoch + 1) + '.bin'))
        else:
            torch.save(model.state_dict(), os.path.join(model_dir, 'checkpoint_' + str(epoch + 1) + '.bin'))

        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_valid_epoch = epoch + 1
            shutil.copyfile(os.path.join(model_dir, 'checkpoint_' + str(epoch + 1) + '.bin'),
                            os.path.join(model_dir, 'pytorch_model.bin'))
            print("Best valid acc : {:.2f} at epoch {}\n\n".format(best_valid_acc, best_valid_epoch))
        if best_valid_acc > valid_acc and epoch - best_valid_epoch >= 1:  # epoch没有加1
            print("No optimization for a long time, auto-stopping...")
            break


if __name__ == "__main__":
    run()