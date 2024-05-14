from pydub import AudioSegment
import os
for i in range(5):
    savepath = "./othermethod/"+str(i)+"/"
    txt_files = [file for file in os.listdir(savepath) if file.endswith(".mp3")]
    num_txt_files = len(txt_files)
    for j in range(num_txt_files):
        filename = str(j)
        # 读取MP3文件
        audio = AudioSegment.from_mp3(savepath+filename+".mp3")
        # 将MP3转换为WAV格式
        audio.export(savepath+filename+".wav", format="wav")