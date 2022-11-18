# -*- coding: utf-8 -*-
# @Date:2022/11/18 0:44
# @Author: Lu
# @Description
import os
import re
from typing import Literal

import onceutils


class GitMan(object):
    def __init__(self, work_path):
        self.work_path = os.path.abspath(work_path)
        os.chdir(self.work_path)

    def branch(self):
        f = os.popen('git branch --show', mode='r')
        branch_name = f.read()
        f.close()
        return branch_name.strip()


class MarkdownLinkProcess(object):
    def __init__(self, git_project_path, mode: Literal['gitee', 'github'], user: str, branch_name: str):
        self.git_project_path = os.path.abspath(git_project_path)
        self.mode = mode
        self.user = user
        self.project = os.path.basename(self.git_project_path)
        self.branch = branch_name

    def process(self, ):
        for root, dirs, files in os.walk(self.git_project_path):
            for f in files:
                if not f.lower().endswith('.md'):
                    continue
                if os.path.basename(root) in ['.git', '.idea', '.pytest_cache', 'Python', '__pycache__']:
                    continue
                if re.search(r'gitee|github\.md', f, re.I):
                    continue
                self.process_file(os.path.abspath(os.path.join(root, f)))

    def process_file(self, file_path: str):
        file_mode_path = f"{file_path[0: -len('.md')]}.{self.mode}.md"

        text = onceutils.read_text(file_path)
        text_process = self.collect_process_text(file_path, text)
        if text == text_process:
            if os.path.exists(file_mode_path):
                os.remove(file_mode_path)

            print(f'{file_path} not need create {self.mode} file!!!')
            return
        # set newline="" to keep the line, no change
        with open(file_mode_path, 'w', encoding='utf-8', newline="") as f:
            f.write(text_process)

    def collect_process_text(self, file_path: str, text: str) -> str:
        # 进入当前目录中，以便处理md文档中的相对路径
        lines = []
        os.chdir(os.path.dirname(file_path))
        for line in text.splitlines(keepends=True):
            # ![name](link) : markdown img or link
            m = re.search(r'!?\[(.*)?]\(([^:*?|<>\n\r\t]+?)\)', line)
            if m:
                alt = m.group(1)
                if not alt:
                    alt = ""
                url = m.group(2)
                if m.group(0).startswith("!") and re.search(r'\.svg$', url, re.I):
                    # svg图片链接在一些博客的markdown编辑器中无法正常显示，需要手动上传
                    # 转为html <img>标签后正常显示
                    span = m.span(0)
                    line2html = line[:span[0]] + f'<img alt="{alt}" src="{url}">' + line[span[1]:]
                    line = self.process_line_html(line2html)
                else:
                    # 处理markdown标签
                    line = self.process_line_md(line)
            elif re.search(r"<(?:img|a)\s.+?/?>", line):
                # 处理html标签
                line = self.process_line_html(line)
            lines.append(line)
        return "".join(lines)

    def fix_url_line(self, line: str, url: str, fix_url: str, span: tuple[int, int]):
        try:
            if not fix_url == url:
                line = line[0:span[0]] + fix_url + line[span[1]:]
        except:
            pass
        return line

    def process_line_md(self, line: str):
        m = re.search(r"!?\[.*?]\(([^:*?|<>\n\r\t]+?)\)", line)
        if not m:
            return line
        url = m.group(1)
        if m.group(0).startswith("!"):
            fix_url = self.make_http_url(url, jsdrive=True)
        else:
            fix_url = self.make_http_url(url)
        line = self.fix_url_line(line, url, fix_url, m.span(1))
        return line

    def process_line_html(self, line: str) -> str:
        m = re.search(r"<a\s.*?href=(['\"])(.*?)\1.*?/?>", line, re.I)
        if m:
            href = m.group(2)
            fix_href = self.make_http_url(href)
            line = self.fix_url_line(line, href, fix_href, m.span(2))

        m = re.search(r"<img\s.*?src=([\"'])(.*?)\1.*?/?>", line, re.I)
        if m:
            src = m.group(2)
            fix_src = self.make_http_url(src, jsdrive=True)
            line = self.fix_url_line(line, src, fix_src, m.span(2))
        return line

    def make_http_url(self, url, jsdrive=False):
        if re.search(r'https?://|//', url, re.I):
            # 网络链接不用处理
            return False
        abs_url = os.path.abspath(url)
        if not abs_url.startswith(self.git_project_path):
            print(
                f"Error, abs_url not start with work_parh!!!\n abs_url: {abs_url}\n work_path: {self.git_project_path}"
            )
            return url
        ret = url
        rel_path = abs_url.replace(self.git_project_path, "").replace("\\", "/")
        if 'gitee' == self.mode:
            ret = f'https://gitee.com/{self.user}/{self.project}/raw/{self.branch}{rel_path}'
        elif 'github' == self.mode:
            if not jsdrive:
                ret = f'https://raw.githubusercontent.com/{self.user}/{self.project}/{self.branch}{rel_path}'
            # 利用jsdrive加速
            else:
                ret = f'https://cdn.jsdelivr.net/gh/{self.user}/{self.project}{rel_path}'
        return ret


def main():
    # gitee防盗链了
    git_project_path = './'
    branch = GitMan(git_project_path).branch()
    MarkdownLinkProcess(git_project_path,
                        mode='github',
                        user='Mingyueyixi',
                        branch_name=branch).process()


def test_main():
    main()