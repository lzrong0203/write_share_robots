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
            cred_path = os.path.join(settings.BASE_DIR, 'stocksentiment-8cf69-firebase-adminsdk-rsalw-001d55408c.json')
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