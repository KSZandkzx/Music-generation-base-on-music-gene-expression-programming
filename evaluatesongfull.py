import numpy as np
from scipy.fftpack import fft
from scipy.io import wavfile
from keras.layers import Dense, Dropout,LSTM
from sklearn.model_selection import train_test_split
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.models import load_model
from keras.regularizers import l2
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
import os

if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    X = []
    for n in range(80):
        rad = "./trainset/zhoujielun/" + "full/" + str(n) + ".fft.npy"
        # 一个声音文件的0-1000的频率
        fft_features = np.load(rad)
        X.append(fft_features)
    folder_path = "./othermethod/"
    # for i in range(4, 6):
    #     rad = folder_path + str(i) + "/"
    #     txt_files = [file for file in os.listdir(rad) if file.endswith(".fft.npy")]
    #     num_txt_files = len(txt_files)
    #     for j in range(num_txt_files):
    #         fft_features = np.load(rad + str(j) + '.fft.npy')
    #         X.append(fft_features)
    X = np.array(X)
    # 计算相似值
    correlation_matrix = np.corrcoef(X.reshape(80, 1000))
    average_similarity = np.mean(correlation_matrix, axis=1)
    Y = average_similarity.reshape(-1, 1)
    X1 = []
    num_txt_files = 0
    folder_path = "./othermethod/"
    for i in range(4, 6):
        rad = folder_path + str(i) + "/"
        txt_files = [file for file in os.listdir(rad) if file.endswith(".fft.npy")]
        num_txt_files = len(txt_files)
        for j in range(num_txt_files):
            fft_features = np.load(rad + str(j) + '.fft.npy')
            X1.append(fft_features)
    X1 = np.array(X1)
    for j in range(len(X1)):
        arr1 = X1[j]
        arr1 = arr1.reshape(1, 1000)
        corr_coeffs = np.array([np.corrcoef(arr1.flatten(), arr.flatten())[0, 1] for arr in X.reshape(80, 1000)])
        Y = np.append(Y, abs(corr_coeffs.mean()))
    X = np.concatenate((X,X1))
    Y = Y.reshape(-1,1)

    X_train, X_test, y_train, y_test = train_test_split(
        X , Y, test_size=0.3, random_state=42)
    # # Reshape the input data to have the correct shape
    X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[2]))
    X_test = X_test.reshape((X_test.shape[0], 1,  X_test.shape[2]))
    # Define the model architecture
    timesteps = X_train.shape[1]
    input_dim = X_train.shape[2]

    # 构建神经网络模型
    model = Sequential()
    model.add(LSTM(128, input_shape=(timesteps, input_dim), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    optimizer = Adam(learning_rate=0.001)
    # 编译模型
    model.compile(loss='mean_squared_error', optimizer=optimizer)

    # model = load_model('my_modelfull.h5')
    # lr_scheduler = ReduceLROnPlateau(factor=0.1, patience=5, monitor='loss')
    # 早停函数
    early_stopping = EarlyStopping(monitor='val_loss', patience=20, mode='min', restore_best_weights=True)
    # Train the model on the training data
    model.fit(X_train, y_train, epochs=30, batch_size=64, callbacks=[early_stopping], validation_data=(X_test, y_test))
    # Save the model to a file
    model.save('my_modelfull.h5')
    mymodel = load_model('my_modelfull.h5')
    # 预测
    # mymodel = model
    Y_pre = mymodel.predict(X_train)
    # print(Y_pre)
    pausepoint = 1
