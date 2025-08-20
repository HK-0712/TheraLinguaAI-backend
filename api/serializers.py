# api/serializers.py (最終的、絕對正確的、經過修正的修正版)

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, UserSetting, PracticeSession, UserProgressSummary
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username', validated_data['email']),
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        UserSetting.objects.create(user=user)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    practice_language = serializers.SerializerMethodField()

    # --- ✨ 核心修正 1: 我們不再需要 'language_update'，因為它帶來了混淆。
    # 我們將直接在 update 方法中處理傳入的 'practice_language' key。
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = UserProfile
        # 我們在 fields 中只保留模型中真實存在的欄位，以及唯讀欄位
        fields = [
            'user_id', 'user', 'email', 'date_joined', 'is_new', 
            'practice_language', 'username', 'password', 'confirm_password'
        ]

    def get_practice_language(self, obj):
        if hasattr(obj.user, 'settings'):
            return obj.user.settings.language
        return 'en'

    def validate(self, attrs):
        # ✨ 核心修正 2: 由於前端發送的 payload 中有 'practice_language'，
        # DRF 會嘗試驗證它。我們需要手動將它添加到 attrs 中，以便後續使用。
        request = self.context.get('request')
        if request and request.data.get('practice_language'):
            attrs['practice_language'] = request.data.get('practice_language')
        
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password and password != confirm_password:
            raise serializers.ValidationError({"password": "New passwords do not match."})
        return attrs

    # --- ✨ 核心修正 3: 這是最終的、絕對正確的、手動的 update 方法 ✨ ---
    def update(self, instance, validated_data):
        user_instance = instance.user
        
        # 1. 手動處理 language 更新
        language_data = validated_data.get('practice_language', None)
        if language_data:
            user_setting = user_instance.settings
            user_setting.language = language_data
            user_setting.save()

        # 2. 手動處理 username 更新
        new_username = validated_data.get('username', None)
        if new_username is not None:
            user_instance.username = new_username

        # 3. 手動處理 password 更新
        new_password = validated_data.get('password', None)
        if new_password:
            user_instance.set_password(new_password)
        
        # 4. 將對 User 模型的所有修改一次性保存
        user_instance.save()

        # 5. 手動處理 UserProfile 自身的欄位更新 (如果有的話)
        instance.is_new = validated_data.get('is_new', instance.is_new)
        instance.save()
        
        return instance

# --- 其他 Serializer 保持不變 ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if user is None:
            raise serializers.ValidationError('No active account found with the given credentials')
        refresh = self.get_token(user)
        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ['language', 'sug_lvl', 'cur_lvl']
        read_only_fields = ['language']

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = '__all__'
        read_only_fields = ('user',)

class UserProgressSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgressSummary
        fields = '__all__'
