from django.shortcuts import render, redirect
from django.contrib import messages
from .firebase_auth import FirebaseAuth

# 創建 FirebaseAuth 實例
firebase_auth = FirebaseAuth()

def register(request):
    """用戶註冊視圖"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 檢查密碼是否匹配
        if password != password_confirm:
            messages.error(request, '兩次輸入密碼不相符')
            return render(request, 'accounts/register.html')
        
        try:
            # 註冊用戶
            user = firebase_auth.register(email, password)
            messages.success(request, '註冊成功，請登入')
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'accounts/register.html')

def login(request):
    """用戶登入視圖"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # 登入用戶
            user_info = firebase_auth.login(email, password)
            
            # 將用戶信息存儲在會話中
            request.session['user'] = {
                'token': user_info['token'],
                'email': user_info['email'],
                'localId': user_info['localId'],
                'is_authenticated': True
            }
            print(user_info)
            messages.success(request, '登入成功')
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'accounts/login.html')

def logout(request):
    """用戶登出視圖"""
    # 清除會話數據
    if 'user' in request.session:
        del request.session['user']
    
    messages.success(request, '已登出')
    return redirect('login')

def home(request):
    """首頁視圖"""
    # 檢查用戶是否已登入
    if 'user' not in request.session or not request.session['user'].get('is_authenticated'):
        return redirect('login')
    
    user_email = request.session['user'].get('email')
    return render(request, 'accounts/home.html', {'user_email': user_email})
