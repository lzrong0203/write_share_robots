import time

import firebase_admin
from firebase_admin import credentials, firestore
from ch20.PTTScraper import PTT_SCRAPER


"""Firestore 和 Realtime Database 都是 Firebase 提供的 NoSQL 資料庫
Firestore 比較像是一個文件式的資料庫，它的結構是由集合（Collections）和文件（Documents）所組成，
有點像是電腦裡的資料夾和檔案的概念。我們建立了一個叫做 "ptt_posts" 的集合，然後在裡面存放不同的文件。
Firestore 特別適合需要複雜查詢的應用程式，而且能自動進行擴展。
Realtime Database 則是採用 JSON 樹狀結構來儲存資料。
它的設計比較簡單，但在即時同步方面表現優異。因為傳輸的資料量較小，所以在需要即時更新的應用中較有效率。
"""


class Firebase_PTT:

    def __init__(self, collection):
        """
        Certificate 請替換成自己的
        """
        cred = credentials.Certificate("stocksentiment-8cf69-firebase-adminsdk-rsalw-4d49167956.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        self.collection_ref = db.collection(collection)

    def upload_post(self):
        board = "stock"
        scraper = PTT_SCRAPER(board)
        st = time.time()
        data = scraper.fetch_posts(max_posts=5, until_date="1/20")[["title", "date"]]
        for d in data.iterrows():
            post = {
                "title": d["title"],
                "date": d["date"],
                "content": d["content"],
                "pushes": d["pushes"]
            }
            post_id = f"post_{d[0]}_{time.strftime('%Y%m%d_%H%M%S')}"
            self.collection_ref.document(post_id).set(post)

    def get_post(self):
        posts = self.collection_ref.stream()
        for post in posts:
            print(post.id)
            print(post.to_dict()["title"])

if __name__ == "__main__":
    firebase = Firebase_PTT("ptt_posts")
    # firebase.get_post()
    post_ref = firebase.collection_ref.document("post_9_20241105_133803")
    doc = post_ref.get()

    if doc.exists:
        print(f"data: {doc.to_dict()}")