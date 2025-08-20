# api/urls.py (The final, correct version with inline login view)

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer # Import the serializer, not the view
from .views import (
    RegisterView, 
    ProfileView, 
    UserSettingView, 
    InitialTestStatusView
)

# --- ✨ 核心修正: 將 View 的定義直接內聯到 urls.py 中 ✨ ---
# 這徹底斬斷了 urls.py 和 views.py 之間的循環依賴
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

urlpatterns = [
    # --- 現在，/token/ 指向我們在這個檔案中定義的 View ---
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/<str:language>/', UserSettingView.as_view(), name='user-setting'),
    path('initial-test/status/', InitialTestStatusView.as_view(), name='initial-test-status'),
]
