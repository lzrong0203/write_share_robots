# 視圖實現 5：PTT 文章視圖

本節將介紹如何實現 PTT 文章相關的視圖功能，包括文章列表視圖和文章詳情視圖。這些視圖允許用戶瀏覽從 PTT 股票版爬取並存儲在 Firebase 中的文章。

## 1. PTT 文章視圖概述

PTT 文章功能包含兩個主要視圖：
- **文章列表視圖**：顯示 PTT 股票版文章列表，支持關鍵字搜索
- **文章詳情視圖**：顯示單篇文章的詳細內容，包括推文

這些視圖與 Firebase Firestore 數據庫交互，從中獲取文章數據。

## 2. 實現 PTT 文章列表視圖

PTT 文章列表視圖負責從 Firebase Firestore 獲取文章列表，並支持關鍵字搜索功能。

### 視圖函數實現

在 `views.py` 中實現 `ptt_posts_view` 函數：

```python
def ptt_posts_view(request):
    """顯示 PTT 股票版文章列表"""
    keyword = request.GET.get('keyword', '')
    
    # 獲取 PTT 文章列表
    ptt_manager = FirebasePTTManager.get_instance()
    posts = ptt_manager.get_posts(limit=20, keyword=keyword)
    
    # 檢查文章是否有內容
    valid_posts = []
    for post in posts:
        if post.get('content') and len(post.get('content').strip()) > 0:
            valid_posts.append(post)
    
    context = {
        'posts': valid_posts,
        'keyword': keyword,
        'firebase_api_key': FIREBASE_CONFIG['apiKey'],
        'firebase_auth_domain': FIREBASE_CONFIG['authDomain'],
        'firebase_project_id': FIREBASE_CONFIG['projectId'],
        'firebase_storage_bucket': FIREBASE_CONFIG['storageBucket'],
        'firebase_messaging_sender_id': FIREBASE_CONFIG['messagingSenderId'],
        'firebase_app_id': FIREBASE_CONFIG['appId'],
    }
    
    return render(request, 'stock_app/ptt_posts.html', context)
```

這個視圖函數執行以下操作：
1. 獲取用戶輸入的關鍵字（如果有）
2. 使用 `FirebasePTTManager` 從 Firebase Firestore 獲取文章列表
3. 過濾掉沒有內容的文章
4. 將文章列表和 Firebase 配置傳遞給模板

### URL 配置

在 `urls.py` 中添加 PTT 文章列表的 URL 路由：

```python
path('ptt_posts/', views.ptt_posts_view, name='ptt_posts'),
```

## 3. 實現 PTT 文章詳情視圖

PTT 文章詳情視圖負責顯示單篇文章的詳細內容，包括推文。

### 視圖函數實現

在 `views.py` 中實現 `ptt_post_detail_view` 函數：

```python
def ptt_post_detail_view(request, post_id):
    """顯示 PTT 文章詳情"""
    ptt_manager = FirebasePTTManager.get_instance()
    post = ptt_manager.get_post_by_id(post_id)
    
    if not post:
        messages.error(request, f"找不到 ID 為 {post_id} 的文章")
        return redirect('ptt_posts')
    
    # 確保推文列表存在
    if 'pushes' not in post:
        post['pushes'] = []
    
    context = {
        'post': post,
        'firebase_api_key': FIREBASE_CONFIG['apiKey'],
        'firebase_auth_domain': FIREBASE_CONFIG['authDomain'],
        'firebase_project_id': FIREBASE_CONFIG['projectId'],
        'firebase_storage_bucket': FIREBASE_CONFIG['storageBucket'],
        'firebase_messaging_sender_id': FIREBASE_CONFIG['messagingSenderId'],
        'firebase_app_id': FIREBASE_CONFIG['appId'],
    }
    
    return render(request, 'stock_app/ptt_post_detail.html', context)
```

這個視圖函數執行以下操作：
1. 使用 `FirebasePTTManager` 從 Firebase Firestore 獲取指定 ID 的文章
2. 如果文章不存在，顯示錯誤消息並重定向到文章列表頁面
3. 確保文章包含推文列表（即使為空）
4. 將文章數據和 Firebase 配置傳遞給模板

### URL 配置

在 `urls.py` 中添加 PTT 文章詳情的 URL 路由：

```python
path('ptt_posts/<str:post_id>/', views.ptt_post_detail_view, name='ptt_post_detail'),
```

## 4. Firebase PTT 管理

PTT 文章視圖依賴於 `FirebasePTTManager` 類來與 Firebase Firestore 交互。這個類在 `firebase_ptt.py` 中實現：

```python
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
        # 初始化 Firebase 連接
        # ...
        
    def get_posts(self, limit=10, keyword=None):
        """獲取 PTT 股票版文章列表"""
        # 從 Firestore 獲取文章列表
        # 如果提供了關鍵字，則進行過濾
        # ...
        
    def get_post_by_id(self, post_id):
        """根據 ID 獲取 PTT 文章"""
        # 從 Firestore 獲取指定 ID 的文章
        # ...
```

`FirebasePTTManager` 類使用單例模式，確保整個應用中只有一個實例，負責從 Firestore 獲取 PTT 文章。

## 5. PTT 爬蟲功能

PTT 文章數據通過爬蟲獲取並存儲到 Firebase Firestore。爬蟲功能在 `ptt_crawler.py` 中實現，並通過 Django 管理命令 `crawl_ptt.py` 執行。

### 爬蟲類實現

```python
class PTTCrawler:
    """PTT 股票版爬蟲類"""
    
    PTT_URL = 'https://www.ptt.cc'
    STOCK_BOARD = '/bbs/Stock'
    
    def __init__(self):
        # 初始化爬蟲
        # ...
        
    def get_latest_posts(self, pages=1):
        """獲取最新的文章列表"""
        # 爬取 PTT 股票版最新文章
        # ...
        
    def get_post_content(self, post_url):
        """獲取文章內容"""
        # 爬取文章詳細內容
        # ...
        
    def crawl_and_upload(self, pages=1):
        """爬取並上傳文章到 Firebase"""
        # 爬取文章並上傳到 Firestore
        # ...
```

### 管理命令實現

在 `management/commands/crawl_ptt.py` 中實現爬蟲管理命令：

```python
class Command(BaseCommand):
    help = 'Crawl PTT Stock board posts and upload to Firebase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Number of pages to crawl'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        self.stdout.write(self.style.SUCCESS(f'Starting to crawl {pages} page(s) from PTT Stock board...'))
        
        try:
            uploaded_count = crawl_ptt_stock(pages)
            self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {uploaded_count} posts to Firebase'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
```

執行爬蟲命令：

```bash
python manage.py crawl_ptt --pages 3
```

## 6. 總結

PTT 文章視圖功能允許用戶瀏覽從 PTT 股票版爬取的文章，支持關鍵字搜索和查看文章詳情。這些功能通過以下組件實現：

1. **視圖函數**：`ptt_posts_view` 和 `ptt_post_detail_view`
2. **URL 路由**：配置在 `urls.py` 中
3. **Firebase 管理**：`FirebasePTTManager` 類負責與 Firestore 交互
4. **爬蟲功能**：`PTTCrawler` 類和 `crawl_ptt` 管理命令負責獲取和上傳文章

通過這些組件的協同工作，用戶可以方便地瀏覽 PTT 股票版的最新討論，獲取投資決策所需的信息。 