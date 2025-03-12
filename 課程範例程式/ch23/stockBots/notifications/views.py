from django.shortcuts import render
import os
import json
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import firebase_admin
from firebase_admin import credentials, messaging

# 確保環境變數已載入
load_dotenv()

def notification_page(request):
    """顯示通知頁面"""
    # 從 .env 讀取 Firebase 配置
    firebase_config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID'),
        'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
        'serverKey': os.environ.get('FIREBASE_SERVER_KEY'),
        'vapidKey': os.environ.get('FIREBASE_VAPID_KEY'),
    }
    
    return render(request, 'notifications/notification_page.html', {
        'firebase_config': firebase_config
    })

@csrf_exempt
@require_POST
def subscribe_topic(request):
    """訂閱主題 API 端點"""
    try:
        # 解析請求數據
        data = json.loads(request.body)
        token = data.get('token')
        topic = data.get('topic')
        
        # 驗證參數
        if not token or not topic:
            return JsonResponse({
                'success': False,
                'error': '缺少必要參數'
            })
        
        # 初始化 Firebase Admin SDK (如果尚未初始化)
        if not firebase_admin._apps:
            # 獲取專案根目錄的絕對路徑
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 憑證文件的路徑
            cred_path = os.path.join(base_dir, "stocksentiment-8cf69-firebase-adminsdk-rsalw-a998bda61f.json")
            
            # 初始化 Firebase Admin SDK
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        # 訂閱主題
        response = messaging.subscribe_to_topic(token, topic)
        
        # 返回結果
        if response.success_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'成功訂閱主題 {topic}',
                'success_count': response.success_count,
                'failure_count': response.failure_count
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'訂閱主題失敗',
                'success_count': response.success_count,
                'failure_count': response.failure_count
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
