import random
import music21
from itertools import groupby
from midi2audio import FluidSynth
from scipy.io import wavfile
from scipy.fftpack import fft
import numpy as np
from keras.models import load_model
import subprocess
import os
import mymain
def create_fit(n,foldername):
    # zfill 返回指定长度的字符串，原字符串右对齐，前面填充0
    rad = "./trainset/" + foldername+"/zhuge/" + str(n).zfill(5) + 'zhuge' + ".wav"
    # sample_rate:采样率
    # 模电（连续的信号）变数电（数字的表达）
    # 采样率越高，如果单位时间采样点越多，信息损失的越少
    # X 就是音乐文件
    sample_rate, X = wavfile.read(rad)
    X = X[:,0]
    # 用傅立叶变化处理1000以下的赫兹
    fft_features = abs(fft(X)[:1000])
    sad = "./trainset/" + foldername+"/zhuge/" + str(n).zfill(5) + "zhuge.fft"
    X = np.array(fft_features)
    X = X.reshape((1, X.shape[0], 1))
    # 把特征存到某个具体的路径下面去
    np.save(sad, X)

if __name__ == '__main__':
    foldername = 'zhoujielun'
    for i in range(71,80):
        rad = "./trainset/" + foldername+"/zhuge/" + str(i).zfill(5) + "zhuge.txt"
        #使用已有对象完成转换
        nowScore = mymain.MyScore(1,16).readMyScore(rad)
        nowScore.saveMyScore('./trainset/'+foldername+'/zhuge/',str(i).zfill(5)+"zhuge")
        create_fit(i,foldername)
        print(i)