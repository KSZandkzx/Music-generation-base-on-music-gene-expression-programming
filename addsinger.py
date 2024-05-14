import mymain
rad1 = "./othermethod/0/77.txt"
rad2 = "./temp/singer/"
#使用已有对象完成转换
nowScore = mymain.MyScore(1,16).readMyScore(rad1)
nowScore.saveMyScore(savepath=rad2, filename='77singer',singer=1)
nowScore.saveMyScore(savepath=rad2, filename='77origin',singer=0)