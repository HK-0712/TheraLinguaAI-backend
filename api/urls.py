# api/urls.py

from django.urls import path
# 【關鍵修正】: 導入一個新的 View
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView,
    # 導入這個專為 Email 登入設計的 View
    TokenObtainPairView as EmailTokenObtainPairView
)
from .views import RegisterView, ProfileView, SettingsView

urlpatterns = [
    # 【關鍵修正】: 將 token/ 路徑指向新的 View
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/<str:language>/', SettingsView.as_view(), name='settings'),
]
