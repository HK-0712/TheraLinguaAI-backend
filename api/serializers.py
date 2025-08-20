# api/serializers.py (The final, fully synchronized version)

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserSetting, UserStatus, UserProgressSummary, PracticeSession

User = get_user_model()

# MyTokenObtainPairSerializer 和 RegisterSerializer 保持不變
class MyTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email, password = attrs.get('email'), attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user: raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')
        else: raise serializers.ValidationError('Must include "email" and "password".', code='authorization')
        refresh = TokenObtainPairSerializer.get_token(user)
        attrs['refresh'], attrs['access'] = str(refresh), str(refresh.access_token)
        return attrs

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password')
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']: raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
        UserSetting.objects.create(user=user, language='en')
        UserStatus.objects.create(user=user, language='en')
        return user

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ('language', 'cur_lvl', 'sug_lvl')

# --- ✨ 核心修正: 讓 Profile API 返回測試完成狀態 ✨ ---
class UserProfileSerializer(serializers.ModelSerializer):
    settings = UserSettingSerializer(source='usersetting', read_only=True)
    practice_language = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    # 1. 添加一個新的欄位，用於返回測試完成狀態
    is_initial_test_completed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_joined', 'password', 'confirm_password', 'settings', 'practice_language', 'is_initial_test_completed')
        read_only_fields = ('id', 'email', 'date_joined', 'settings', 'is_initial_test_completed')
        extra_kwargs = { 'password': {'write_only': True, 'required': False} }

    # 2. 定義如何獲取這個新欄位的值
    def get_is_initial_test_completed(self, obj):
        # 嘗試獲取該使用者的 'en' 語言的 UserStatus
        # 如果存在且 is_test_completed 為 True，則返回 True，否則返回 False
        status = UserStatus.objects.filter(user=obj, language='en').first()
        return status.is_test_completed if status else False

    def validate(self, attrs):
        password = attrs.get('password')
        if password and password != attrs.get('confirm_password'): raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password: instance.set_password(password)
        instance.save()
        return instance

class InitialTestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ('language', 'test_completed_count', 'is_test_completed', 'cur_word', 'cur_log')
