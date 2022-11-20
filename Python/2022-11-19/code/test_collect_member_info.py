# -*- coding: utf-8 -*-
# @Date:2022/11/16 17:49
# @Author: Lu
# @Description
import sqlite3
import time

import pyautogui
from pygetwindow import Win32Window
from pyrect import Box

from clipboard import Clipboard
from shot_screen import ShotUtil


class MemberDataBase(object):
    def __init__(self):
        self.connect = sqlite3.connect('member.db')
        self.connect.execute("""
        CREATE TABLE  IF NOT EXISTS "user" (
                "ID" INTEGER,
                "nickname" TEXT NOT NULL,
                "dingID" TEXT UNIQUE NOT NULL,
                PRIMARY KEY ("ID")
                );
        """)

    def insert_user(self, nickname: str, dingID: str):
        c = self.connect.cursor()
        c.execute(f"insert or ignore into user (nickname, dingID) values ('{nickname}', '{dingID}');")
        c.close()

    def search_not_dingID_users(self):
        c = self.connect.cursor()
        c.execute(f'select * from user where dingID=null;')
        data = c.fetchall()
        c.close()
        return data

    def has_dingID(self, nickname: str) -> bool:
        c = self.connect.cursor()
        sql = f"select nickname from user where nickname='{nickname}' and dingID is NOT NULL;"
        c.execute(sql)
        data = c.fetchone()
        c.close()
        if data:
            return True
        return False

    def close(self):
        self.connect.commit()
        self.connect.close()


db = MemberDataBase()


class SearchMemberAction(object):
    def __init__(self):
        """
        win:钉钉窗口
        nickname:昵称，用于搜索对应的用户
        header_p: 用户聊天对话，顶部头像坐标
        """
        self.nickname: str = None
        self.win: Win32Window = None
        self.header_p: (int, int) = None

    def do_init(self, win: Win32Window, nickname: str, header_p: (int, int)):
        self.nickname = nickname
        self.win = win
        self.header_p = header_p

    def run(self):
        pyautogui.click(self.win.centerx, self.win.top + 15)
        Clipboard.setText(self.nickname)
        time.sleep(0.5)
        Clipboard.paste()
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(0.5)

        # 查看用户个人信息
        pyautogui.click(self.header_p)
        time.sleep(0.5)
        # 用户信息弹窗
        win_user = pyautogui.getActiveWindow()
        pyautogui.moveTo((win_user.centerx, win_user.centery))
        # 滚到底部
        pyautogui.mouseDown((win_user.right - 5, win_user.bottom - 150), duration=150)
        time.sleep(0.5)
        pyautogui.mouseUp()

        img = ShotUtil.shot_active_window()
        box: Box = pyautogui.locate("./img/钉钉号.png", img)
        if not box:
            print(f"{self.nickname} 找不到钉钉号，请自行检查")
            return
        pyautogui.moveTo(win_user.left + box.width + 75, win_user.top + box.top + 10)
        pyautogui.rightClick()
        pyautogui.hotkey('down')
        pyautogui.hotkey('enter')

        dingID = Clipboard.getText()
        print(f'{self.nickname},{dingID}')
        db.insert_user(self.nickname, dingID)


def main():
    win_py: Win32Window = pyautogui.getActiveWindow()
    win_ding: Win32Window = pyautogui.getWindowsWithTitle('钉钉')[0]
    win_ding.activate()
    win_ding.maximize()
    time.sleep(0.5)
    f = open('./res/nikenames.txt', 'r', encoding='utf-8')
    action = None

    for index, line in enumerate(f.readlines()):
        nickname = line.strip()
        if db.has_dingID(nickname):
            continue
        if index % 20 == 0:
            db.connect.commit()

        if not action:
            action = SearchMemberAction()
        action.do_init(win_ding, nickname, (512, 82))

        try:
            action.run()
        except Exception as e:
            # 重试
            try:
                action.run()
            except Exception as e:
                print(e)
    f.close()
    db.close()
    win_py.activate()


def test_main():
    main()
