import time
import PyPtt
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()


class PyPttObj:
    def __init__(self):
        self.ptt_bot = PyPtt.API(log_level=PyPtt.LOG_LEVEL.SILENT)

    def login(self):
        max_retry = 5

        for retry in range(max_retry):
            try:
                if self.ptt_bot is None:
                    self.ptt_bot = PyPtt.API()
                self.ptt_bot.login(
                    ptt_id=os.getenv('ptt_id'),
                    ptt_pw=os.getenv('ptt_pw'),
                    kick_other_session=True)
                break
            except PyPtt.LoginError:
                self.ptt_bot = None
                print('登入失敗')
                time.sleep(3)
            except PyPtt.WrongIDorPassword:
                self.ptt_bot = None
                print('帳號密碼錯誤')
            except PyPtt.OnlySecureConnection:
                self.ptt_bot = None
                print('只能使用安全連線')
            except PyPtt.ResetYourContactEmail:
                self.ptt_bot = None
                print('請先至信箱設定連絡信箱')
            except PyPtt.exceptions.LoginTooOften:
                self.ptt_bot = None
                print("請稍後再試")
            time.sleep(5)

    def logout(self):
        self.ptt_bot.logout()

    def get_num_newest_posts(self, post_num=1):
        search_list = [(PyPtt.SearchType.KEYWORD, '盤中閒聊')]
        newest_index = self.ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD,
                                                     board="Stock",
                                                     search_list=search_list
                                                     )
        from PyPtt import screens
        screens.Target.content_end_list.append('--\n※ 文章網址')
        screens.Target.content_end_list.append('--\n\n※ 文章網址:')
        screens.Target.content_end_list.append('\n\n--\n※ 文章網址:')
        post_data = []
        for i in range(post_num):
            post_info = self.ptt_bot.get_post(board="Stock",
                                              index=newest_index - i,
                                              search_list=search_list)
            post_data.append({"title": post_info["title"], "comments": post_info["comments"],
                              "num_of_comments": len(post_info["comments"])})

        return post_data


if __name__ == "__main__":
    ptt = PyPttObj()
    ptt.login()
    for p in ptt.get_num_newest_posts(5):
        print(p["title"], p["num_of_comments"])
    ptt.logout()
