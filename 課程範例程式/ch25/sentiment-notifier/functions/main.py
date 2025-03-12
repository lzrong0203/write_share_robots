# # Welcome to Cloud Functions for Firebase for Python!
# # To get started, simply uncomment the below code or create your own.
# # Deploy with `firebase deploy`
#
# from firebase_functions import db_fn, https_fn
# from firebase_admin import initialize_app, messaging
# import firebase_admin
# import logging
# import requests
#
# # 初始化 Firebase 應用
# initialize_app()
#
# # 設置日誌
# logger = logging.getLogger('sentiment_monitor')
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)
#
#
# @db_fn.on_value_created(
#     reference="/sentiment_analysis/stock_indices/{push_id}",
#     region="asia-southeast1"
# )
# def monitor_sentiment_index(event: db_fn.Event) -> None:
#     """監控情緒分析指數，當超出閾值時發送通知"""
#     try:
#         # 從 event.params 中獲取 push_id
#         push_id = event.params.get('push_id')
#         logger.info(f"監控到新的情緒分析數據，ID: {push_id}")
#
#         # 獲取新數據
#         sentiment_data = event.data
#         logger.info(f"收到新的情緒分析數據: {sentiment_data}")
#
#         # 檢查數據是否有效
#         if not sentiment_data or not isinstance(sentiment_data, dict):
#             logger.warning(f"無效的數據格式: {sentiment_data}")
#             return
#
#         # 提取情緒指數和股票代號
#         sentiment_value = sentiment_data.get('value')
#         stock_id = sentiment_data.get('stock_id')
#
#         # 檢查是否有必要的字段
#         if sentiment_value is None or stock_id is None:
#             logger.warning(f"數據缺少必要字段: {sentiment_data}")
#             return
#
#         # 檢查情緒指數是否超出閾值
#         if abs(float(sentiment_value)) <= 0.2:
#             logger.info(f"情緒指數在閾值範圍內: {sentiment_value}")
#             return
#
#         # 生成通知消息
#         if float(sentiment_value) > 0.2:
#             title = f"{stock_id} 情緒指數上升"
#             body = f"{stock_id} 情緒指數上升至 {float(sentiment_value):.2f}，可能是利多消息"
#             level = "positive"
#         else:
#             title = f"{stock_id} 情緒指數下降"
#             body = f"{stock_id} 情緒指數下降至 {float(sentiment_value):.2f}，可能是利空消息"
#             level = "negative"
#
#         logger.info(f"準備發送通知: {title} - {body}")
#
#         # 創建消息
#         message = messaging.Message(
#             topic='sentiment_alerts',
#             notification=messaging.Notification(
#                 title=title,
#                 body=body
#             ),
#             data={
#                 'stock_id': stock_id,
#                 'sentiment_value': str(sentiment_value),
#                 'level': level,
#                 'timestamp': str(sentiment_data.get('timestamp', 0))
#             }
#         )
#
#         # 發送消息
#         response = messaging.send(message)
#         logger.info(f"通知發送成功: {response}")
#
#         line_token = '78WbRd+SY+o7uX6RMwG0WTiVRaxmb4RIt3BtlxgCPUj23wv8RZA+UZiZ8iEUcy8GyvY9KrLpcZ5iN3EqJplMI0my0kciK73pUTrh4AML3DOqN8qR7gVMK6ry42z0YLcy0YY+2WJNT1auFdAJo2NjggdB04t89/1O/w1cDnyilFU='
#         to_user = 'U48b87214dbc58cc2a4ae08bfea16233c'  # 改為接收消息的用户 ID
#         message_line = {
#             "to": to_user,
#             "messages": [
#                 {
#                     "type": "text",
#                     "text": f"{body}"
#                 }
#             ]
#         }
#
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {line_token}'
#         }
#
#         response = requests.post('https://api.line.me/v2/bot/message/push', json=message_line, headers=headers)
#         if response.status_code != 200:
#             logger.info(f"Error sending to LINE: {response.text}")
#         else:
#             logger.info("Successfully sent message to LINE")
#
#     except Exception as e:
#         logger.error(f"監控情緒指數時出錯: {str(e)}")
#
#
# # 添加一個簡單的 HTTP 函數用於測試
# @https_fn.on_request()
# def hello_world(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello from Firebase Cloud Functions (Python)!")




# Welcome to Cloud Functions for Firebase for Python!
from firebase_functions import db_fn, https_fn
from firebase_admin import initialize_app, messaging
import firebase_admin
import logging
import requests
import json
import hashlib
import hmac
import base64

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

# LINE API 相關設定
LINE_CHANNEL_SECRET = 'a4de0bb469b2cb767281a3dd910d1032'  # 替換為您的頻道密鑰
LINE_CHANNEL_ACCESS_TOKEN = '78WbRd+SY+o7uX6RMwG0WTiVRaxmb4RIt3BtlxgCPUj23wv8RZA+UZiZ8iEUcy8GyvY9KrLpcZ5iN3EqJplMI0my0kciK73pUTrh4AML3DOqN8qR7gVMK6ry42z0YLcy0YY+2WJNT1auFdAJo2NjggdB04t89/1O/w1cDnyilFU='


# 用於監控情緒分析的資料庫函數 (保持不變)
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

        # 發送 LINE 推送訊息
        to_user = 'U48b87214dbc58cc2a4ae08bfea16233c'  # 改為接收消息的用户 ID
        send_line_push_message(to_user, body)

    except Exception as e:
        logger.error(f"監控情緒指數時出錯: {str(e)}")


# 新增的 LINE 推送訊息函數
def send_line_push_message(user_id, text):
    """發送 LINE 推送訊息"""
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logger.error(f"LINE 推送訊息失敗: {response.text}")
    else:
        logger.info("LINE 推送訊息成功")
    return response


# 新增 LINE Webhook 處理函數
@https_fn.on_request()
def line_webhook(req: https_fn.Request) -> https_fn.Response:
    """
    LINE Webhook 處理函數
    負責驗證和處理來自 LINE 的 Webhook 請求
    """
    # 僅接受 POST 請求
    if req.method != 'POST':
        return https_fn.Response("Method Not Allowed", status=405)

    # 獲取 X-Line-Signature 頭信息
    signature = req.headers.get('X-Line-Signature', '')
    if not signature:
        logger.error("缺少 X-Line-Signature")
        return https_fn.Response("Bad Request: Missing X-Line-Signature", status=400)

    # 獲取請求體
    body = req.data.decode('utf-8')

    # 驗證簽名
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()

    calculated_signature = base64.b64encode(hash).decode('utf-8')
    if calculated_signature != signature:
        logger.error("簽名驗證失敗")
        return https_fn.Response("Bad Request: Invalid signature", status=400)

    # 處理 Webhook 事件
    try:
        events = json.loads(body).get('events', [])
        for event in events:
            handle_line_event(event)

        return https_fn.Response("OK", status=200)
    except Exception as e:
        logger.error(f"處理 LINE Webhook 時出錯: {str(e)}")
        return https_fn.Response(f"Internal Server Error: {str(e)}", status=500)


def handle_line_event(event):
    """處理 LINE 事件"""
    event_type = event.get('type')

    # 獲取回覆令牌和用戶ID
    reply_token = event.get('replyToken')
    user_id = event.get('source', {}).get('userId')

    logger.info(f"收到 LINE 事件: {event_type} 來自用戶: {user_id}")

    # 處理文字消息
    if event_type == 'message':
        message = event.get('message', {})
        message_type = message.get('type')

        if message_type == 'text':
            text = message.get('text', '')
            logger.info(f"收到文字消息: {text}")

            # 簡單的命令處理
            if text.startswith('/'):
                handle_command(reply_token, user_id, text)
            else:
                # 一般消息回覆
                send_line_reply(reply_token, f"收到您的訊息: {text}")

    # 處理追蹤/取消追蹤事件
    elif event_type == 'follow':
        send_line_reply(reply_token, "感謝您追蹤我們的機器人！您將會收到股票情緒指數的即時通知。")

    elif event_type == 'unfollow':
        logger.info(f"用戶 {user_id} 取消追蹤")


def handle_command(reply_token, user_id, command):
    """處理命令"""
    command = command.lower()

    if command.startswith('/help'):
        message = (
            "股票情緒監控 Bot 指令列表：\n"
            "/subscribe - 訂閱通知\n"
            "/status - 查看系統狀態\n"
            "/help - 顯示此幫助訊息"
        )
        send_line_reply(reply_token, message)

    elif command.startswith('/subscribe'):
        # 這裡可以實現訂閱邏輯，例如將用戶ID保存到資料庫
        send_line_reply(reply_token, "您已成功訂閱通知！")

    elif command.startswith('/status'):
        send_line_reply(reply_token, "系統運作正常，正在監控股票情緒指數。")

    else:
        send_line_reply(reply_token, f"未知命令: {command}。輸入 /help 查看可用命令。")


def send_line_reply(reply_token, text):
    """發送 LINE 回覆訊息"""
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logger.error(f"LINE 回覆訊息失敗: {response.text}")
    else:
        logger.info("LINE 回覆訊息成功")
    return response


# 測試用的 HTTP 函數
@https_fn.on_request()
def hello_world(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello from Firebase Cloud Functions (Python) with LINE Webhook integration!", status=200)