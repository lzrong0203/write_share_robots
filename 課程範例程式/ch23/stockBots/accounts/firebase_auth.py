"""
Firebase 身份驗證工具類
提供用戶註冊、登入和登出功能
"""
import pyrebase
from django.conf import settings
from .firebase_config import FIREBASE_CONFIG

class FirebaseAuth:
    """Firebase 身份驗證工具類"""
    
    def __init__(self):
        """初始化 Firebase"""
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.auth = self.firebase.auth()
    
    def register(self, email, password):
        """
        註冊新用戶
        
        Args:
            email: 用戶電子郵件
            password: 用戶密碼
            
        Returns:
            dict: 包含用戶信息的字典
            
        Raises:
            Exception: 註冊失敗時拋出異常
        """
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            return user
        except Exception as e:
            # 處理註冊錯誤
            raise Exception(f"註冊失敗: {str(e)}")
    
    def login(self, email, password):
        """
        用戶登入
        
        Args:
            email: 用戶電子郵件
            password: 用戶密碼
            
        Returns:
            dict: 包含用戶信息和 ID token 的字典
            
        Raises:
            Exception: 登入失敗時拋出異常
        """
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            # 獲取用戶信息
            user_info = self.auth.get_account_info(user['idToken'])
            return {
                'token': user['idToken'],
                'refreshToken': user['refreshToken'],
                'localId': user['localId'],
                'email': user_info['users'][0]['email'],
                'emailVerified': user_info['users'][0]['emailVerified']
            }
        except Exception as e:
            # 處理登入錯誤
            raise Exception(f"登入失敗: {str(e)}")
    
    def logout(self):
        """
        用戶登出
        
        注意: Firebase 不提供服務器端登出功能，
        登出主要是在客戶端刪除 token
        """
        # Firebase 不提供服務器端登出功能
        # 在 Django 中，我們只需要清除會話數據
        return True
    
    def get_user_info(self, id_token):
        """
        獲取用戶信息
        
        Args:
            id_token: 用戶的 ID token
            
        Returns:
            dict: 包含用戶信息的字典
        """
        try:
            user_info = self.auth.get_account_info(id_token)
            return user_info
        except Exception as e:
            raise Exception(f"獲取用戶信息失敗: {str(e)}")
    
    def verify_token(self, id_token):
        """
        驗證 ID token
        
        Args:
            id_token: 用戶的 ID token
            
        Returns:
            bool: token 是否有效
        """
        try:
            self.auth.get_account_info(id_token)
            return True
        except:
            return False 