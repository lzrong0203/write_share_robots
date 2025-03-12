from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_page, name='notification_page'),
    path('subscribe_topic/', views.subscribe_topic, name='subscribe_topic'),
] 