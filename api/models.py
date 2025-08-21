# api/models.py (The final, definitive, absolutely correct version)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.email

# --- ✨ 釜底抽薪的、終極的、決定性的修正 ✨ ---
class UserSetting(models.Model):
    # 1. 將關聯從 ForeignKey (一對多) 改為 OneToOneField (一對一)
    #    這將確保每個 User 最多只能有一個 UserSetting。
    #    我們還將 related_name 改為 'usersetting' (單數)，以匹配序列化器中的 source。
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='usersetting' # <--- 與序列化器中的 source='usersetting' 完全匹配
    )
    
    # 2. 既然是一對一，我們就不再需要在模型層面區分語言，
    #    語言將作為這個單一設定中的一個普通欄位。
    language = models.CharField(max_length=20, default='en')
    
    # 3. 根據您的提議，將 cur_lvl 和 sug_lvl 移到 UserStatus 中
    #    這兩個欄位將從這裡被【徹底移除】

    def __str__(self):
        return f"{self.user.username}'s settings"

class UserStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='status')
    language = models.CharField(max_length=2)
    
    # 4. 將 cur_lvl 和 sug_lvl 添加到這裡
    suggested_difficulty_level = models.CharField(max_length=20, help_text="Suggested difficulty level", blank=True)
    current_difficulty_level = models.CharField(max_length=20, help_text="Current difficulty level", default='Kindergarten')

    cur_word = models.CharField(max_length=255, help_text="Current test word", blank=True)
    cur_err = models.CharField(max_length=255, help_text="Error phonemes from last test", blank=True)
    cur_log = models.TextField(help_text="Full log from last test", blank=True)
    test_completed_count = models.IntegerField(default=0, help_text="Completed words in initial test")
    is_test_completed = models.BooleanField(default=False, help_text="Is initial test completed for this language?")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'language')
        
    def __str__(self):
        return f"{self.user.username}'s status in {self.language} (Test completed: {self.is_test_completed})"

# --- 其他模型保持不變 ---
class UserProgressSummary(models.Model):
    pid = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_summary')
    language = models.CharField(max_length=2)
    phoneme = models.CharField(max_length=255)
    total_atmp = models.IntegerField(default=0)
    err_amount = models.IntegerField(default=0)
    class Meta:
        unique_together = ('user', 'language', 'phoneme')
    def __str__(self):
        return f"Summary for {self.user.username} on phoneme '{self.phoneme}'"

class PracticeSession(models.Model):
    psid = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    input_mp3_path = models.CharField(max_length=255)
    output_txt = models.CharField(max_length=255)
    language = models.CharField(max_length=2)
    target_word = models.CharField(max_length=255)
    diffi_level = models.CharField(max_length=20)
    error_rate = models.FloatField()
    full_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Session {self.psid} for {self.user.username}"
