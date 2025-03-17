import firebase_admin
from firebase_admin import credentials, storage
import os
import logging

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

class FirebaseStorageClient:
    """Firebase Storage 客戶端"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """單例模式獲取實例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化 Firebase Storage 連接"""
        try:
            # 檢查 Firebase 是否已初始化
            if not firebase_admin._apps:
                # 獲取專案根目錄的絕對路徑
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # 憑證文件的路徑
                cred_path = os.path.join(base_dir, "stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
                
                # 初始化 Firebase
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'stocksentiment-8cf69.firebasestorage.app',
                    'databaseURL': 'https://stocksentiment-8cf69-default-rtdb.asia-southeast1.firebasedatabase.app/'
                })
            
            # 獲取 Storage bucket
            self.bucket = storage.bucket()
            logger.info("Firebase Storage 初始化成功")
        except Exception as e:
            logger.error(f"Firebase Storage 初始化失敗: {str(e)}")
            raise
    
    def list_stock_folders(self):
        """
        獲取所有股票代號文件夾
        
        Returns:
            list: 股票代號列表
        """
        try:
            # 列出 mops_images 目錄下的所有文件夾
            blobs = self.bucket.list_blobs(prefix='mops_images/')
            
            # 提取股票代號
            stock_ids = set()
            for blob in blobs:
                # 從路徑中提取股票代號
                # 格式: mops_images/股票代號/日期_時間
                parts = blob.name.split('/')
                if len(parts) >= 3:
                    stock_ids.add(parts[1])
            
            return sorted(list(stock_ids))
        except Exception as e:
            logger.error(f"獲取股票代號列表失敗: {str(e)}")
            raise
    
    def list_stock_news(self, stock_id):
        """
        獲取特定股票的所有重大訊息
        
        Args:
            stock_id: 股票代號
            
        Returns:
            list: 重大訊息列表，每個元素包含 URL 和日期時間
        """
        try:
            # 列出特定股票目錄下的所有圖片
            blobs = self.bucket.list_blobs(prefix=f'mops_images/{stock_id}/')
            
            news_list = []
            for blob in blobs:
                # 從路徑中提取日期和時間
                # 格式: mops_images/股票代號/日期_時間
                parts = blob.name.split('/')
                if len(parts) >= 3:
                    date_time = parts[2]
                    
                    # 格式化日期時間
                    if '_' in date_time:
                        date, time = date_time.split('_')
                        formatted_date = f"{date[:3]}/{date[3:5]}/{date[5:]}"
                        formatted_time = f"{time[:2]}:{time[2:4]}:{time[4:]}" if len(time) >= 6 else time
                        display_date = f"{formatted_date} {formatted_time}"
                    else:
                        display_date = date_time
                    
                    # 獲取公開 URL
                    url = blob.public_url
                    
                    news_list.append({
                        'url': url,
                        'date_time': date_time,
                        'display_date': display_date,
                        'blob_name': blob.name
                    })
            
            # 按日期時間降序排序
            news_list.sort(key=lambda x: x['date_time'], reverse=True)
            
            return news_list
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 的重大訊息列表失敗: {str(e)}")
            raise
    
    def get_news_url(self, stock_id, date_time):
        """
        獲取特定重大訊息的 URL
        
        Args:
            stock_id: 股票代號
            date_time: 日期時間
            
        Returns:
            str: 圖片 URL
        """
        try:
            # 構建 blob 路徑
            blob_path = f'mops_images/{stock_id}/{date_time}'
            blob = self.bucket.blob(blob_path)
            
            # 檢查 blob 是否存在
            if blob.exists():
                return blob.public_url
            else:
                logger.warning(f"找不到圖片: {blob_path}")
                return None
        except Exception as e:
            logger.error(f"獲取圖片 URL 失敗: {str(e)}")
            raise 