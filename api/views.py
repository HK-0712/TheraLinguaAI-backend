# api/views.py (The final, simplified version)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
import json
import random
import os

from .models import UserSetting, UserStatus, UserProgressSummary
from .serializers import (
    RegisterSerializer, 
    UserProfileSerializer, 
    UserSettingSerializer, 
    InitialTestStatusSerializer
)

User = get_user_model()

# RegisterView 保持不變
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# ProfileView 保持不變
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return User.objects.prefetch_related('usersetting').get(pk=self.request.user.pk)
    def update(self, request, *args, **kwargs):
        language_data = request.data.pop('practice_language', None)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if language_data:
            user_setting, created = UserSetting.objects.get_or_create(user=instance)
            user_setting.language = language_data
            user_setting.save()
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

# UserSettingView 保持不變
class UserSettingView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'language'
    def get_queryset(self):
        return UserSetting.objects.filter(user=self.request.user)

# --- ✨ 核心修正: 徹底簡化 InitialTestStatusView 的邏輯 ✨ ---
class InitialTestStatusView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InitialTestStatusSerializer

    def get(self, request, *args, **kwargs):
        # GET 請求現在只負責一件事：返回使用者在特定語言下的測試狀態
        language = request.query_params.get('lang', 'en')
        status_obj, _ = UserStatus.objects.get_or_create(user=request.user, language=language)
        return Response(self.get_serializer(status_obj).data)

    def post(self, request, *args, **kwargs):
        # POST 請求現在只負責更新狀態，不再生成單字
        user = request.user
        language = request.data.get('language', 'en')
        word_status = request.data.get('status')
        
        status_obj, _ = UserStatus.objects.get_or_create(user=user, language=language)

        if status_obj.is_test_completed:
            return Response({"detail": "Test already completed."}, status=status.HTTP_400_BAD_REQUEST)

        # "Try Another" 這個邏輯現在完全由前端處理，後端直接忽略即可
        if word_status == 'try_another':
            return Response(self.get_serializer(status_obj).data, status=status.HTTP_200_OK)

        # 只有當 status 是 'completed' 或 'skipped' 時，才更新進度
        if word_status in ['completed', 'skipped']:
            status_obj.cur_log = request.data.get('cur_log', '')
            status_obj.cur_err = ", ".join(request.data.get('cur_err', []))
            
            # 如果是 'completed' 且有錯誤，才記錄到 ProgressSummary
            if word_status == 'completed':
                for phoneme in request.data.get('cur_err', []):
                    summary, _ = UserProgressSummary.objects.get_or_create(user=user, language=language, phoneme=phoneme)
                    summary.total_atmp += 1
                    summary.err_amount += 1
                    summary.save()
            
            status_obj.test_completed_count += 1
            if status_obj.test_completed_count >= 20:
                status_obj.is_test_completed = True
            
            status_obj.save()

        # 返回更新後的最新狀態
        return Response(self.get_serializer(status_obj).data)
