# Django 與 Firebase 整合的股市分析平台教學 - 第三部分：Firebase 整合

## 四、Firebase 整合實現

### 1. Firebase 專案設置

在開始整合 Firebase 之前，需要先在 Firebase 控制台創建專案並設置相關服務：

1. 創建 Firebase 專案
2. 啟用 Firebase Authentication，設置電子郵件/密碼登入
3. 創建 Firestore 數據庫
4. 啟用 Firebase Storage
5. 下載服務帳戶密鑰 JSON 文件，放在專案根目錄

### 2. Firebase 認證實現

#### 2.1 安裝依賴

首先，安裝 Firebase Admin SDK：

```bash
pip install firebase-admin
```

#### 2.2 實現 FirebaseAuth 類

在 `firebase_auth.py` 中實現 Firebase 認證功能：

```python
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

class FirebaseAuth:
    """Firebase 認證工具類"""
    
    _app = None
    
    @classmethod
    def initialize_firebase(cls):
        """初始化 Firebase 應用程式"""
        if cls._app is None:
            # 指定服務金鑰的路徑
            cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')
            cred = credentials.Certificate(cred_path)
            cls._app = firebase_admin.initialize_app(cred)
        return cls._app
    
    @classmethod
    def verify_id_token(cls, id_token):
        """驗證 Firebase ID Token"""
        if cls._app is None:
            cls.initialize_firebase()
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Firebase 驗證錯誤: {e}")
            return None
    
    @classmethod
    def get_user_by_email(cls, email):
        """透過電子郵件獲取用戶資訊"""
        if cls._app is None:
            cls.initialize_firebase()
        try:
            user = auth.get_user_by_email(email)
            return user
        except Exception as e:
            print(f"獲取用戶錯誤: {e}")
            return None
    
    @classmethod
    def get_user_by_uid(cls, uid):
        """透過 UID 獲取用戶資訊"""
        if cls._app is None:
            cls.initialize_firebase()
        try:
            user = auth.get_user(uid)
            return user
        except Exception as e:
            print(f"獲取用戶錯誤: {e}")
            return None
```

#### 2.3 實現用戶模型

在 `models.py` 中定義 `FirebaseUser` 模型：

```python
from django.db import models

class FirebaseUser(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    photo_url = models.URLField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.firebase_uid
```

#### 2.4 實現認證中間件

在 `middleware.py` 中實現 `FirebaseAuthMiddleware`：

```python
from django.contrib.auth.models import AnonymousUser
from .firebase_auth import FirebaseAuth
from .models import FirebaseUser

class FirebaseAuthMiddleware:
    """Firebase 認證中間件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 初始化 Firebase
        FirebaseAuth.initialize_firebase()
    
    def __call__(self, request):
        # 檢查 session 中是否有用戶資訊
        firebase_uid = request.session.get('firebase_uid')
        if firebase_uid:
            try:
                # 從資料庫中獲取用戶
                user = FirebaseUser.objects.get(firebase_uid=firebase_uid)
                request.firebase_user = user
            except FirebaseUser.DoesNotExist:
                request.firebase_user = None
                # 清除 session 中的用戶資訊
                if 'firebase_uid' in request.session:
                    del request.session['firebase_uid']
                if 'firebase_user_email' in request.session:
                    del request.session['firebase_user_email']
                if 'firebase_user_name' in request.session:
                    del request.session['firebase_user_name']
        else:
            # 從請求頭中獲取 ID Token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
                # 驗證 ID Token
                decoded_token = FirebaseAuth.verify_id_token(id_token)
                if decoded_token:
                    uid = decoded_token.get('uid')
                    # 獲取或創建用戶
                    user, created = FirebaseUser.objects.get_or_create(
                        firebase_uid=uid,
                        defaults={
                            'email': decoded_token.get('email', ''),
                            'display_name': decoded_token.get('name', '')
                        }
                    )
                    # 如果用戶已存在但資訊有更新，則更新用戶資訊
                    if not created:
                        update_fields = []
                        if decoded_token.get('email') and user.email != decoded_token.get('email'):
                            user.email = decoded_token.get('email')
                            update_fields.append('email')
                        if decoded_token.get('name') and user.display_name != decoded_token.get('name'):
                            user.display_name = decoded_token.get('name')
                            update_fields.append('display_name')
                        if update_fields:
                            user.save(update_fields=update_fields)
                    
                    # 將用戶添加到請求中
                    request.firebase_user = user
                    
                    # 將用戶資訊存儲在 session 中
                    request.session['firebase_uid'] = uid
                    request.session['firebase_user_email'] = user.email
                    request.session['firebase_user_name'] = user.display_name
                else:
                    request.firebase_user = None
            else:
                request.firebase_user = None
        
        response = self.get_response(request)
        return response
```

#### 2.5 實現登入裝飾器

在 `decorators.py` 中實現 `login_required` 裝飾器：

```python
from functools import wraps
from django.shortcuts import redirect

def login_required(view_func):
    """檢查用戶是否已登入的裝飾器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 檢查 session 中是否有用戶資訊
        if 'firebase_uid' not in request.session:
            # 重定向到登入頁面
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
```

### 3. Firebase Firestore 整合

#### 3.1 實現 FirebasePTTManager 類

在 `firebase_ptt.py` 中實現 PTT 文章管理功能：

```python
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
                cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')
                cred = credentials.Certificate(cred_path)
                app = firebase_admin.initialize_app(cred, name='ptt_app')
                self.db = firestore.client(app=app)
            
            self.collection_ref = self.db.collection(collection)
            FirebasePTTManager._initialized = True
        else:
            # 如果已經初始化，使用現有的應用
            try:
                app = firebase_admin.get_app(name='ptt_app')
            except ValueError:
                app = firebase_admin.get_app()
            self.db = firestore.client(app=app)
            self.collection_ref = self.db.collection(collection)
    
    def get_posts(self, limit=10, keyword=None):
        """獲取 PTT 股票版文章列表"""
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
            
            return post_data
        except Exception as e:
            print(f"獲取文章詳情時出錯: {e}")
            return None
```

### 4. Firebase Storage 整合

#### 4.1 實現 FirebaseStorageManager 類

在 `firebase_storage.py` 中實現重大訊息圖片管理功能：

```python
import os
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
from django.conf import settings

class FirebaseStorageManager:
    """Firebase Storage 管理類，用於上傳和獲取 MOPS 重大訊息圖片"""
    
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """獲取單例實例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化 Firebase Storage"""
        if not FirebaseStorageManager._initialized:
            # 檢查 Firebase 是否已初始化
            try:
                # 嘗試獲取已存在的 Firebase 應用
                app = firebase_admin.get_app()
                self.bucket = storage.bucket(app=app)
            except ValueError:
                # 如果未初始化，則初始化 Firebase
                cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')
                cred = credentials.Certificate(cred_path)
                app = firebase_admin.initialize_app(cred, {
                    'storageBucket': 'your-project-id.appspot.com'
                }, name='storage_app')
                self.bucket = storage.bucket(app=app)
            
            FirebaseStorageManager._initialized = True
        else:
            # 如果已經初始化，使用現有的應用
            try:
                app = firebase_admin.get_app(name='storage_app')
            except ValueError:
                app = firebase_admin.get_app()
            self.bucket = storage.bucket(app=app)
    
    def upload_image(self, image_path, storage_path):
        """上傳圖片到 Firebase Storage"""
        try:
            # 加入 mops_images 前綴到儲存路徑
            blob = self.bucket.blob(f"mops_images/{storage_path}")
            blob.upload_from_filename(image_path)
            blob.make_public()
            
            print(f"成功上傳圖片: {blob.public_url}")
            return blob.public_url
        
        except Exception as e:
            print(f"上傳失敗: {e}")
            return None
    
    def get_news_images(self, stock_id=None, limit=10):
        """獲取 MOPS 重大訊息圖片列表"""
        try:
            prefix = f"mops_images/{stock_id}/" if stock_id else "mops_images/"
            blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=limit))
            
            result = []
            for blob in blobs:
                # 從路徑解析股票代碼和時間
                # 路徑格式: mops_images/2330/20231105_133803
                path_parts = blob.name.replace('mops_images/', '').split('/')
                if len(path_parts) >= 2:
                    stock_id = path_parts[0]
                    date_time = path_parts[1].split('_')
                    
                    if len(date_time) >= 2:
                        # 將日期格式化為 YYYY/MM/DD
                        date_str = date_time[0]
                        if len(date_str) == 8:  # YYYYMMDD
                            date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"
                        else:
                            date = date_str
                        
                        # 將時間格式化為 HH:MM:SS
                        time_str = date_time[1]
                        if len(time_str) == 6:  # HHMMSS
                            time_formatted = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                        else:
                            time_formatted = time_str
                        
                        result.append({
                            'url': blob.public_url,
                            'stock_id': stock_id,
                            'date': date,
                            'time': time_formatted
                        })
            
            return result
        
        except Exception as e:
            print(f"獲取圖片列表失敗: {e}")
            return []
```

### 5. 避免 Firebase 多次初始化問題

在整合 Firebase 時，一個常見的問題是多次初始化 Firebase 應用，這會導致錯誤。為了避免這個問題，我們使用了以下策略：

1. 使用單例模式確保每個管理類只有一個實例
2. 使用類變量 `_initialized` 跟踪初始化狀態
3. 在初始化前檢查 Firebase 應用是否已存在
4. 為不同的服務使用不同的應用名稱

這些策略確保了 Firebase 服務在整個應用中只被初始化一次，避免了重複初始化的錯誤。 