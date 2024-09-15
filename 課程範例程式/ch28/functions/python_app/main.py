import os
import json
from google.cloud import firestore
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import logging

# 設置日誌級別
logging.basicConfig(level=logging.INFO)

# 獲取 LINE 的 Channel Access Token 和 Channel Secret
line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_channel_secret = os.getenv('LINE_CHANNEL_SECRET')

# 初始化 Firestore
db = firestore.Client()

# 初始化 Line Bot
line_bot_api = LineBotApi(line_channel_access_token)

def check_conditions_and_notify():
    try:
        # 查询 Firestore 中的条件
        users_ref = db.collection('users')
        docs = users_ref.stream()

        for doc in docs:
            user_data = doc.to_dict()
            # 这里简单地判断用户是否满足某个条件，例如年龄大于20
            if user_data.get('age', 0) > 20:
                # 触发 Line Bot 消息
                user_id = user_data.get('line_user_id')
                if user_id:
                    message = f"Hello {user_data.get('name')}, you have a new notification!"
                    send_line_message(user_id, message)
    except Exception as e:
        logging.error(f"Error checking conditions and notifying: {e}")

def send_line_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        logging.info(f"Message sent to {user_id}")
    except Exception as e:
        logging.error(f"Failed to send message to {user_id}: {e}")

if __name__ == "__main__":
    check_conditions_and_notify()

