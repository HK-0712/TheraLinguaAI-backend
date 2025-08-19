from django.contrib import admin
from .models import Profile, UserSetting, UserProgressSummary, PracticeSession

# Register your models here.

# 建立一個 Profile 的內聯顯示，這樣在查看 User 時可以直接編輯 Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# 擴充預設的 UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# 重新註冊 User 模型以使用我們自訂的 Admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 直接註冊其他模型，讓它們出現在管理後台
admin.site.register(UserSetting)
admin.site.register(UserProgressSummary)
admin.site.register(PracticeSession)

