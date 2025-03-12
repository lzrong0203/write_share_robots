"""
直接使用 FCM API 發送通知的腳本
"""
import firebase_admin
from firebase_admin import credentials, messaging
import os
import argparse
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class FCMNotifier:
    """FCM 通知發送器"""
    
    def __init__(self):
        """初始化 Firebase Admin SDK"""
        # 獲取專案根目錄的絕對路徑
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 憑證文件的路徑
        cred_path = os.path.join(base_dir, "stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
        
        # 初始化 Firebase Admin SDK (如果尚未初始化)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        print("Firebase Admin SDK 初始化成功")
    
    def send_to_token(self, token, title, body, data=None):
        """
        向特定設備令牌發送通知
        
        Args:
            token: FCM 設備令牌
            title: 通知標題
            body: 通知內容
            data: 附加數據 (字典)
        
        Returns:
            bool: 是否成功
        """
        try:
            # 準備消息
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            
            # 發送消息
            response = messaging.send(message)
            print(f"成功發送通知: {response}")
            return True
        except Exception as e:
            print(f"發送通知失敗: {str(e)}")
            return False
    
    def send_to_topic(self, topic, title, body, data=None):
        """
        向特定主題發送通知
        
        Args:
            topic: 主題名稱
            title: 通知標題
            body: 通知內容
            data: 附加數據 (字典)
        
        Returns:
            bool: 是否成功
        """
        try:
            # 準備消息
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )
            
            # 發送消息
            response = messaging.send(message)
            print(f"成功發送主題通知: {response}")
            return True
        except Exception as e:
            print(f"發送主題通知失敗: {str(e)}")
            return False
    
    def subscribe_to_topic(self, token, topic):
        """
        訂閱主題
        
        Args:
            token: FCM 設備令牌
            topic: 主題名稱
        
        Returns:
            bool: 是否成功
        """
        try:
            # 訂閱主題
            response = messaging.subscribe_to_topic(token, topic)
            print(f"成功訂閱主題: {response.success_count} 成功, {response.failure_count} 失敗")
            return response.success_count > 0
        except Exception as e:
            print(f"訂閱主題失敗: {str(e)}")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='使用 FCM API 發送通知')
    parser.add_argument('--token', type=str, help='FCM 設備令牌')
    parser.add_argument('--topic', type=str, help='FCM 主題名稱')
    parser.add_argument('--title', type=str, default='情緒分析通知', help='通知標題')
    parser.add_argument('--body', type=str, default='收到新的情緒分析數據', help='通知內容')
    parser.add_argument('--stock', type=str, default='2330', help='股票代號')
    parser.add_argument('--value', type=str, default='0.5', help='情緒分析指數')
    parser.add_argument('--subscribe', action='store_true', help='訂閱主題')
    
    args = parser.parse_args()
    
    # 初始化通知發送器
    notifier = FCMNotifier()
    
    # 準備附加數據
    data = {
        'stock_id': args.stock,
        'sentiment_value': args.value,
        'source': 'direct_test'
    }
    
    # 根據參數執行不同操作
    if args.subscribe and args.token and args.topic:
        # 訂閱主題
        notifier.subscribe_to_topic(args.token, args.topic)
    elif args.token:
        # 向特定設備發送通知
        notifier.send_to_token(args.token, args.title, args.body, data)
    elif args.topic:
        # 向主題發送通知
        notifier.send_to_topic(args.topic, args.title, args.body, data)
    else:
        print("請指定 FCM 設備令牌或主題名稱")

if __name__ == "__main__":
    main() 