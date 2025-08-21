# api/views.py (The final, fully re-architected version)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserSetting, UserStatus
from .serializers import RegisterSerializer, UserProfileSerializer, InitialTestStatusSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 預先加載所有相關的數據，提高效率
        return User.objects.prefetch_related('usersetting', 'status').get(pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        
        # --- 處理 User 模型的更新 (username, password) ---
        user_serializer = UserProfileSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # --- 處理 UserSetting 的更新 (全域偏好語言) ---
        practice_language = request.data.get('practice_language')
        if practice_language:
            # 因為是 OneToOne，所以可以直接獲取並更新
            user_setting = user.usersetting
            user_setting.language = practice_language
            user_setting.save()

        # --- 處理 UserStatus 的更新 (特定語言的難度) ---
        # 注意：這裡我們假設難度更新，總是針對當前的偏好語言
        difficulty_level = request.data.get('current_difficulty_level')
        if difficulty_level:
            lang_to_update = practice_language or user.usersetting.language
            status_obj, _ = UserStatus.objects.get_or_create(user=user, language=lang_to_update)
            status_obj.current_difficulty_level = difficulty_level
            status_obj.save()

        # 返回包含了所有最新數據的、完整的 User 物件
        return Response(self.get_serializer(user).data)

# --- InitialTestStatusView 的邏輯也需要同步更新 ---
class InitialTestStatusView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InitialTestStatusSerializer

    def get(self, request, *args, **kwargs):
        language = request.query_params.get('lang', 'en')
        status_obj, _ = UserStatus.objects.get_or_create(user=request.user, language=language)
        return Response(self.get_serializer(status_obj).data)

    def post(self, request, *args, **kwargs):
        user = request.user
        language = request.data.get('language', 'en')
        status_obj, _ = UserStatus.objects.get_or_create(user=user, language=language)

        if status_obj.is_test_completed:
            return Response({"detail": "Test already completed."}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('status') in ['completed', 'skipped']:
            status_obj.test_completed_count += 1
            if status_obj.test_completed_count >= 20:
                status_obj.is_test_completed = True
            status_obj.save()

        return Response(self.get_serializer(status_obj).data)
