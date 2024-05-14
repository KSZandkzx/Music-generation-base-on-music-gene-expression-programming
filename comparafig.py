import numpy as np
import matplotlib.pyplot as plt

# 设置全局字体为新罗马字体
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Times New Roman'

# 设置全局字体大小
plt.rcParams.update({'font.size': 12})

# Sample data
x = ['Our method', 'GNETIC', 'TRANSFORMER', "LSTM With WAVENET", "A", "B"]
y = []
for i in [0,1,2,3,4,5]:
    savepath = "./othermethod/"+str(i)+"/"
    with open(savepath + "fitness.txt", "r") as file:
        # 逐行读取文件内容并获取数字
        numbers = []
        for line in file:
            number = float(line.strip())  # 去除每行末尾的换行符并将字符串转换为整数
            numbers.append(number)
    y.append(numbers)

# 计算每一个柱子的平均值，最小值和最大值
y_avg = [np.mean(bar) for bar in y]
y_min = [np.min(bar) for bar in y]
y_max = [np.max(bar) for bar in y]

# 设置柱子的颜色
# colors = ['red', 'green', 'orange', 'yellow']
colors = ['red', 'green', 'orange', 'yellow', 'purple', 'blue']


# 设置柱子的宽度
bar_width = 0.35

# Create an array of indices for each bar
indices = np.arange(len(x))

# 使用平均值绘制柱状图
fig, ax = plt.subplots()
bars = ax.bar(indices, y_avg, width=bar_width)

# 调整图像大小
fig.set_size_inches(18, 4.5)

# 调整y轴范围
plt.ylim(0,1)

# Adding labels and title
plt.xlabel('Categories of methods for generating music', fontsize=12)
plt.ylabel('Musical works assessment score', fontsize=12)
plt.title('Comparative experiments of various methods', fontsize=12)

# Set the x-axis tick positions and labels
ax.set_xticks(indices)
ax.set_xticklabels(x, fontsize=12)
plt.tick_params(axis='y', labelsize=12)
plt.tick_params(axis='x', labelsize=12)

# Adding error bars for minimum and maximum values
for i, bar in enumerate(bars):
    bar_x = bar.get_x() + bar.get_width() / 2
    bar_y = bar.get_height()
    error_min = bar_y - y_min[i]
    error_max = y_max[i] - bar_y
    ax.errorbar(bar_x, bar_y, yerr=[[error_min], [error_max]], color='black', capsize=5)
    bars[i].set_color(colors[i])
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.6f}', ha='center', va='bottom', fontsize=12)

# 创建图示
legend  = plt.legend(bars, x, title='Categories', loc='upper right', fontsize='12')
plt.setp(legend.get_title(), fontsize='12')

# Save the chart as a JPG file
plt.savefig('./figure/bar_chart.jpg', format='jpg', dpi=2000)

plt.show()