from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from .utils import get_stock_data, generate_stock_chart

def login_required_custom(view_func):
    """自定義登入要求裝飾器，適用於 Firebase 身份驗證"""
    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session or not request.session['user'].get('is_authenticated'):
            messages.error(request, '請先登入')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_custom
def stock_chart(request):
    """股票圖表視圖"""
    # 預設值
    default_ticker = '2330.tw'
    default_start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    default_end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 從請求中獲取參數，如果沒有則使用預設值
    ticker = request.GET.get('ticker', default_ticker)
    start_date = request.GET.get('start_date', default_start_date)
    end_date = request.GET.get('end_date', default_end_date)
    
    chart = None
    error_message = None
    
    # 如果有請求參數，生成圖表
    if 'generate' in request.GET:
        # 獲取股票數據
        data, error = get_stock_data(ticker, start_date, end_date)
        
        if error:
            error_message = error
        else:
            # 生成圖表
            chart, chart_error = generate_stock_chart(data, ticker)
            if chart_error:
                error_message = chart_error
    
    context = {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'chart': chart,
        'error_message': error_message,
        'user_email': request.session['user'].get('email') if 'user' in request.session else None
    }
    
    return render(request, 'stock_charts/chart.html', context)
