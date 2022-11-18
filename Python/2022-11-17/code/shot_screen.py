# -*- coding: utf-8 -*-
# @Date:2022/10/30 15:35
# @Author: Lu
# @Description window截屏
import win32con
import win32gui
import win32ui
from PIL import Image


class ShotUtil(object):

    @staticmethod
    def shot_active_window() -> Image.Image:
        hWnd = win32gui.GetForegroundWindow()
        # 获取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(hWnd)
        width = right - left
        height = bot - top
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hWndDC = win32gui.GetWindowDC(hWnd)
        # 创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        # 创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        # 将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        ###获取位图信息
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        ###生成图像
        im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        # 内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hWnd, hWndDC)
        return im_PIL
