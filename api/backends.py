# api/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # 核心邏輯：嘗試用傳入的 username (實際上是 email) 去 User 表的 email 欄位裡查找
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        # 如果找到了使用者，就檢查密碼是否正確
        if user.check_password(password):
            return user
        return None
