import time
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings


class FirebasePTTManager:
    """Firebase PTT 管理類，用於獲取 PTT 股票版文章"""
    
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """獲取單例實例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self, collection="ptt_posts"):
        """初始化 Firebase Firestore"""
        if not FirebasePTTManager._initialized:
            # 檢查 Firebase 是否已初始化
            try:
                # 嘗試獲取已存在的 Firebase 應用
                app = firebase_admin.get_app()
                self.db = firestore.client(app=app)
            except ValueError:
                # 如果未初始化，則初始化 Firebase
                cred_path = os.path.join(settings.BASE_DIR, 'stocksentiment-8cf69-firebase-adminsdk-rsalw-001d55408c.json')
                cred = credentials.Certificate(cred_path)
                try:
                    # 嘗試獲取 storage_app
                    app = firebase_admin.get_app(name='storage_app')
                    self.db = firestore.client(app=app)
                except ValueError:
                    # 如果 storage_app 不存在，創建新的 ptt_app
                    app = firebase_admin.initialize_app(cred, name='ptt_app')
                    self.db = firestore.client(app=app)
            
            self.collection_ref = self.db.collection(collection)
            FirebasePTTManager._initialized = True
        else:
            # 如果已經初始化，使用現有的應用
            try:
                app = firebase_admin.get_app(name='ptt_app')
            except ValueError:
                try:
                    app = firebase_admin.get_app(name='storage_app')
                except ValueError:
                    app = firebase_admin.get_app()
            self.db = firestore.client(app=app)
            self.collection_ref = self.db.collection(collection)
    
    def get_posts(self, limit=10, keyword=None):
        """獲取 PTT 股票版文章列表
        
        Args:
            limit: 最大獲取數量
            keyword: 搜尋關鍵字，如果提供則只獲取包含該關鍵字的文章
            
        Returns:
            文章列表，每個元素包含 id, title, date, content, pushes
        """
        try:
            # 按照創建時間排序，最新的在前面
            query = self.collection_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            
            # 用於去重的標題集合
            seen_titles = set()
            result = []
            
            for doc in docs:
                post_data = doc.to_dict()
                title = post_data.get('title', '')
                
                # 跳過已經看過的標題
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                # 如果提供了關鍵字，則檢查標題和內容是否包含該關鍵字
                if keyword:
                    content = post_data.get('content', '')
                    if keyword.lower() not in title.lower() and keyword.lower() not in content.lower():
                        continue
                
                # 格式化推文數據
                pushes = []
                if 'pushes' in post_data and isinstance(post_data['pushes'], list):
                    for push in post_data['pushes']:
                        pushes.append({
                            'type': push.get('type', ''),
                            'user': push.get('user', ''),
                            'content': push.get('content', ''),
                            'time': push.get('time', '')
                        })
                
                result.append({
                    'id': doc.id,
                    'title': post_data.get('title', ''),
                    'author': post_data.get('author', ''),
                    'date': post_data.get('date', ''),
                    'content': post_data.get('content', ''),
                    'push_count': len(pushes),
                    'pushes': pushes
                })
            
            return result
        
        except Exception as e:
            print(f"獲取 PTT 文章列表失敗: {e}")
            return []
    
    def get_post_by_id(self, post_id):
        """根據 ID 獲取文章詳情"""
        try:
            # 從 Firestore 獲取文章
            doc_ref = self.db.collection('ptt_posts').document(post_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            
            # 如果文章沒有內容，嘗試爬取
            if not post_data.get('content') or len(post_data.get('content', '').strip()) == 0:
                # 檢查是否有 URL
                if post_data.get('url'):
                    try:
                        # 使用爬蟲獲取文章內容
                        crawler = PTTCrawler()
                        post_content = crawler.get_post_content(post_data['url'])
                        
                        if post_content and 'content' in post_content:
                            # 更新文章內容
                            post_data['content'] = post_content['content']
                            post_data['pushes'] = post_content.get('pushes', [])
                            
                            # 更新 Firestore 中的文章
                            doc_ref.update({
                                'content': post_data['content'],
                                'pushes': post_data['pushes']
                            })
                    except Exception as e:
                        print(f"爬取文章內容時出錯: {e}")
            
            return post_data
        except Exception as e:
            print(f"獲取文章詳情時出錯: {e}")
            return None


def upload_ptt_post(title, author, date, content, pushes):
    """上傳 PTT 文章到 Firebase
    
    Args:
        title: 文章標題
        author: 作者
        date: 日期
        content: 內容
        pushes: 推文列表
        
    Returns:
        文章 ID
    """
    try:
        manager = FirebasePTTManager.get_instance()
        
        post = {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "pushes": pushes
        }
        
        post_id = f"post_{int(time.time())}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        manager.collection_ref.document(post_id).set(post)
        
        return post_id
    
    except Exception as e:
        print(f"上傳 PTT 文章失敗: {e}")
        return None 