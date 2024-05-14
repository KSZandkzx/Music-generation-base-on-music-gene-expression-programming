import random
import math
import music21
from itertools import groupby
from midi2audio import FluidSynth
from scipy.io import wavfile
from scipy.fftpack import fft
import numpy as np
from keras.models import load_model
import subprocess
import time
import os

# 节类
class MySection:
    def __init__(self, totalbeat = 16):
        """
        一拍的单位
        一节的拍数
        音符列表
        """
        self.totalbeat = totalbeat
        self.noteslist = []
        self.countlist = []

    # 初始化音符
    def initRand(self):
        for i in range(self.totalbeat):
            while True:
                temp = random.randint(1, 49)
                if (temp != 10) and (temp != 20) and (temp != 30) and (temp != 40):
                    break
            self.noteslist.append(temp)

# 乐谱类
class MyScore:
    def __init__(self, totalsection=0, totalbeat=16):
        """
        总节数
        一节的拍数
        一节的拍数
        节列表
        适应度
        """
        self.totalsection = totalsection
        self.totalbeat = totalbeat
        self.sectionlist = []
        self.fitness = 0
        for i in range(totalsection):
            section = MySection(totalbeat)
            self.sectionlist.append(section)

    # 乐谱随机初始化
    def initSec(self):
        for i in range(len(self.sectionlist)):
            self.sectionlist[i].initRand()
            self.getMyScorenote(i)
        return self

    # 乐谱拼接
    def spliceexisscore(self, outerscore):
        for i in range(len(outerscore.sectionlist)):
            newsection = MySection()
            newsection.noteslist = outerscore.sectionlist[i].noteslist[:]
            newsection.countlist = outerscore.sectionlist[i].countlist[:]
            self.sectionlist.append(newsection)
            self.totalsection += 1

        return self

    # 乐谱打印
    def printMyScore(self):
        for i in range(self.totalsection):
            print("第%d节" % (i + 1))
            section = self.sectionlist[i]
            print(section.noteslist)
            print()

    # 读取乐曲
    def readMyScore(self, name):
        with open(name, 'r') as file:
            content = file.read()
            numbers = [int(num) for num in content.split()]
            self.totalsection = math.ceil(len(numbers) / self.totalbeat)
            componet = MyScore(self.totalsection, self.totalbeat).initSec()
            for i in range(self.totalsection):
                componet.sectionlist[i].noteslist = numbers[i * 16:i * 16 + 16]
                componet.getMyScorenote(i)

        return componet

    # 乐曲切割
    def cutMyScoretail(self, num):
        for i in range(num):
            self.sectionlist[-1].noteslist.pop()

    def cutMyScorehead(self, num):
        for i in range(num):
            self.sectionlist[0].noteslist.pop()

    # 搜索音的时长
    def serchnotetime(self, sectionindex=1, randindex=0, num=0):
        # 传入乐谱节索引，音符位置，音的个数
        # 输出音符位置,及时长
        # 更新索引表
        self.getMyScorenote(sectionindex)
        notenumlist = self.sectionlist[sectionindex].countlist
        noteindex = 0
        # 转化为另一个表的索引
        for noteindex in range(1, len(notenumlist) + 1):
            if sum([v for k, v in notenumlist[0:noteindex]]) > randindex:
                noteindex -= 1
                break
        returnflag = 1
        # 检测传入索引后的音的个数是否足够
        while noteindex + num <= len(notenumlist):
            for i in range(num):
                if notenumlist[i + noteindex][0] == 0:
                    # 索引移到0后面
                    noteindex = i + noteindex + 1
                    returnflag = 0
                    break
            if returnflag:
                return [sum([v for k, v in notenumlist[0:noteindex]]), [
                    v for k, v in notenumlist[noteindex:noteindex + num]]]
            returnflag = 1
        # 没有索引成功
        return [-1]

    # 搜索音的位置
    def serchnoteindex(self, sectionindex=1, randindex=0, num=[0]):
        # 传入乐谱节索引，音符索引，音的时长
        # 输出音符索引
        # 更新索引表
        self.getMyScorenote(sectionindex)
        notenumlist = self.sectionlist[sectionindex].countlist
        noteindex = 0
        # 转化为另一个表的索引
        for noteindex in range(1, len(notenumlist) + 1):
            if sum([v for k, v in notenumlist[0:noteindex]]) > randindex:
                noteindex -= 1
                break
        returnflag = 1
        while noteindex + len(num) <= len(notenumlist):
            if num == [v for k, v in notenumlist[noteindex:noteindex + len(num)]]:
                for i in range(len(num)):
                    if notenumlist[i + noteindex][0] == 0:
                        # 索引移到0后面
                        noteindex = i + noteindex + 1
                        returnflag = 0
                        break
                if returnflag:
                    return sum([v for k, v in notenumlist[0:noteindex]])
                returnflag = 1
            else:
                noteindex += 1
        return -1

    # 获取乐谱的音及持续时间
    def getMyScorenote(self, sectionlistindex):
        # 这里的方法使用了itertools.groupby函数来将列表中相邻且相同的元素分组。
        # 然后，我们使用列表推导式来获取每个元素及其出现的次数，从而得到最终的结果。
        self.sectionlist[sectionlistindex].countlist = [[k, len(list(v))] for k, v in groupby(
            self.sectionlist[sectionlistindex].noteslist)]

    # 保存乐谱
    def saveMyScore(self, savepath='./temp/', filename='bestScore',singer=0):
        # 写入txt文件
        with open(savepath+filename + '.txt', "w") as txtfile:
            for i in range(self.totalsection):
                for j in range(len(self.sectionlist[i].noteslist)):
                    number = self.sectionlist[i].noteslist[j]
                    txtfile.write(str(number))
                    if number == 0:
                        txtfile.write("   ")
                    else:
                        txtfile.write(" ")
                txtfile.write("\n")
        # 创建一个新的Score对象
        mytempo = music21.tempo.MetronomeMark(number=60)
        score = music21.stream.Score()
        score.append(mytempo)
        # 创建一个乐器对象
        # instrument = music21.instrument.Guitar()
        # 创建小节
        for i in range(self.totalsection):
            mysection = self.sectionlist[i]
            notetimelist = self.sectionlist[i].countlist
            # 创建一个小节对象
            m = music21.stream.Measure()
            for j in range(len(notetimelist)):
                notenum = mysection.noteslist[sum([v for k, v in notetimelist[:j]])]
                letter = ''
                # 创建音符
                if notenum == 0:
                    mynote = []
                    zeronum = notetimelist[j][1]
                    while 1:
                        if zeronum == 1:
                            restduration = '16th'
                            zeronote = music21.note.Rest()
                            zeronote.duration = music21.duration.Duration(restduration)
                            mynote.append(zeronote)
                            break
                        elif zeronum == 2:
                            restduration = 'eighth'
                            zeronote = music21.note.Rest()
                            zeronote.duration = music21.duration.Duration(restduration)
                            mynote.append(zeronote)
                            break
                        elif zeronum <= 4:
                            if zeronum == 4:
                                restduration = 'quarter'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                                break
                            else:
                                zeronum -= 2
                                restduration = 'eighth'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                        elif zeronum <= 8:
                            if zeronum == 8:
                                restduration = 'half'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                                break
                            else:
                                zeronum -= 4
                                restduration = 'quarter'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                        elif zeronum <= 16:
                            if zeronum == 16:
                                restduration = 'whole'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                                break
                            else:
                                zeronum -= 8
                                restduration = 'half'
                                zeronote = music21.note.Rest()
                                zeronote.duration = music21.duration.Duration(restduration)
                                mynote.append(zeronote)
                else:
                    mynote = music21.note.Note()
                    if singer:
                        letternum = 2
                    else:
                        letternum = 4
                    if notenum > 30:
                        if notenum > 40:
                            letternum += 2
                        else:
                            letternum += 1
                    elif notenum < 20:
                        if notenum < 10:
                            letternum -= 2
                        else:
                            letternum -= 1
                    notenumstr = str(notenum)
                    if notenumstr[-1] == '1':
                        letter = 'C'
                    elif notenumstr[-1] == '2':
                        letter = 'D'
                    elif notenumstr[-1] == '3':
                        letter = 'E'
                    elif notenumstr[-1] == '4':
                        letter = 'F'
                    elif notenumstr[-1] == '5':
                        letter = 'G'
                    elif notenumstr[-1] == '6':
                        letter = 'A'
                    elif notenumstr[-1] == '7':
                        letter = 'B'
                    mynote.pitch = music21.pitch.Pitch(letter + str(letternum))  # 将音高对象设置为音符对象的音高属性
                    mynote.duration.quarterLength = 0.25 * notetimelist[j][1]  # 音符的时值设置
                    # # 将乐器对象分配给音符对象
                    # mynote.offset = 0  # 设置音符的偏移量
                    # mynote.partName = 'Guitar'  # Set the part name
                    # mynote.instrument = instrument

                # 在小节中添加音符
                m.append(mynote)
            # 将小节添加到Score对象中
            score.append(m)
        # 导出为MIDI文件
        score.write('midi', fp=savepath + filename + '.mid')  # 将乐谱对象导出为MIDI文件
        # 将mid文件转化为wav文件
        # 定义要运行的命令
        command = ['FluidSynth', '-F', savepath + filename + '.wav', './sf2/YDPGrandPiano20160804.sf2',
                   savepath + filename + '.mid']
        # 运行命令并等待其完成
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            output, error = process.communicate()
            if process.returncode != 0:
                print(f'An error occurred: {error}')

    # 评估函数
    def evaluatesong(self, mymodle):
        # 转化歌曲
        self.saveMyScore()
        # 转化频谱
        sample_rate, X = wavfile.read('./temp/bestScore.wav')
        # 取单通道
        X = X[:, 0]
        # 用傅立叶变化处理1000以下的赫兹
        fft_features = abs(fft(X)[:1000])
        X = np.array(fft_features)
        X = X.reshape((1, X.shape[0], 1))
        # 预测符合概率
        predic = mymodle.predict([X])
        return predic[0][0]


class Environment:
    def __init__(self):
        """
        population          种群：用于保存染色体
        bestChromosome      最佳染色体：保存当代最佳染色体
        bestfitness         最佳染色体的适应度：保证当代最佳染色体的适应度
        """
        self.population = []
        self.bestChromosome = []
        self.component = []
        self.componentindex = [[i + 1] for i in range(50)]
        self.bestfitness = 0
        self.populationSize = 0
        self.totalsection = 0
        self.totalbeat = 0
        self.model = None
        self.zhugeScore = [MyScore() for i in range(6)]
        self.fugeScore = [MyScore() for i in range(6)]
        self.fullScore = [MyScore() for i in range(6)]
        self.style = 0
        self.createmode = 0

    # 读取其他歌曲
    def readcomponent(self):
        # 读取器件库
        import os
        folder_path = "./trainset/zhoujielun/pianduan"  # 替换为您要读取的文件夹路径
        txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]
        num_txt_files = len(txt_files)
        for n in range(num_txt_files):
            rad = "./trainset/zhoujielun/pianduan/" + str(n).zfill(5) + "pianduan.txt"
            with open(rad, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    numbers = [int(num) for num in line.split()]
                    if len(numbers) > 0:
                        self.component.append(numbers)
                        self.componentindex[len(numbers) - 1].append(len(self.component) - 1)
        a = 1

    # 乐谱填充
    def initfill(self, NowScore):
        countlist = []
        noteindex = 0
        for i in range(NowScore.totalsection):
            for j in range(len(NowScore.sectionlist[i].noteslist)):
                if NowScore.sectionlist[i].noteslist[j] != 0:
                    NowScore.sectionlist[i].noteslist[j] = 48
            NowScore.getMyScorenote(i)
            countlist = countlist + NowScore.sectionlist[i].countlist
        # 将0和待填充部分分开
        countlist = [[key, sum(item[1] for item in group)] for key, group in groupby(countlist, lambda x: x[0])]
        for count in countlist:
            if count[0] != 0:
                # 循环填充
                while count[1] != 0:
                    # 设置最大填充数
                    if count[1] <= 50:
                        num = random.randint(1, count[1])
                    else:
                        num = random.randint(1, 50)
                    for numindex in range(len(self.componentindex)):
                        if num == self.componentindex[numindex][0]:
                            # 对应长度的索引为空
                            if len(self.componentindex[numindex]) == 1:
                                break
                            else:
                                randnumindex = random.randint(1, len(self.componentindex[numindex]) - 1)
                                for i in range(num):
                                    NowScore.sectionlist[noteindex // self.totalbeat].noteslist[
                                        noteindex % self.totalbeat] = \
                                        self.component[self.componentindex[numindex][randnumindex]][i]
                                    noteindex += 1
                                count[1] -= num
                                break
            else:
                noteindex += count[1]
        # 更新时长表
        for i in range(NowScore.totalsection):
            NowScore.getMyScorenote(i)
        return NowScore

    # 初始化
    def zhugeinit(self, populationSize = 100, totalbeat = 16, style=1):
        # 读取歌曲库
        self.readcomponent()
        self.style = style - 1
        self.createmode = 0
        self.populationSize = populationSize
        self.totalbeat = totalbeat
        self.population = [self.initfill(MyScore(self.totalsection, self.totalbeat).readMyScore(
            './trainset/zhoujielun/zhuge/' + str(self.style).zfill(5) + 'zhuge.txt')) for i
            in range(self.populationSize)]
        self.totalsection = self.population[0].totalsection
        self.model = load_model('my_modelzhuge.h5')

    def fugeinit(self, populationSize = 100, totalbeat = 16, style=1):
        # 读取歌曲库
        self.readcomponent()
        self.style = style - 1
        self.createmode = 1
        self.populationSize = populationSize
        self.totalbeat = totalbeat
        self.population = [self.initfill(MyScore(self.totalsection, self.totalbeat).readMyScore(
            './trainset/zhoujielun/fuge/' + str(self.style).zfill(5) + 'fuge.txt')) for i
            in range(self.populationSize)]
        self.totalsection = self.population[0].totalsection
        self.model = load_model('my_modelfuge.h5')

    # 淘汰80%
    def select(self):
        # 并行排序
        selected = []
        fitnesslist = []
        for i in range(self.populationSize):
            fitnesslist.append(self.population[i].fitness)
        fitnesslistindex = [i for i in range(self.populationSize)]

        # 将第一组数据和第二组数据根据第一组数据的值进行组合和排序
        combined_data = sorted(zip(fitnesslist, fitnesslistindex), reverse=True)

        # 计算出对应于前20%数据的索引
        twenty_percent_index = int(len(combined_data) * 0.2)

        # 从排序后的数据中提取出前80%的第一组数据和对应的第二组数据
        sorted_data1, sorted_data2 = zip(*combined_data[:twenty_percent_index])
        for i in sorted_data2:
            selected.append(self.population[i])
        self.population = []
        for i in range(len(selected)):
            self.population.append(selected[i])

    # 个体复制,解决数组中两个类是同一个的问题
    def replicate(self, oldMyScore):
        newMyScore = MyScore(self.totalsection, self.totalbeat).initSec()
        for j in range(newMyScore.totalsection):
            newMyScore.sectionlist[j].noteslist = oldMyScore.sectionlist[j].noteslist[:]
            newMyScore.sectionlist[j].totalbeat = oldMyScore.sectionlist[j].totalbeat
            newMyScore.sectionlist[j].countlist = oldMyScore.sectionlist[j].countlist[:]

        return newMyScore

    # 乐谱修改箱
    def modifykit(self, NowtBestMyScore, headsectionindex=0, tailsectionindex=16):
        # 输入音谱索引，音谱的节索引
        # 设置完成标志，方法
        change = [0] * 6
        completeflag = 0
        changepercentage = [0.1, 0.025, 0.2, 0.1, 0.525, 0.05]  # 设置方法概率
        accumulator = 0
        roulette = []  # 设置轮盘
        # 制作赌盘
        for i in range(len(change)):
            roulette.append(accumulator + changepercentage[i])
            accumulator += changepercentage[i]
        # 遍历节
        for sectionindex in range(headsectionindex, tailsectionindex):
            # 有概率不修改
            if random.random() > 0.5:
                # for sectionindex in range(tailsectionindex,1):
                midifynoteslist = NowtBestMyScore.sectionlist[sectionindex].noteslist
                for serchchangenum in range(7):
                    # 随机选择节内位置
                    randindex = random.randint(0, self.totalbeat - 2)
                    # 随机选择方法
                    methdindexnum = random.random()
                    methdindex = 0
                    for methdindex in range(len(change)):
                        if methdindexnum <= roulette[methdindex]:
                            break
                    change[methdindex] = 1
                    if change[0]:
                        # 两个音的节拍重组 例2233变为2223
                        completeflag = 0
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, 2)
                        if serchindexresult[0] != -1:
                            completeflag = 1
                            # 储存原来的两个音
                            firstnote = midifynoteslist[serchindexresult[0]]
                            secondnote = midifynoteslist[serchindexresult[0] + serchindexresult[1][0]]
                            # 节奏打乱
                            firstlen = random.randint(1, sum(serchindexresult[1]) - 1)
                            for i in range(sum(serchindexresult[1])):
                                # 前长度为firstlen的为第一个音
                                if i < firstlen:
                                    midifynoteslist[i + serchindexresult[0]] = firstnote
                                else:
                                    midifynoteslist[i + serchindexresult[0]] = secondnote
                            checkflag = 1
                            temp = midifynoteslist[serchindexresult[0]]
                            for i in range(sum(serchindexresult[1])):
                                if temp != midifynoteslist[i + serchindexresult[0]]:
                                    checkflag = 0
                                    break
                            if checkflag:
                                a = 1
                            # 更新时长表
                            NowtBestMyScore.getMyScorenote(sectionindex)
                            # print(0)
                    elif change[1]:
                        # 两个音的节拍复制 例2233变为22223333
                        completeflag = 0
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, 2)
                        if serchindexresult[0] != -1:
                            # 将两个音的节奏复制
                            firstlen = serchindexresult[1][0] * 2
                            secondlen = serchindexresult[1][1] * 2
                            # 不能超出范围
                            if (serchindexresult[0] + firstlen + secondlen) <= self.totalbeat:
                                completeflag = 1
                                # 不能覆盖0
                                for i in range(firstlen + secondlen - sum(serchindexresult[1])):
                                    if midifynoteslist[i + serchindexresult[0] + sum(serchindexresult[1])] == 0:
                                        completeflag = 0
                                        break
                                if completeflag:
                                    # 储存两个音
                                    firstnote = midifynoteslist[serchindexresult[0]]
                                    secondnote = midifynoteslist[serchindexresult[0] + serchindexresult[1][0]]
                                    # 前面部分覆盖第一个音，后面第二个音
                                    for i in range(firstlen + secondlen):
                                        if i < firstlen:
                                            midifynoteslist[i + serchindexresult[0]] = firstnote
                                        else:
                                            midifynoteslist[i + serchindexresult[0]] = secondnote
                                    # 更新时长表
                                    NowtBestMyScore.getMyScorenote(sectionindex)
                                    # print(1)
                    elif change[2]:
                        # 多个音以中间某个音为中心移位 例224433变为334422，以44为中心
                        completeflag = 0
                        # 随机翻转音的个数
                        notenum = random.randint(3, 8)
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, notenum)
                        if serchindexresult[0] != -1:
                            completeflag = 1
                            # 随机中间位置
                            middlerand = random.randint(1, len(serchindexresult[1]) - 2)
                            # 复制原音符数组
                            notelisttemp = midifynoteslist[:]
                            # 获取后面音的长度
                            tailcount = sum(serchindexresult[1][middlerand + 1:])
                            for i in range(sum(serchindexresult[1])):
                                # 将后面部分前移
                                if i < tailcount:
                                    midifynoteslist[i + serchindexresult[0]] = notelisttemp[
                                        i + sum(serchindexresult[1][:middlerand + 1]) + serchindexresult[0]]
                                # 中间部分保留
                                elif i < tailcount + serchindexresult[1][middlerand]:
                                    midifynoteslist[i + serchindexresult[0]] = notelisttemp[i + sum(
                                        serchindexresult[1][:middlerand]) - tailcount + serchindexresult[0]]
                                # 前面部分后移
                                else:
                                    midifynoteslist[i + serchindexresult[0]] = notelisttemp[
                                        i - tailcount - serchindexresult[1][middlerand] + serchindexresult[0]]
                            # 更新时长表
                            NowtBestMyScore.getMyScorenote(sectionindex)
                            # print(2)
                    elif change[3]:
                        # 音节前后倒位 例 223344变为442233
                        completeflag = 0
                        # 随机翻转音的个数
                        notenum = random.randint(2, 8)
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, notenum)
                        if serchindexresult[0] != -1:
                            completeflag = 1
                            # 随机中间位置
                            middlerand = random.randint(0, len(serchindexresult[1]) - 2)
                            notelisttemp = midifynoteslist[:]
                            # 获取后面音的长度
                            tailcount = sum(serchindexresult[1][middlerand + 1:])
                            for i in range(sum(serchindexresult[1])):
                                # 后面音前移
                                if i < tailcount:
                                    midifynoteslist[i + serchindexresult[0]] = notelisttemp[i + sum(
                                        serchindexresult[1][:middlerand + 1]) + serchindexresult[0]]
                                # 前面音后移
                                else:
                                    midifynoteslist[i + serchindexresult[0]] = notelisttemp[
                                        i - tailcount + serchindexresult[0]]
                            # 更新时长表
                            NowtBestMyScore.getMyScorenote(sectionindex)
                            # print(3)
                    elif change[4]:
                        # 乐谱替换
                        completeflag = 0
                        # 随机音节的个数
                        notenum = 2
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, notenum)
                        # 符合片段库
                        matchresult = []
                        if serchindexresult[0] != -1:
                            completeflag = 1
                            subnotenum = sum(serchindexresult[1])
                            subnoteindex = serchindexresult[0]
                            while subnotenum != 0:
                                if subnotenum <= 6:
                                    num = random.randint(1, subnotenum)
                                else:
                                    num = random.randint(1, 6)
                                for numindex in range(len(self.componentindex)):
                                    if num == self.componentindex[numindex][0]:
                                        # 如果对应长度的库为空则重新计算
                                        if len(self.componentindex[numindex]) == 1:
                                            break
                                        else:
                                            randnumindex = random.randint(1, len(self.componentindex[numindex]) - 1)
                                            for i in range(num):
                                                midifynoteslist[i + subnoteindex] = \
                                                    self.component[self.componentindex[numindex][randnumindex]][i]
                                            subnoteindex += num
                                            subnotenum -= num
                                            break
                            # 更新时长表
                            NowtBestMyScore.getMyScorenote(sectionindex)
                            # print(4)
                    elif change[5]:
                        completeflag = 0
                        # 音节升或降，1，2，3
                        # print('进行方式6')
                        # 随机翻转音的个数
                        notenum = random.randint(2, 3)
                        # 查询是否存在相关片段
                        serchindexresult = NowtBestMyScore.serchnotetime(sectionindex, randindex, notenum)
                        if serchindexresult[0] != -1:
                            completeflag = 1
                            # 随机上升音阶
                            tone = random.randint(1, 3)
                            # 防止超出范围
                            for i in range(sum(serchindexresult[1])):
                                if midifynoteslist[i + serchindexresult[0]] - tone <= 0:
                                    completeflag = 0
                                    break
                                elif midifynoteslist[i + serchindexresult[0]] + tone >= 48:
                                    completeflag = 0
                                    break
                            if completeflag:
                                # 随机升或降
                                if random.randint(0, 1) == 0:
                                    for i in range(sum(serchindexresult[1])):
                                        # 当超出7时需要上升级数
                                        strmidifynoteslist = str(midifynoteslist[i + serchindexresult[0]])
                                        if int(strmidifynoteslist[-1]) + tone >= 8:
                                            midifynoteslist[i + serchindexresult[0]] = (int(
                                                strmidifynoteslist[0]) + 1) * 10 + \
                                                                                       int(strmidifynoteslist[
                                                                                               -1]) + tone - 7
                                        else:
                                            midifynoteslist[i + serchindexresult[0]] += tone
                                else:
                                    for i in range(sum(serchindexresult[1])):
                                        # 当低于1时需要下降级数
                                        strmidifynoteslist = str(midifynoteslist[i + serchindexresult[0]])
                                        if int(strmidifynoteslist[-1]) - tone <= 0:
                                            midifynoteslist[i + serchindexresult[0]] = int(
                                                int(strmidifynoteslist[0]) - 1) * 10 \
                                                                                       + 7 + int(
                                                strmidifynoteslist[-1]) - tone
                                        else:
                                            midifynoteslist[i + serchindexresult[0]] -= tone
                                # 更新时长表
                                NowtBestMyScore.getMyScorenote(sectionindex)
                                # print(5)
                    change = [0] * 6
                    if completeflag:
                        completeflag = 0
                        break
        return NowtBestMyScore

    # 复制部分修改
    def copymodify(self, NowtBestMyScore, p=0.4):
        # 末尾一定修改，中间以一定概率修改
        sectionnum = self.population[-1].totalsection*3//10
        NowtBestMyScore = self.modifykit(NowtBestMyScore, headsectionindex=NowtBestMyScore.totalsection - sectionnum,
                       tailsectionindex=NowtBestMyScore.totalsection)
        if random.random() < p:
            NowtBestMyScore = self.modifykit(NowtBestMyScore, headsectionindex=NowtBestMyScore.totalsection//2 - sectionnum//2,
                           tailsectionindex=NowtBestMyScore.totalsection//2 + sectionnum - sectionnum//2)

        return NowtBestMyScore

    # 音节延长修改
    def longmodify(self,NowtBestMyScore):
        for sectionindex in range(NowtBestMyScore.totalsection-1):
            if random.random() < 0.3:
                completeflag = 0
                midifynotecountslistreverse =NowtBestMyScore.sectionlist[sectionindex].countlist[:]
                midifynotecountslistreverse.reverse()
                # 不足两个四分音的延长
                if midifynotecountslistreverse[-1][1] < 8:
                    for i in range(len(midifynotecountslistreverse)):
                        # 寻找长度大于8的尾部
                        if sum([v for k,v in midifynotecountslistreverse[0:i+1]]) >= 8:
                            completeflag = 1
                            midifynoteslist = NowtBestMyScore.sectionlist[sectionindex].noteslist
                            # 判断是否存在0
                            for j in range(sum([v for k, v in midifynotecountslistreverse[1:i + 1]])):
                                if midifynoteslist[NowtBestMyScore.totalbeat -
                                                sum([v for k, v in midifynotecountslistreverse[1:i + 1]]) + j] == 0:

                                    break
                            if completeflag == 0:
                                break
                            for j in range(sum([v for k,v in midifynotecountslistreverse[1:i+1]])):
                                midifynoteslist[NowtBestMyScore.totalbeat -
                                                sum([v for k,v in midifynotecountslistreverse[1:i+1]]) + j] = \
                                midifynoteslist[NowtBestMyScore.totalbeat -
                                                sum([v for k, v in midifynotecountslistreverse[0:i + 1]])]
                            # 更新时长表
                            NowtBestMyScore.getMyScorenote(sectionindex)
                            completeflag = 0
                            break
        # 结尾必定发生
        midifynoteslist = NowtBestMyScore.sectionlist[NowtBestMyScore.totalsection - 1].noteslist
        for i in range(NowtBestMyScore.totalbeat):
            if midifynoteslist[i] != 0:
                for j in range(NowtBestMyScore.totalbeat):
                    midifynoteslist[j] = midifynoteslist[i]
                break
        # 更新时长表
        NowtBestMyScore.getMyScorenote(NowtBestMyScore.totalsection - 1)

        return NowtBestMyScore

    # 迭代进化
    def run(self, generationCount=3):
        childrennum = 80
        savenum = 6
        generation = 0
        for i in range(len(self.population)):
            i_MyScore = self.population[i]
            # 进行适应度计算
            # start_time = time.time()
            i_MyScore.fitness = i_MyScore.evaluatesong(self.model)
            # end_time = time.time()
            # runtime = end_time - start_time
            # print("Program runtime:", runtime, "seconds")
        # 进行筛选20%
        self.select()
        while True:
            # 进行代数打印
            print("generation: ", generation)
            generation += 1
            notevolvenum = 0
            for i in range(len(self.population)):
                # 使用变异产生新个体
                childrenScore = [self.modifykit(self.replicate(self.population[i]), headsectionindex=0,
                                          tailsectionindex=self.totalsection) for j in range(childrennum)]
                for j in range(len(childrenScore)):
                    # 进行适应度计算
                    childrenScore[j].fitness = childrenScore[j].evaluatesong(self.model)
                nowBestScoreindex = -1
                nowBestScorefitness = -1
                for j in range(len(childrenScore)):
                    if nowBestScorefitness < childrenScore[j].fitness:
                        nowBestScorefitness = childrenScore[j].fitness
                        nowBestScoreindex = j
                if nowBestScorefitness >= self.population[i].fitness:
                    self.population[i] = childrenScore[nowBestScoreindex]
                else:
                    notevolvenum += 1
                    print(str(notevolvenum)+'not evolve')

            # 繁衍代数大于generationCount退出, 并输出最佳解
            if generation >= generationCount or notevolvenum == 20:
                print("*" * 46, "  ", generationCount, "代后最佳解  ", "*" * 46)
                # 并行排序
                selected = []
                fitnesslist = []
                for i in range(len(self.population)):
                    fitnesslist.append(self.population[i].fitness)
                fitnesslistindex = [i for i in range(len(self.population))]

                # 将第一组数据和第二组数据根据第一组数据的值进行组合和排序
                combined_data = sorted(zip(fitnesslist, fitnesslistindex), reverse=True)

                # 从排序后的数据中提取出前80%的第一组数据和对应的第二组数据
                sorted_data1, sorted_data2 = zip(*combined_data[:savenum])
                for i in sorted_data2:
                    selected.append(self.population[i])
                    print(self.population[i].fitness)

                return selected
    
    # 风格确定
    def musicstyle(self, zhugestyle=['A', 'A', 'B'], fugestyle=['B', 'B', 'C']):
        zhugestylecount = [len(list(v)) for k, v in groupby(zhugestyle)]
        print("生成主歌部分")
        # 主歌部分
        for i in range(len(zhugestylecount)):
            self.zhugeinit(100, 16, 1)
            ResultBestMyScore = self.run(50)
            # 尾部延长
            # 保存第一段
            for j in range(len(ResultBestMyScore)):
                self.zhugeScore[j].spliceexisscore(self.longmodify(self.replicate(ResultBestMyScore[j])))
            if zhugestylecount[i] > 1:
                for j in range(zhugestylecount[i]-1):
                    # 修改后尾
                    for k in range(len(ResultBestMyScore)):
                        self.zhugeScore[k].spliceexisscore(self.longmodify(self.copymodify(
                            self.replicate(ResultBestMyScore[k]))))

        fugestylecount = [len(list(v)) for k, v in groupby(fugestyle)]
        print("生成副歌部分")
        # 副歌部分
        for i in range(len(fugestylecount)):
            self.fugeinit(100, 16, 1)
            ResultBestMyScore = self.run(50)
            # 尾部延长
            # 保存第一段
            for j in range(len(ResultBestMyScore)):
                self.fugeScore[j].spliceexisscore(self.longmodify(self.replicate(ResultBestMyScore[j])))
            if fugestylecount[i] > 1:
                for j in range(fugestylecount[i] - 1):
                    # 修改后尾
                    for k in range(len(ResultBestMyScore)):
                        self.fugeScore[k].spliceexisscore(self.longmodify(self.copymodify(
                            self.replicate(ResultBestMyScore[k]))))
        for i in range(6):
            self.fullScore[i].spliceexisscore(self.zhugeScore[i])
            self.fullScore[i].spliceexisscore(self.fugeScore[i])
            self.fullScore[i].saveMyScore(filename=str(i))
            # self.fullScore[i].saveMyScore(filename=str(i)+'singer',singer=1)
        print("生成结束")
