"""
交互式 colorbar 调用
一次只显示一个图
可以滚动 也可以点击调节最大值和最小值 支持手动输入最大值与最小值
左键修改最小值 右键修改最大值
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
from matplotlib.backend_bases import MouseEvent


class InteractiveColorbar:
    """
    交互式 colorbar
    """
    def __init__(self, x, y, z, cmap='viridis', font='SimHei'):
        # 中文字体
        plt.rcParams['font.sans-serif'] = [font]
        plt.rcParams['axes.unicode_minus'] = False

        self.x, self.y, self.z = x, y, z
        self.cmap = cmap

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        plt.subplots_adjust(bottom=0.20)  # 预留底部空间多一点

        self.im = self.ax.imshow(z, origin='lower', cmap=cmap)
        self.cbar = self.fig.colorbar(self.im, ax=self.ax)
        self.ax.set_title("交互式 Colorbar")
        self.ax.set_xlabel("X 轴")
        self.ax.set_ylabel("Y 轴")

        # 原始范围
        self.orig_vmin, self.orig_vmax = np.min(z), np.max(z)
        self.vmin, self.vmax = self.im.get_clim()

        # 在底部放两个输入框
        # left, bottom, width, height
        ax_box_vmin = plt.axes((0.15, 0.05, 0.1, 0.05))
        ax_box_vmax = plt.axes((0.45, 0.05, 0.1, 0.05))
        self.textbox_vmin = TextBox(ax_box_vmin, 'vmin: ', initial=f"{self.vmin:.6f}")
        self.textbox_vmax = TextBox(ax_box_vmax, 'vmax: ', initial=f"{self.vmax:.6f}")

        self.textbox_vmin.on_submit(self.update_vmin)
        self.textbox_vmax.on_submit(self.update_vmax)

        # 重置按钮
        ax_reset = plt.axes((0.75, 0.05, 0.1, 0.05))
        self.button_reset = Button(ax_reset, '重置范围')
        self.button_reset.on_clicked(self.reset_range)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('scroll_event', self.onscroll)
        self.fig.canvas.mpl_connect('button_press_event', self.on_dblclick)

        # self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        # self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        # self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
    # def on_press(self, event):
    #     if event.inaxes == self.cbar.ax:
    #         self.dragging['active'] = True
    #         self.dragging['start_y'] = event.ydata
    #         self.dragging['vmin'], self.dragging['vmax'] = self.im.get_clim()
    #         if event.key == 'shift':
    #             self.dragging['modifier'] = 'shift'
    #         elif event.key == 'control':
    #             self.dragging['modifier'] = 'ctrl'
    #         else:
    #             self.dragging['modifier'] = None
    #
    # def on_release(self, event):
    #     self.dragging['active'] = False
    #     self.dragging['modifier'] = None
    # def on_motion(self, event):
    #     if self.dragging['active'] and event.inaxes == self.cbar.ax and event.ydata is not None:
    #         dy = event.ydata - self.dragging['start_y']
    #         scale = (self.dragging['vmax'] - self.dragging['vmin']) / 50.0
    #         vmin0, vmax0 = self.dragging['vmin'], self.dragging['vmax']
    #         mod = self.dragging['modifier']
    #         if mod == 'shift':
    #             new_vmin, new_vmax = vmin0 + dy * scale, vmax0
    #         elif mod == 'ctrl':
    #             new_vmin, new_vmax = vmin0, vmax0 + dy * scale
    #         else:
    #             new_vmin, new_vmax = vmin0 + dy * scale, vmax0 + dy * scale
    #         if new_vmax > new_vmin:
    #             self.apply_clim(new_vmin, new_vmax)

    def update_vmin(self, text):
        try:
            self.vmin = float(text)
            self.im.set_clim(self.vmin, self.vmax)
            print(f'vmin is {self.vmin}, vmax is {self.vmax}')
        except ValueError:
            pass

    def update_vmax(self, text):
        try:
            self.vmax = float(text)
            self.im.set_clim(self.vmin, self.vmax)
            print(f'vmin is {self.vmin}, vmax is {self.vmax}')

        except ValueError:
            pass

    def reset_range(self, _event=None):
        """重置 vmin / vmax 为原始数据范围"""
        self.vmin, self.vmax = self.orig_vmin, self.orig_vmax
        self.textbox_vmin.set_val(f"{self.vmin:.2f}")
        self.textbox_vmax.set_val(f"{self.vmax:.2f}")
        self.im.set_clim(self.vmin, self.vmax)

    def onclick(self, event: MouseEvent) -> None:
        if event.inaxes == self.cbar.ax:
            norm_y = (event.y - self.cbar.ax.get_position().y0 * self.fig.bbox.height) / (
                self.cbar.ax.get_position().height * self.fig.bbox.height
            )
            data_val = self.vmin + norm_y * (self.vmax - self.vmin)
            if event.button == 1:  # 左键调 vmin
                self.vmin = data_val
                self.textbox_vmin.set_val(f"{self.vmin:.2f}")
            elif event.button == 3:  # 右键调 vmax
                self.vmax = data_val
                self.textbox_vmax.set_val(f"{self.vmax:.2f}")
            self.im.set_clim(self.vmin, self.vmax)

    def on_dblclick(self, event):
        if event.inaxes == self.cbar.ax and event.button == 3 and event.dblclick:
            self.reset_range()  # 恢复原始范围

    def onscroll(self, event: MouseEvent):
        if event.inaxes == self.cbar.ax:
            print(f'current button is {event.button}')
            scale = 0.9 if event.button == 'up' else 1.1
            print(f'scale is {scale}')
            center = (self.vmin + self.vmax) / 2
            print(f'center is {center}')
            half_range = (self.vmax - self.vmin) / 2 * scale
            print(f'half_range is {half_range}')
            self.vmin = center - half_range
            self.vmax = center + half_range
            print(f'vmin is {self.vmin}, vmax is {self.vmax}')
            self.textbox_vmin.set_val(f"{self.vmin:.2f}")
            self.textbox_vmax.set_val(f"{self.vmax:.2f}")
            self.im.set_clim(self.vmin, self.vmax)

    @staticmethod
    def show():
        plt.show()


# 直接运行示例
if __name__ == "__main__":
    _x = np.linspace(-3, 3, 200)
    _y = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(_x, _y)
    Z = np.sin(X**2 + Y**2) / (X**2 + Y**2 + 1e-6)

    icb = InteractiveColorbar(X, Y, Z)
    icb.show()
