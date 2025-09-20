"""
在热力图上绘制矢量场(箭头)的工具类
支持 streamplot(流线箭头) 和 quiver(离散箭头)
可一次性保存PNG、PDF、SVG多种格式，并自动创建文件夹
"""

import numpy as np
import matplotlib.pyplot as plt
import os


class HeatmapVectorPlot:
    """
    在热力图上绘制矢量场(箭头)的工具类
    支持 streamplot(流线箭头) 和 quiver(离散箭头)
    可一次性保存PNG、PDF、SVG多种格式，并自动创建文件夹
    """
    def __init__(self, X, Y, Z, U, V, cmap='hot'):
        """
        X, Y: 网格坐标 (meshgrid)
        Z: 热力图数据
        U, V: 矢量场分量
        cmap: 热力图配色
        """
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        self.X = X
        self.Y = Y
        self.Z = Z
        self.U = U
        self.V = V
        self.cmap = cmap

    def _ensure_dir(self, dir_path):
        """确保目录存在"""
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _save_multi(self, basefile, formats, dpi=300):
        """辅助函数：多格式保存"""
        for fmt in formats:
            plt.savefig(f"{basefile}.{fmt}", dpi=dpi, bbox_inches='tight')

    def plot(self, mode='stream', density=1.5, linewidth=1, scale=30,
             arrow_color='white', figsize=(8,6),
             title='Heatmap with Vector Field',
             savefile_prefix=None, save_dir=None,
             formats=('png',), dpi=300):
        """
        绘制并显示图像
        mode: 'stream' = 流线箭头, 'quiver' = 离散箭头
        density: streamplot疏密
        linewidth: streamplot线宽
        scale: quiver箭头长度缩放
        arrow_color: 箭头颜色
        figsize: 画布大小
        title: 标题
        dpi: 分辨率
        savefile_prefix: 文件名前缀
        save_dir: 保存文件夹路径（None=当前目录）
        formats: 保存格式列表 ('png','pdf','svg')
        """
        plt.figure(figsize=figsize)
        plt.imshow(self.Z,
                   extent=[self.X.min(), self.X.max(), self.Y.min(), self.Y.max()],
                   origin='lower', cmap=self.cmap, aspect='auto')

        if mode == 'stream':
            plt.streamplot(self.X, self.Y, self.U, self.V,
                           color=arrow_color, density=density, linewidth=linewidth)
        elif mode == 'quiver':
            plt.quiver(self.X, self.Y, self.U, self.V,
                       color=arrow_color, scale=scale)
        else:
            raise ValueError("mode must be 'stream' or 'quiver'")

        plt.colorbar(label='Intensity')
        plt.title(title)

        # 保存
        if savefile_prefix:
            if save_dir:
                self._ensure_dir(save_dir)
                basefile = os.path.join(save_dir, savefile_prefix)
            else:
                basefile = savefile_prefix
            self._save_multi(basefile, formats, dpi)

        plt.show()

    def compare(self, density=1.5, linewidth=1, scale=30,
                arrow_color='white', figsize=(12,5),
                title_left='Heatmap + Streamplot',
                title_right='Heatmap + Quiver',
                savefile_prefix=None, save_dir=None,
                formats=('png',), dpi=300):
        """
        同时绘制左边 streamplot + 右边 quiver 对比
        并可保存两张单独图片
        save_dir: 保存目录
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # 左边 streamplot
        im1 = ax1.imshow(self.Z, extent=[self.X.min(), self.X.max(),
                                         self.Y.min(), self.Y.max()],
                         origin='lower', cmap=self.cmap, aspect='auto')
        ax1.streamplot(self.X, self.Y, self.U, self.V,
                       color=arrow_color, density=density, linewidth=linewidth)
        ax1.set_title(title_left)
        fig.colorbar(im1, ax=ax1)

        # 右边 quiver
        im2 = ax2.imshow(self.Z, extent=[self.X.min(), self.X.max(),
                                         self.Y.min(), self.Y.max()],
                         origin='lower', cmap=self.cmap, aspect='auto')
        ax2.quiver(self.X, self.Y, self.U, self.V,
                   color=arrow_color, scale=scale)
        ax2.set_title(title_right)
        fig.colorbar(im2, ax=ax2)

        plt.tight_layout()

        # 保存对比图
        if savefile_prefix:
            if save_dir:
                self._ensure_dir(save_dir)
                basefile = os.path.join(save_dir, f"{savefile_prefix}_compare")
            else:
                basefile = f"{savefile_prefix}_compare"
            self._save_multi(basefile, formats, dpi)

        plt.show()

        # 保存单独图片
        if savefile_prefix:
            self.plot(mode='stream', density=density, linewidth=linewidth,
                      arrow_color=arrow_color,
                      title=title_left,
                      savefile_prefix=f"{savefile_prefix}_stream",
                      save_dir=save_dir,
                      formats=formats, dpi=dpi)
            self.plot(mode='quiver', scale=scale,
                      arrow_color=arrow_color,
                      title=title_right,
                      savefile_prefix=f"{savefile_prefix}_quiver",
                      save_dir=save_dir,
                      formats=formats, dpi=dpi)


# ========== 使用示例 ==========
if __name__ == "__main__":
    nx, ny = (30, 30)
    x = np.linspace(0, 2*np.pi, nx)
    y = np.linspace(0, 2*np.pi, ny)
    X, Y = np.meshgrid(x, y)

    Z = np.sin(X) * np.cos(Y)
    U = -np.cos(X) * np.sin(Y)
    V = np.sin(X) * np.cos(Y)

    plotter = HeatmapVectorPlot(X, Y, Z, U, V, cmap='hot')

    # 保存到 output 文件夹，格式为 PNG、PDF、SVG
    plotter.compare(savefile_prefix='heatmap_example',
                    save_dir='output',
                    formats=('png', 'pdf', 'svg'))
