from django.contrib.auth.models import User
from rest_framework import serializers, validators

class RegisterSerializer(serializers.ModelSerializer):
    # email 欄位是必需的，並且在所有使用者中必須是唯一的
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )

    # password 欄位只用於寫入 (前端傳給後端)，不能被讀取 (後端傳給前端)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User  # 我們要操作的模型是 Django 內建的 User
        # 我們需要前端提供這三個欄位
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        # 這是建立新使用者的核心邏輯
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    # 讓 username 直接顯示在 Profile 裡，方便前端使用
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        # 我們希望回傳這些欄位給前端
        fields = ('username', 'email', 'is_new', 'current_language')

from .models import UserSetting # 引入 UserSetting 模型

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        # 我們只希望前端能讀取和修改這三個欄位
        # 'user' 欄位將由後端根據當前登入者自動處理，不需要前端提供
        fields = ('language', 'suggested_level', 'current_level')

from .models import PracticeSession # 引入 PracticeSession 模型

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        # 'user' 欄位將由後端自動設定，所以我們從 fields 中排除
        # 'id' 和 'created_at' 是唯讀的，DRF 會自動處理
        fields = ('id', 'input_audio_path', 'asr_output', 'language', 'target_word', 'difficulty_level', 'error_rate', 'full_log', 'created_at')
        # 將 'input_audio_path' 設定為唯讀，因為我們不希望使用者能直接修改檔案路徑
        # 檔案上傳將透過另一個機制處理
        read_only_fields = ('input_audio_path',)
