import PyPtt
from dotenv import load_dotenv
import os

load_dotenv()


class PTT_OBJ:

    def __init__(self):
        self.ptt_bot = PyPtt.API(log_level=PyPtt.LOG_LEVEL.SILENT)

    def login(self):

        try:
            self.ptt_bot.login(
                ptt_id=os.getenv('ptt_id'), ptt_pw=os.getenv('ptt_pw'), kick_other_session=True)
        except PyPtt.LoginError:
            print('登入失敗')
        except PyPtt.WrongIDorPassword:
            print('帳號密碼錯誤')
        except PyPtt.OnlySecureConnection:
            print('只能使用安全連線')
        except PyPtt.ResetYourContactEmail:
            print('請先至信箱設定連絡信箱')

    def logout(self):
        self.ptt_bot.logout()


if __name__ == "__main__":
    ptt = PTT_OBJ()
    ptt.login()
    post_info = ptt.ptt_bot.get_post("Stock", index=1,
                                     search_list=[(PyPtt.SearchType.KEYWORD, '台積電')])
    print(list(post_info.keys()))
    print(post_info["date"], post_info["title"])
    print(post_info["comments"])
    print(post_info)
