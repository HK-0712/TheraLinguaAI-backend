# api/admin.py
from django.contrib import admin
from .models import UserProfile, UserSetting, UserStatus, UserProgressSummary, PracticeSession

# 將所有新模型都註冊到 Admin 站點
admin.site.register(UserProfile)
admin.site.register(UserSetting)
admin.site.register(UserStatus)
admin.site.register(UserProgressSummary)
admin.site.register(PracticeSession)
