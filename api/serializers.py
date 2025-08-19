# api/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, UserSetting, PracticeSession, UserProgressSummary

# ... RegisterSerializer 保持不變 ...
class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user


# --- ✨ 最終的完美修正 ✨ ---

# 1. 告訴 UserSerializer，在讀取時，需要包含所有我們關心的欄位
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 【關鍵修正】: 補上 id, email, date_joined
        fields = ['id', 'username', 'email', 'date_joined']
        # 為了安全，我們明確標記 email 和 date_joined 在巢狀更新時是只讀的
        read_only_fields = ['email', 'date_joined']

# 2. UserProfileSerializer 現在可以保持不變，它會正確地使用上面那個更完整的 UserSerializer
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    practice_language = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'is_new', 'password', 'practice_language']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        user = instance.user
        user.username = user_data.get('username', user.username)
        
        password = validated_data.pop('password', None)
        if password:
            user.set_password(password)
        user.save()

        instance.is_new = validated_data.get('is_new', instance.is_new)
        instance.save()

        language_data = validated_data.pop('practice_language', None)
        if language_data:
            UserSetting.objects.update_or_create(
                user=user,
                language=language_data,
                defaults={'cur_lvl': 'Easy'}
            )

        return instance

# --- 其他 Serializer 保持不變 ---
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
