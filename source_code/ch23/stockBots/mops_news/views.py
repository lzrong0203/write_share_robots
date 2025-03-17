from django.shortcuts import render, redirect
from django.contrib import messages
from stock_charts.views import login_required_custom
from .firebase_storage import FirebaseStorageClient
import logging

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

@login_required_custom
def stock_list(request):
    """股票列表視圖"""
    try:
        # 獲取 Firebase Storage 客戶端
        storage_client = FirebaseStorageClient.get_instance()
        
        # 獲取股票代號列表
        stocks = storage_client.list_stock_folders()
        
        context = {
            'stocks': stocks,
            'user_email': request.session['user'].get('email') if 'user' in request.session else None
        }
        
        return render(request, 'mops_news/stock_list.html', context)
    except Exception as e:
        logger.error(f"獲取股票列表時出錯: {str(e)}")
        messages.error(request, f"獲取股票列表時出錯: {str(e)}")
        return render(request, 'mops_news/stock_list.html', {'stocks': []})

@login_required_custom
def news_list(request, stock_id):
    """訊息列表視圖"""
    try:
        # 獲取 Firebase Storage 客戶端
        storage_client = FirebaseStorageClient.get_instance()
        
        # 獲取特定股票的重大訊息列表
        news = storage_client.list_stock_news(stock_id)
        
        context = {
            'stock_id': stock_id,
            'news': news,
            'user_email': request.session['user'].get('email') if 'user' in request.session else None
        }
        
        return render(request, 'mops_news/news_list.html', context)
    except Exception as e:
        logger.error(f"獲取訊息列表時出錯: {str(e)}")
        messages.error(request, f"獲取訊息列表時出錯: {str(e)}")
        return redirect('stock_list')

@login_required_custom
def news_detail(request, stock_id, date_time):
    """訊息詳情視圖"""
    try:
        # 獲取 Firebase Storage 客戶端
        storage_client = FirebaseStorageClient.get_instance()
        
        # 獲取特定重大訊息的 URL
        url = storage_client.get_news_url(stock_id, date_time)
        
        if not url:
            messages.error(request, '找不到指定的訊息')
            return redirect('news_list', stock_id=stock_id)
        
        # 格式化日期時間
        if '_' in date_time:
            date, time = date_time.split('_')
            formatted_date = f"{date[:3]}/{date[3:5]}/{date[5:]}"
            formatted_time = f"{time[:2]}:{time[2:4]}:{time[4:]}" if len(time) >= 6 else time
            display_date = f"{formatted_date} {formatted_time}"
        else:
            display_date = date_time
        
        context = {
            'stock_id': stock_id,
            'date_time': date_time,
            'display_date': display_date,
            'url': url,
            'user_email': request.session['user'].get('email') if 'user' in request.session else None
        }
        
        return render(request, 'mops_news/news_detail.html', context)
    except Exception as e:
        logger.error(f"獲取訊息詳情時出錯: {str(e)}")
        messages.error(request, f"獲取訊息詳情時出錯: {str(e)}")
        return redirect('news_list', stock_id=stock_id)
