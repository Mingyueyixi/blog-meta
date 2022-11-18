# -*- coding: utf-8 -*-
# Author:Lu
# Date:2022/11/3
# Description:
import time

import pyautogui
from pygetwindow import Win32Window
from pyscreeze import Box

from clipboard import Clipboard


class SearchGroupAction(object):

    def __init__(self, name, win: Win32Window):
        self.name = name
        self.win = win

    def run(self):
        w = self.win
        x = w.left + w.width / 2
        y = w.top + 10

        Clipboard.setText(self.name)
        pyautogui.click((x, y))
        time.sleep(0.5)
        Clipboard.paste()
        time.sleep(1)
        pyautogui.hotkey("enter")
        time.sleep(0.5)


class ParseMemberInfoAction(object):
    def __init__(self, win_ding: Win32Window):
        self.win = win_ding
        self.win_setting = None
        self.result_text = ''

    def run(self):
        w = self.win
        # 点击设置，访问设置对话框
        pyautogui.click((w.right - 35, w.top + 65))
        time.sleep(1)
        win_setting = pyautogui.getActiveWindow()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        text = Clipboard.getText()
        # 取消选中
        pyautogui.click(w.right - 100, w.top + 100)
        if '查看更多' in text:
            img = pyautogui.screenshot(
                region=(win_setting.left, win_setting.top, win_setting.width, win_setting.bottom))
            box: Box = pyautogui.locate(f'./res/chakangengduo.png', img)
            pyautogui.click(win_setting.left + box.left + box.width / 2, win_setting.top + box.top + box.height / 2)
            pyautogui.vscroll(-3000)

            time.sleep(0.5)
            # 滚动到底部后，此时”查看更多“的坐标固定了。下次点击可以不用再截图查坐标
            img = pyautogui.screenshot(
                region=(win_setting.left, win_setting.top, win_setting.width, win_setting.bottom))
            box: Box = pyautogui.locate(f'./res/chakangengduo.png', img)

            pyautogui.click(win_setting.left + box.left + box.width / 2, win_setting.top + box.top + box.height / 2)
            while True:
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                text = Clipboard.getText()
                # 取消全选
                pyautogui.click()
                if '查看更多' not in text:
                    print(text)
                    self.result_text = text
                    return self
                pyautogui.click(win_setting.left + box.left + box.width / 2, win_setting.top + box.top + box.height / 2)
                pyautogui.vscroll(-3000)
                time.sleep(1)

        return self


def main():
    pywindow = pyautogui.getActiveWindow()
    w = pyautogui.getWindowsWithTitle('钉钉')[0]
    w.activate()
    w.maximize()
    print(w)

    SearchGroupAction("xxx沙雕群", w).run()
    pmc = ParseMemberInfoAction(w).run()

    time.sleep(3)
    pywindow.activate()


def test_main():
    main()
