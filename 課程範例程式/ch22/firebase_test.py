import time

import firebase_admin
from firebase_admin import credentials, firestore
from ch20.PTTScraper import PTT_SCRAPER


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