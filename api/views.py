# api/views.py (The final, truly robust version)

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

# RegisterView 和 get_next_test_word 保持不變
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

def get_next_test_word(language, completed_count):
    difficulty_map = { range(0, 5): 'Kindergarten', range(5, 10): 'Primary School', range(10, 15): 'Secondary School', range(15, 20): 'Professor', }
    current_difficulty = next((level for num_range, level in difficulty_map.items() if completed_count in num_range), None)
    if not current_difficulty: return None
    file_path = os.path.join(settings.BASE_DIR, 'initial-test-words.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f: word_data = json.load(f)
        word_list = word_data.get(current_difficulty, [])
        return random.choice(word_list) if word_list else "Error: Word list empty."
    except (FileNotFoundError, json.JSONDecodeError): return "Error: Word data file not found."

# --- ✨ 核心修正: 讓 ProfileView 的查詢更具魯棒性 ✨ ---
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 使用 prefetch_related 代替 select_related。
        # 即使關聯的 usersetting 不存在，這也不會導致查詢失敗。
        return User.objects.prefetch_related('usersetting').get(pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        language_data = request.data.pop('practice_language', None)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 這裡我們手動調用序列化器來處理 User 模型的更新
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 如果前端提供了語言數據，就更新它
        if language_data:
            # 使用 get_or_create 來確保 UserSetting 記錄一定存在
            user_setting, created = UserSetting.objects.get_or_create(user=instance)
            user_setting.language = language_data
            user_setting.save()

        # 重新獲取實例以確保所有資料都是最新的
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

# --- 其他 View 保持不變 ---
class UserSettingView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'language'
    def get_queryset(self):
        return UserSetting.objects.filter(user=self.request.user)

class InitialTestStatusView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InitialTestStatusSerializer
    def get(self, request, *args, **kwargs):
        language = request.query_params.get('lang', 'en')
        status_obj, _ = UserStatus.objects.get_or_create(user=request.user, language=language)
        if status_obj.is_test_completed: return Response(self.get_serializer(status_obj).data)
        next_word = get_next_test_word(language, status_obj.test_completed_count)
        status_obj.cur_word = next_word or "Test Finished"; status_obj.save()
        return Response(self.get_serializer(status_obj).data)
    def post(self, request, *args, **kwargs):
        user, language = request.user, request.data.get('language', 'en')
        status_obj, _ = UserStatus.objects.get_or_create(user=user, language=language)
        if status_obj.is_test_completed: return Response({"detail": "Test already completed."}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('status') == 'try_another':
            status_obj.cur_word = get_next_test_word(language, status_obj.test_completed_count)
            status_obj.save()
            return Response(self.get_serializer(status_obj).data, status=status.HTTP_200_OK)
        status_obj.cur_log, status_obj.cur_err = request.data.get('cur_log', ''), ", ".join(request.data.get('cur_err', []))
        if request.data.get('status') == 'completed':
            for phoneme in request.data.get('cur_err', []):
                summary, _ = UserProgressSummary.objects.get_or_create(user=user, language=language, phoneme=phoneme)
                summary.total_atmp += 1; summary.err_amount += 1; summary.save()
        status_obj.test_completed_count += 1
        if status_obj.test_completed_count >= 20: status_obj.is_test_completed = True
        status_obj.save()
        return self.get(request, *args, **kwargs)
