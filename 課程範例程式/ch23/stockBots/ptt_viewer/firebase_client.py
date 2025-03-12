import firebase_admin
from firebase_admin import credentials, db
import os

class FirebasePTTClient:
    """Firebase PTT 文章客戶端"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """單例模式獲取實例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化 Firebase 連接"""
        # 檢查 Firebase 是否已初始化
        if not firebase_admin._apps:
            # 獲取專案根目錄的絕對路徑
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 憑證文件的路徑
            cred_path = os.path.join(base_dir, "stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
            
            # 初始化 Firebase
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://stocksentiment-8cf69-default-rtdb.asia-southeast1.firebasedatabase.app/',
                'storageBucket': 'stocksentiment-8cf69.firebasestorage.app'
            })
        
        # 獲取 PTT 文章的參考路徑
        self.ref = db.reference('ptt_posts')
    
    def get_all_posts(self, limit=20):
        """
        獲取所有文章
        
        參數:
            limit: 最大返回數量
        """
        # 獲取數據
        posts = self.ref.get()
        
        # 處理數據
        result = []
        if posts:
            # 轉換為列表並添加 ID
            for post_id, post in posts.items():
                post['id'] = post_id
                result.append(post)
            
            # 按時間戳降序排序
            result.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # 應用限制
            result = result[:limit]
        
        return result
    
    def get_post(self, post_id):
        """
        獲取單篇文章
        
        參數:
            post_id: 文章 ID
        """
        post = self.ref.child(post_id).get()
        if post:
            post['id'] = post_id
        return post 