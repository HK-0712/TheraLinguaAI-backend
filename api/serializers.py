# api/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, UserSetting, PracticeSession, UserProgressSummary
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

# RegisterSerializer 和 MyTokenObtainPairSerializer 保持不變
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
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        UserSetting.objects.create(user=user, language='en', cur_lvl='Easy')
        return user

# --- ✨ 這是我們的全新武器：一個專門處理 User 更新的序列化器 ✨ ---
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    這個序列化器只關心一件事：如何更新 User 模型。
    它只包含可以被使用者修改的欄位。
    """
    class Meta:
        model = User
        fields = ['username'] # 只允許更新 username

class UserProfileSerializer(serializers.ModelSerializer):
    """
    這是我們重構後的主序列化器。
    """
    # --- 用於讀取 (GET) 的欄位 ---
    # ✨ 核心修正 1: 我們不再使用 source='user.username'，而是直接將整個 User 物件
    # 通過我們上面定義的 UserUpdateSerializer 進行序列化，但只用於讀取。
    user = UserUpdateSerializer(read_only=True)
    
    # 為了在頂層依然能方便地讀取 email 等資訊，我們保留這些欄位
    email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    practice_language = serializers.SerializerMethodField()

    # --- 用於寫入 (PATCH) 的欄位 ---
    # ✨ 核心修正 2: 我們創建一個專門用於「寫入」的巢狀欄位。
    # 前端發送的 {"username": "new_name"} 將會被這個欄位捕獲。
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = [
            'user_id', 'user', 'email', 'date_joined', 'is_new', 
            'practice_language', 'username', 'password', 'confirm_password'
        ]
        # 我們將 'user' 欄位從 Meta 中移除，因為我們手動定義了它

    def get_practice_language(self, obj):
        setting = UserSetting.objects.filter(user=obj.user).first()
        return setting.language if setting else 'en'

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password and password != confirm_password:
            raise serializers.ValidationError({"password": "New passwords do not match."})
        return attrs

    # --- ✨ 核心修正 3: 這是一個全新的、邏輯無比清晰的 update 方法 ✨ ---
    def update(self, instance, validated_data):
        user_instance = instance.user

        # 1. 更新 Username
        # 我們從 validated_data 中獲取 'username'，如果存在，就更新它。
        new_username = validated_data.get('username', None)
        if new_username is not None:
            user_instance.username = new_username

        # 2. 更新 Password
        # 我們從 validated_data 中獲取 'password'，如果存在，就更新它。
        new_password = validated_data.get('password', None)
        if new_password:
            user_instance.set_password(new_password)
        
        # 將對 User 模型的所有修改一次性保存
        user_instance.save()

        # 3. 更新 Language Setting
        language_data = validated_data.get('practice_language')
        if language_data:
            UserSetting.objects.update_or_create(
                user=user_instance,
                defaults={'language': language_data}
            )

        # 4. 更新 UserProfile 自身的欄位 (如果有的話)
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
