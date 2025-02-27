from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('stock_chart/', views.stock_chart_view, name='stock_chart'),
    path('ptt_posts/', views.ptt_posts_view, name='ptt_posts'),
    path('news/', views.news_view, name='news'),
    path('user_info/', views.user_info_view, name='user_info'),
] 