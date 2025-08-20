# api/admin.py (The final, correct version)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSetting, UserStatus, UserProgressSummary, PracticeSession

# This custom admin class allows us to customize how the new User model is displayed.
class CustomUserAdmin(UserAdmin):
    # Add our custom fields to the display list in the admin panel
    list_display = ('email', 'username', 'date_joined', 'is_staff')
    # Add our custom fields to the fieldsets for editing
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets

# Register all our models with the admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserSetting)
admin.site.register(UserStatus)
admin.site.register(UserProgressSummary)
admin.site.register(PracticeSession)
