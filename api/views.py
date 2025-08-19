# api/views.py

from rest_framework import generics, permissions
from .models import UserProfile, UserSetting
from .serializers import RegisterSerializer, UserProfileSerializer, UserSettingSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    獲取和更新使用者的個人資料。
    GET: 獲取當前登入使用者的 Profile。
    PATCH/PUT: 更新使用者的 username, password, 或 practice_language。
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 總是返回當前登入使用者的 Profile，如果不存在則創建
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

# SettingsView 保持不變
class SettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'language'
    lookup_url_kwarg = 'language'

    def get_queryset(self):
        return UserSetting.objects.filter(user=self.request.user)
