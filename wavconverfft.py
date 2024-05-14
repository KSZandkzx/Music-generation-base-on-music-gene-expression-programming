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
    # rad1 = foldername+"zhuge/"+str(n).zfill(5)+"zhuge.wav"
    # rad2 = foldername+"fuge/"+str(n).zfill(5)+"fuge.wav"
    # sample_rate, X1 = wavfile.read(rad1)
    # sample_rate, X2 = wavfile.read(rad2)
    # X = np.concatenate((X1, X2))
    rad = foldername + str(n) + ".wav"
    sample_rate, X = wavfile.read(rad)
    if len(X.shape) == 2:
        X = X[:,0]
    # 用傅立叶变化处理1000以下的赫兹
    fft_features = abs(fft(X)[:1000])
    sad = foldername+str(n)+".fft"
    X = np.array(fft_features)
    X = X.reshape((1, X.shape[0], 1))
    # 把特征存到某个具体的路径下面去
    np.save(sad, X)

if __name__ == '__main__':
    folder_path = "./othermethod/"  # 替换为您要读取的文件夹路径
    for i in range(1):
        rad = folder_path + str(i) + "/"
        txt_files = [file for file in os.listdir(rad) if file.endswith(".wav")]
        num_txt_files = len(txt_files)
        for j in range(num_txt_files):
            create_fit(j, rad)
            print("第%d个文件夹的"%(i+1)+"%d个文件"%(j+1)+"完成")