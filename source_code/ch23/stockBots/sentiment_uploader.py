import firebase_admin
from firebase_admin import credentials, db
import os
import random
import time
from datetime import datetime
import argparse

class SentimentUploader:
    """情緒分析指數上傳器"""
    
    def __init__(self):
        """初始化 Firebase 連接"""
        # 獲取專案根目錄的絕對路徑
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 憑證文件的路徑
        cred_path = os.path.join(base_dir, "stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
        
        # 初始化 Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://stocksentiment-8cf69-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
        
        # 獲取情緒分析的參考路徑
        self.ref = db.reference('sentiment_analysis/stock_indices')
        print("Firebase 連接初始化成功")
    
    def upload_sentiment(self, stock_id, sentiment_value, source="news"):
        """
        上傳情緒分析指數
        
        Args:
            stock_id: 股票代號
            sentiment_value: 情緒分析指數 (-1.0 到 1.0 之間)
            source: 數據來源 (news, social_media, etc.)
        
        Returns:
            bool: 是否成功
        """
        try:
            # 生成時間戳
            timestamp = int(time.time() * 1000)  # 毫秒級時間戳
            
            # 準備數據
            data = {
                'value': sentiment_value,
                'stock_id': stock_id,
                'source': source,
                'timestamp': timestamp,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 上傳數據
            self.ref.child(str(timestamp)).set(data)
            
            print(f"成功上傳 {stock_id} 的情緒分析指數: {sentiment_value}")
            return True
        except Exception as e:
            print(f"上傳情緒分析指數失敗: {str(e)}")
            return False
    
    def generate_random_sentiment(self, stock_id, source="random_generator"):
        """
        生成隨機情緒分析指數並上傳
        
        Args:
            stock_id: 股票代號
            source: 數據來源
        
        Returns:
            float: 生成的情緒分析指數
        """
        # 生成 -1.0 到 1.0 之間的隨機值
        sentiment_value = round(random.uniform(-1.0, 1.0), 2)
        
        # 上傳數據
        self.upload_sentiment(stock_id, sentiment_value, source)
        
        return sentiment_value
    
    def generate_threshold_sentiment(self, stock_id, source="threshold_test"):
        """
        生成超出閾值的情緒分析指數並上傳
        
        Args:
            stock_id: 股票代號
            source: 數據來源
        
        Returns:
            float: 生成的情緒分析指數
        """
        # 生成超出閾值的隨機值 (大於 0.2 或小於 -0.2)
        if random.choice([True, False]):
            # 正面情緒 (0.2 到 1.0)
            sentiment_value = round(random.uniform(0.2, 1.0), 2)
        else:
            # 負面情緒 (-1.0 到 -0.2)
            sentiment_value = round(random.uniform(-1.0, -0.2), 2)
        
        # 上傳數據
        self.upload_sentiment(stock_id, sentiment_value, source)
        
        return sentiment_value

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='上傳情緒分析指數到 Firebase Realtime Database')
    parser.add_argument('--stock', type=str, default='2330', help='股票代號')
    parser.add_argument('--value', type=float, help='情緒分析指數 (-1.0 到 1.0 之間)')
    parser.add_argument('--source', type=str, default='manual', help='數據來源')
    parser.add_argument('--random', action='store_true', help='生成隨機情緒分析指數')
    parser.add_argument('--threshold', action='store_true', help='生成超出閾值的情緒分析指數')
    parser.add_argument('--count', type=int, default=1, help='生成數據的數量')
    parser.add_argument('--interval', type=float, default=1.0, help='生成數據的間隔時間 (秒)')
    
    args = parser.parse_args()
    
    # 初始化上傳器
    uploader = SentimentUploader()
    
    # 根據參數執行不同操作
    for i in range(args.count):
        if args.threshold:
            # 生成超出閾值的情緒分析指數
            sentiment_value = uploader.generate_threshold_sentiment(args.stock, args.source)
            print(f"生成超出閾值的情緒分析指數: {sentiment_value}")
        elif args.random:
            # 生成隨機情緒分析指數
            sentiment_value = uploader.generate_random_sentiment(args.stock, args.source)
            print(f"生成隨機情緒分析指數: {sentiment_value}")
        elif args.value is not None:
            # 上傳指定的情緒分析指數
            uploader.upload_sentiment(args.stock, args.value, args.source)
        else:
            print("請指定情緒分析指數或使用 --random 或 --threshold 參數")
            return
        
        # 如果需要生成多個數據，則等待指定的間隔時間
        if args.count > 1 and i < args.count - 1:
            time.sleep(args.interval)

if __name__ == "__main__":
    main() 