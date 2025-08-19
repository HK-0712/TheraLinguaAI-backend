from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.contrib.auth.models import User

# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    一個允許任何人 (AllowAny) 建立新使用者 (CreateAPIView) 的 API 視圖。
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # 允許任何未登入的使用者訪問此 API
    serializer_class = RegisterSerializer # 告訴這個視圖要使用哪個序列化器

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # 驗證資料，如果失敗會自動拋出錯誤
        user = serializer.save() # 呼叫 serializer 中的 create 方法來儲存使用者

        # 可以在這裡擴充，例如建立 Profile
        if not hasattr(user, 'profile'):
            from .models import Profile
            Profile.objects.create(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User created successfully."}, # 回傳一個成功的訊息
            status=status.HTTP_201_CREATED, # HTTP 狀態碼 201 表示「已建立」
            headers=headers
        )

from rest_framework.permissions import IsAuthenticated # 引入「必須登入」的權限
from .serializers import ProfileSerializer
from .models import Profile

class ProfileView(generics.RetrieveAPIView):
    """
    一個只允許已登入使用者 (IsAuthenticated) 訪問的 API 視圖。
    它會回傳當前登入使用者的 Profile。
    """
    permission_classes = (IsAuthenticated,) # <-- 關鍵！設定權限為必須登入
    serializer_class = ProfileSerializer

    def get_object(self):
        # 這個函式會自動回傳與當前登入使用者關聯的 Profile 物件
        return self.request.user.profile

from .serializers import UserSettingSerializer # 引入新的 Serializer
from .models import UserSetting # 引入新的 Model

class UserSettingView(generics.RetrieveUpdateAPIView):
    """
    一個允許使用者讀取(Retrieve)和更新(Update)自己設定的 API 視圖。
    """
    permission_classes = (IsAuthenticated,) # <-- 同樣，必須登入才能訪問
    serializer_class = UserSettingSerializer

    def get_object(self):
        # 這段程式碼是核心：
        # UserSetting.objects.get_or_create(user=self.request.user)
        # 它會嘗試去獲取當前登入使用者的設定。
        # 如果這個使用者還沒有設定（例如，剛註冊），它會自動為其建立一個空的設定記錄。
        # 這確保了每個使用者都必定有一個 UserSetting 物件，極大地簡化了前端的邏輯。
        # 我們只回傳第一個元素，因為 get_or_create 回傳的是一個 (object, created_boolean) 的元組。
        return UserSetting.objects.get_or_create(user=self.request.user)[0]

from .serializers import PracticeSessionSerializer # 引入新的 Serializer
from .models import PracticeSession # 引入新的 Model

class PracticeSessionView(generics.ListCreateAPIView):
    """
    一個允許使用者查詢(List)自己的練習紀錄，和建立(Create)新紀錄的 API 視圖。
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PracticeSessionSerializer

    def get_queryset(self):
        """
        這個函式是核心之一：它會自動過濾查詢集，
        只回傳屬於當前登入使用者的練習紀錄。
        """
        return PracticeSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        這個函式是另一個核心：當建立新紀錄時，
        它會自動將當前登入的使用者設定為這筆紀錄的 'user'。
        """
        # 這裡我們先用一個假路徑，後續再處理真實的檔案上傳
        serializer.save(user=self.request.user, input_audio_path='temp/fake_path.mp3')
