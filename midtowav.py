import subprocess
for i in range(13):
    filename = str(i)
    savepath = "./othermethod/1/"
    # 定义要运行的命令
    command = ['FluidSynth', '-F', savepath + filename + '.wav', './sf2/YDPGrandPiano20160804.sf2',
               savepath + filename + '.mid']
    # 运行命令并等待其完成
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        output, error = process.communicate()
        if process.returncode != 0:
            print(f'An error occurred: {error}')