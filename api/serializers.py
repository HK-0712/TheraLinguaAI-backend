# api/serializers.py (The final, absolutely correct, and fully functional version)

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
# 1. 我們需要從 simple-jwt 的序列化器中，導入【預設的】TokenObtainPairSerializer，
#    然後對其進行【繼承和擴展】，這是最標準、最穩健的做法。
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserSetting, UserStatus

User = get_user_model()

# --- ✨ 釜底抽薪的、終極的、決定性的修正 ✨ ---
#    我們不再自己從頭寫一個 Serializer，而是繼承 simple-jwt 的預設版本，
#    並在其中，加入我們需要的、額外的返回數據。
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # 這一部分，繼承了父類的所有功能，可以正確地生成 token
        token = super().get_token(user)

        # --- 在這裡，我們可以安全地，向 token 的 payload 中，添加任何我們需要的額外資訊 ---
        # token['username'] = user.username
        # token['email'] = user.email
        
        return token

    def validate(self, attrs):
        # 這一部分，也繼承了父類的所有功能，可以正確地驗證使用者
        data = super().validate(attrs)

        # --- 在這裡，我們可以安全地，向最終返回給前端的 JSON 中，添加任何我們需要的額外資訊 ---
        # 獲取 UserProfileSerializer，並用它來序列化當前登入的使用者
        profile_serializer = UserProfileSerializer(self.user)
        # 將序列化後的 profile 數據，合併到最終的返回結果中
        data.update({'user_profile': profile_serializer.data})
        
        return data

# --- UserSettingSerializer 現在只關心全域設定 ---
class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ('language',)

# --- UserStatusSerializer 現在包含了難度等級 ---
class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ('language', 'is_test_completed', 'current_difficulty_level', 'suggested_difficulty_level')

# --- UserProfileSerializer 現在的邏輯變得極其清晰 ---
class UserProfileSerializer(serializers.ModelSerializer):
    settings = UserSettingSerializer(source='usersetting', read_only=True)
    statuses = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_joined', 'settings', 'statuses', 'password', 'confirm_password')
        read_only_fields = ('id', 'email', 'date_joined', 'settings', 'statuses')

    def get_statuses(self, obj):
        status_objects = UserStatus.objects.filter(user=obj)
        return UserStatusSerializer(status_objects, many=True).data

    def validate(self, attrs):
        password = attrs.get('password')
        if password and password != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

# --- RegisterSerializer 現在需要為新用戶創建正確的關聯物件 ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password')
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserSetting.objects.create(user=user, language='en')
        UserStatus.objects.create(user=user, language='en', current_difficulty_level='Kindergarten')
        return user

# --- InitialTestStatusSerializer 保持不變 ---
class InitialTestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ('language', 'test_completed_count', 'is_test_completed', 'cur_word', 'cur_log', 'current_difficulty_level')
