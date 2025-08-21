# api/urls.py (The final, dependency-free, absolutely correct version)

from django.urls import path
# 1. 只從 simplejwt.views 中，導入【預設的】 View
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# 2. 導入您需要的、來自 views.py 的其他 View
from .views import (
    RegisterView, 
    ProfileView, 
    InitialTestStatusView
)

urlpatterns = [
    # 3. 讓 /token/ 這個路徑，直接指向 simple-jwt 【預設的】TokenObtainPairView。
    #    您在 settings.py 中的設定，會自動地、在幕後，將這個預設的 View，
    #    與您在 serializers.py 中自訂的 MyTokenObtainPairSerializer 關聯起來。
    #    這就是 Django 框架最優雅的「解耦」設計。
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 4. 其他所有的 URL 路徑，保持不變。
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('initial-test/status/', InitialTestStatusView.as_view(), name='initial-test-status'),
]
