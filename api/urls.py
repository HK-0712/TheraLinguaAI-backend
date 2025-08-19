from django.urls import path
# 引入 PracticeSessionView
from .views import RegisterView, ProfileView, UserSettingView, PracticeSessionView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', UserSettingView.as_view(), name='user-settings'),
    # 新增這一行，為 PracticeSession API 設定 URL
    path('sessions/', PracticeSessionView.as_view(), name='practice-sessions'),
]
