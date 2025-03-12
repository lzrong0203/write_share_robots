# git clone https://github.com/lzrong0203/PyPtt.git -b stock market time
import PyPtt
from PyPtt import data_type
import pandas as pd
import os
from dotenv import load_dotenv
from PyPtt import screens

load_dotenv()


class PyPttObj:
    def __init__(self):
        # self.ptt_bot = PyPtt.API()
        self.ptt_bot = PyPtt.API(log_level=PyPtt.LOG_LEVEL.SILENT)

    def login(self, ptt_id, ptt_pw):
        try:
            self.ptt_bot.login(
                ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
        #             kick_other_session=True:是用來在當此帳號在其他裝置上已經先登入時，將其登出從此裝置登入

        except PyPtt.LoginError:
            print('登入失敗')
        except PyPtt.WrongIDorPassword:
            print('帳號密碼錯誤')
        except PyPtt.OnlySecureConnection:
            print('只能使用安全連線')
        except PyPtt.ResetYourContactEmail:
            print('請先至信箱設定連絡信箱')

    def get_num_newest_posts(self, post_num):
        """
        取得post_num個，Stock版中最新的post_num個盤中閒聊文章
        """
        newest_index = self.ptt_bot.get_newest_index(
            index_type=data_type.NewIndex.BOARD, board='Stock', search_type=data_type.SearchType.KEYWORD,
            search_condition="盤中閒聊")
        # index_type=data_type.NewIndex.BOARD:取得特定看板(board='Stock')中的最新文章索引
        # data_type.SearchType.KEYWORD 表示使用關鍵字進行搜尋(search_condition="盤中閒聊")
        # 從newest_index開始往後爬取post_num篇post

        data = []
        for i in range(post_num):
            self.get_ptt_posts(data, newest_index, i)
            # newest_index-n:-n表示幾天前(在抓取特定日期的時候可以先抓一天做嘗試)

        return data

    def get_ptt_posts(self, data, newest_index, i):
        post_info = self.ptt_bot.get_post(
            'Stock', index=newest_index - i, search_type=data_type.SearchType.KEYWORD, search_condition="盤中閒聊")
        pushes_df = pd.DataFrame(post_info['comments'])
        #         取得的文章資訊中的評論部分轉換成 pandas 的 DataFrame 格式

        screens.Target.content_end_list.append('--\n※ 文章網址:')
        screens.Target.content_end_list.append('--\n\n※ 文章網址:')
        screens.Target.content_end_list.append('\n\n--\n※ 文章網址:')
        #       將例外進行排除

        pushes_df.rename(
            columns={'type': 'Tag', 'author': 'Userid', 'content': 'Content', 'ip': 'Ip', 'time': 'Ipdatetime'},
            inplace=True)
        #       將 DataFrame 的欄位名稱重新命名。EX:'type'變成 'Tag'
        #       inplace=True:修改應用於原始的 DataFrame 資料而不是創建一個新的 DataFrame

        pushes_json = pushes_df.to_json(orient='index', force_ascii=False)
        #       將處理過的 DataFrame pushes_df 轉換成 JSON 格式
        #       force_ascii=False:不會對 Unicode 字符進行轉換。這對於存儲或輸出含有非英文字符或特殊符號的資料非常有用，保證資料在轉換時保持原始的內容。

        data.append({'Title': post_info['title'], 'Author': post_info['author'], 'Date': post_info['date'],
                     'Content': post_info['content'], 'Link': post_info['url'], 'Pushes': pushes_json})

    #       以字典形式添加到 data 清單中

    def generate_newest_posts_dataset(self, post_num, save_path):
        """
        指定文章數量，取得文章並儲存成資料集
        """
        data = self.get_num_newest_posts(post_num=post_num)
        result_data_df = pd.DataFrame(data)
        # 格式轉換並儲存

        result_data_df.to_csv(save_path, encoding="utf_8_sig")
        # encoding="utf_8_sig":為了讓CSV不會變成亂碼

    def logout(self):
        self.ptt_bot.logout()


if __name__ == '__main__':
    # 建立物件
    pyptt_obj = PyPttObj()
    # 登入
    pyptt_obj.login(os.getenv('PTT1_ID'), os.getenv('PTT1_PW'))
    # 建立資料集
    pyptt_obj.generate_newest_posts_dataset(
        post_num=1, save_path='ptt_stock_posts.csv')
    # 登出
    pyptt_obj.logout()
