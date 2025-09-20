"""
基本图形绘制
封装 matplotlib 常用绘图接口，快速调用
"""
import matplotlib.pyplot as plt
import numpy as np
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False


def plot_line(x, y, title="折线图", xlabel="X", ylabel="Y", legend=None, grid=True):
    """折线图"""
    plt.figure()
    plt.plot(x, y, marker='o', label=legend)
    if legend:
        plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # 设置y轴范围为10到30
    plt.ylim(10, 30)
    plt.grid(True)  # 添加网格线
    plt.xticks(rotation=45)  # 将标签旋转45度

    if grid:
        plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_scatter(x, y, title="散点图", xlabel="X", ylabel="Y", color='blue', size=30):
    """散点图"""
    plt.figure()
    plt.scatter(x, y, c=color, s=size)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_bar(categories, values, title="柱状图", xlabel="分类", ylabel="值", color='skyblue'):
    """柱状图"""
    plt.figure()
    plt.bar(categories, values, color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()


def plot_hist(data, bins=10, title="直方图", xlabel="值", ylabel="频数", color='orange'):
    """直方图"""
    plt.figure()
    plt.hist(data, bins=bins, color=color, edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()


def plot_pie(labels, sizes, title="饼图", explode=None):
    """饼图"""
    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode)
    plt.title(title)
    plt.axis('equal')  # 保证饼图为正圆
    plt.tight_layout()
    plt.show()


def plot_multiple_lines(x, ys, labels=None, title="多条折线图", xlabel="X", ylabel="Y"):
    """多条折线图"""
    plt.figure()
    for i, y in enumerate(ys):
        label = labels[i] if labels else None
        plt.plot(x, y, marker='o', label=label)
    if labels:
        plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    x = np.linspace(0, 10, 11)
    y = x ** 2

    # 折线图
    plot_line(x, y, title="y=x^2", xlabel="x", ylabel="y", legend="平方")

    # 多条折线
    plot_multiple_lines(x, [x, x ** 2, x ** 3], labels=["y=x", "y=x^2", "y=x^3"])

    # 散点图
    plot_scatter(x, y, title="散点图", color='red', size=50)

    # 柱状图
    plot_bar(['A', 'B', 'C'], [10, 15, 7])

    # 直方图
    data = np.random.randn(1000)
    plot_hist(data, bins=20)

    # 饼图
    labels = ['苹果', '香蕉', '橙子']
    sizes = [30, 45, 25]
    plot_pie(labels, sizes)
