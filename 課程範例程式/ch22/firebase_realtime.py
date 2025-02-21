import time
import firebase_admin
from firebase_admin import credentials, db
from ch20.PTTScraper import PTT_SCRAPER


class Firebase_PTT_Realtime:
    def __init__(self, path):
        """
        初始化 Firebase Realtime Database 連線

        參數:
            path (str): 資料要儲存的路徑
        """
        # 初始化 Firebase 憑證
        cred = credentials.Certificate("stocksentiment-8cf69-firebase-adminsdk-rsalw-4d49167956.json")

        # 注意：請替換成您的資料庫 URL
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://stocksentiment-8cf69-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

        # 取得資料庫參考路徑
        self.ref = db.reference(path)

    def upload_post(self):
        """
        爬取 PTT 文章並上傳到 Realtime Database
        """
        board = "stock"
        scraper = PTT_SCRAPER(board)
        st = time.time()
        data = scraper.fetch_posts(max_posts=10, until_date="2/19")

        for index, d in data.iterrows():
            # 建立文章主體資料
            post_ref = self.ref.push({
                "title": d["title"],
                "date": d["date"],
                "content": d["content"],
                "timestamp": time.time()
            })

            # 取得新建立的文章的 key
            post_key = post_ref.key

            # 建立推文的參考路徑
            pushes_ref = self.ref.child(post_key).child('pushes')

            # 處理並上傳每一則推文
            if isinstance(d["pushes"], list):
                for i, push in enumerate(d["pushes"]):
                    if push:  # 確保 push 不是空字典
                        push_data = {
                            "tag": push.get("tag", ""),
                            "userid": push.get("userid", ""),
                            "content": push.get("content", ""),
                            "datetime": push.get("datetime", ""),
                            "index": i  # 加入順序索引
                        }
                        pushes_ref.push(push_data)

    def get_posts(self):
        """
        從 Realtime Database 讀取文章
        """
        # 取得所有文章
        posts = self.ref.get()
        if posts:
            for key, post in posts.items():
                print(f"文章 ID: {key}")
                print(f"標題: {post.get('title')}")
                print("----------------------")

    def get_single_post(self, post_key):
        """
        讀取單一文章
        """
        post = self.ref.child(post_key).get()
        if post:
            print(f"標題: {post.get('title')}")
            print(f"內容: {post.get('content')}")

    def update_post(self, post_key, update_data):
        """
        更新文章內容
        """
        self.ref.child(post_key).update(update_data)

    def delete_post(self, post_key):
        """
        刪除文章
        """
        self.ref.child(post_key).delete()


if __name__ == "__main__":
    firebase = Firebase_PTT_Realtime("ptt_posts")
    # 上傳新文章
    firebase.upload_post()

    # 讀取所有文章
    firebase.get_posts()

    # 更新特定文章
    # firebase.update_post("-NxyzABC123", {"title": "更新的標題"})