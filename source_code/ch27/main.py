# Example of cloud function deploy
from firebase_functions import db_fn, https_fn
from firebase_admin import initialize_app, messaging
import firebase_admin
import logging
import requests

# 初始化 Firebase 應用
initialize_app()

# 設置日誌
logger = logging.getLogger('sentiment_monitor')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@db_fn.on_value_created(
    reference="/sentiment_analysis/stock_indices/{push_id}",
    region="asia-southeast1"
)
def monitor_sentiment_index(event: db_fn.Event) -> None:
    """監控情緒分析指數，當超出閾值時發送通知"""
    try:
        # 從 event.params 中獲取 push_id
        push_id = event.params.get('push_id')
        logger.info(f"監控到新的情緒分析數據，ID: {push_id}")

        # 獲取新數據
        sentiment_data = event.data
        logger.info(f"收到新的情緒分析數據: {sentiment_data}")

        # 檢查數據是否有效
        if not sentiment_data or not isinstance(sentiment_data, dict):
            logger.warning(f"無效的數據格式: {sentiment_data}")
            return

        # 提取情緒指數和股票代號
        sentiment_value = sentiment_data.get('value')
        stock_id = sentiment_data.get('stock_id')

        # 檢查是否有必要的字段
        if sentiment_value is None or stock_id is None:
            logger.warning(f"數據缺少必要字段: {sentiment_data}")
            return

        # 檢查情緒指數是否超出閾值
        if abs(float(sentiment_value)) <= 0.2:
            logger.info(f"情緒指數在閾值範圍內: {sentiment_value}")
            return

        # 生成通知消息
        if float(sentiment_value) > 0.2:
            title = f"{stock_id} 情緒指數上升"
            body = f"{stock_id} 情緒指數上升至 {float(sentiment_value):.2f}，可能是利多消息"
            level = "positive"
        else:
            title = f"{stock_id} 情緒指數下降"
            body = f"{stock_id} 情緒指數下降至 {float(sentiment_value):.2f}，可能是利空消息"
            level = "negative"

        logger.info(f"準備發送通知: {title} - {body}")

        # 創建消息
        message = messaging.Message(
            topic='sentiment_alerts',
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'stock_id': stock_id,
                'sentiment_value': str(sentiment_value),
                'level': level,
                'timestamp': str(sentiment_data.get('timestamp', 0))
            }
        )

        # 發送消息
        response = messaging.send(message)
        logger.info(f"通知發送成功: {response}")

        line_token = '78WbRd+SY+o7uX6RMwG0WTiVRaxmb4RIt3BtlxgCPUj23wv8RZA+UZiZ8iEUcy8GyvY9KrLpcZ5iN3EqJplMI0my0kciK73pUTrh4AML3DOqN8qR7gVMK6ry42z0YLcy0YY+2WJNT1auFdAJo2NjggdB04t89/1O/w1cDnyilFU='
        to_user = 'U48b87214dbc58cc2a4ae08bfea16233c'  # 改為接收消息的用户 ID
        message_line = {
            "to": to_user,
            "messages": [
                {
                    "type": "text",
                    "text": f"{body}"
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {line_token}'
        }

        response = requests.post('https://api.line.me/v2/bot/message/push', json=message_line, headers=headers)
        if response.status_code != 200:
            logger.info(f"Error sending to LINE: {response.text}")
        else:
            logger.info("Successfully sent message to LINE")

    except Exception as e:
        logger.error(f"監控情緒指數時出錯: {str(e)}")


# 添加一個簡單的 HTTP 函數用於測試
@https_fn.on_request()
def hello_world(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello from Firebase Cloud Functions (Python)!")