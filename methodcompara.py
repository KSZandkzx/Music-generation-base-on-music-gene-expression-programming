import numpy as np
from keras.models import load_model
import os

mymodel = load_model('my_modelfull1.h5')

for i in range(6):
    X = []
    savepath = "./othermethod/"+str(i)+"/"
    # 计算文件数
    txt_files = [file for file in os.listdir(savepath) if file.endswith(".fft.npy")]
    num_txt_files = len(txt_files)
    for j in range(num_txt_files):
        # 一个声音文件的0-1000的频率
        fft_features = np.load(savepath+str(j)+".fft.npy")
        X.append(fft_features)
    X = np.array(X)
    X = X.reshape((X.shape[0], X.shape[2], 1))
    # 预测
    numbers = mymodel.predict(X)
    # 保存数据
    with open(savepath+"fitness.txt","w") as file:
        num = 0
        for number in numbers:
            file.write(str(number[0]) + "\n")
            # file.write(str(number[0]) + "   " + str(num) + "\n")
            # num +=1
    print("第%d个文件完成"%(i+1))
a=1