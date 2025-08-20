# api/serializers.py (The final, definitive, data-integrity-guaranteed version)

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserSetting, UserStatus, UserProgressSummary, PracticeSession

User = get_user_model()

# MyTokenObtainPairSerializer 是正確的，無需改動
class MyTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user: raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')
        else: raise serializers.ValidationError('Must include "email" and "password".', code='authorization')
        refresh = TokenObtainPairSerializer.get_token(user)
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)
        return attrs

# --- ✨ 核心修正: 確保新用戶的數據完整性 ✨ ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # 1. 創建 User 物件
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 2. 【釜底抽薪的修正】: 在這裡，為新用戶創建所有必需的關聯物件。
        #    這將保證任何後續對 profile 的查詢都不會因為缺少關聯物件而失敗。
        UserSetting.objects.create(user=user, language='en')
        UserStatus.objects.create(user=user, language='en') # 確保 UserStatus 也被創建
        
        # 3. 返回創建的 user 物件
        return user

# UserSettingSerializer 是正確的，無需改動
class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ('language', 'cur_lvl', 'sug_lvl')

# UserProfileSerializer 現在是正確的，因為 RegisterSerializer 保證了數據的完整性
class UserProfileSerializer(serializers.ModelSerializer):
    settings = UserSettingSerializer(source='usersetting', read_only=True)
    practice_language = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_joined', 'password', 'confirm_password', 'settings', 'practice_language')
        read_only_fields = ('id', 'email', 'date_joined', 'settings')
        extra_kwargs = { 'password': {'write_only': True, 'required': False} }

    def validate(self, attrs):
        password = attrs.get('password')
        if password and password != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# InitialTestStatusSerializer 是正確的，無需改動
class InitialTestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ('language', 'test_completed_count', 'is_test_completed', 'cur_word', 'cur_log')
