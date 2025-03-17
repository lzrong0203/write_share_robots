"""
URL configuration for stockBots project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

# 提供 Service Worker 文件
def firebase_messaging_sw(request):
    with open(settings.BASE_DIR / 'static' / 'firebase-messaging-sw.js', 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),  # 包含 accounts 應用程式的 URL
    path("stocks/", include("stock_charts.urls")),  # 添加 stock_charts 應用程式的 URL
    path("ptt/", include("ptt_viewer.urls")),  # 添加 ptt_viewer 應用程式的 URL
    path("mops/", include("mops_news.urls")),  # 添加股市重大訊息查看應用程式的 URL
    path("notifications/", include("notifications.urls")),  # 添加通知應用程式的 URL
    
    # 提供 Service Worker 文件
    path("firebase-messaging-sw.js", never_cache(firebase_messaging_sw), name="firebase_messaging_sw"),
]

# 在開發環境中提供靜態文件
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
