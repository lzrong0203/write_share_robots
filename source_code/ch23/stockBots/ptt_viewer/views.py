from django.shortcuts import render, redirect
from django.contrib import messages
from stock_charts.views import login_required_custom
from .firebase_client import FirebasePTTClient

# Create your views here.

@login_required_custom
def post_list(request):
    """PTT 文章列表視圖"""
    # 獲取 Firebase 客戶端
    firebase_client = FirebasePTTClient.get_instance()
    
    # 獲取文章
    posts = firebase_client.get_all_posts()
    
    context = {
        'posts': posts,
        'user_email': request.session['user'].get('email') if 'user' in request.session else None
    }
    
    return render(request, 'ptt_viewer/post_list.html', context)

@login_required_custom
def post_detail(request, post_id):
    """PTT 文章詳情視圖"""
    # 獲取 Firebase 客戶端
    firebase_client = FirebasePTTClient.get_instance()
    
    # 獲取文章
    post = firebase_client.get_post(post_id)
    
    if not post:
        messages.error(request, '找不到指定的文章')
        return redirect('post_list')
    
    context = {
        'post': post,
        'user_email': request.session['user'].get('email') if 'user' in request.session else None
    }
    
    return render(request, 'ptt_viewer/post_detail.html', context)
