from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('<str:stock_id>/', views.news_list, name='news_list'),
    path('<str:stock_id>/<str:date_time>/', views.news_detail, name='news_detail'),
] 