# api/models.py

from django.db import models
from django.conf import settings # <-- 導入 settings

# UserProfile 模型
class UserProfile(models.Model):
    # 使用 settings.AUTH_USER_MODEL 代替直接導入 User
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    is_new = models.BooleanField(default=True, help_text="檢查使用者是否為第一次使用 App 並需要進行初次測試")

    def __str__(self):
        return self.user.username

# UserSetting 模型
class UserSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    language = models.CharField(max_length=20)
    sug_lvl = models.CharField(max_length=20, help_text="基於初次測試結果的建議難度等級")
    cur_lvl = models.CharField(max_length=20, help_text="使用者自己選擇的當前難度等級")

    class Meta:
        unique_together = ('user', 'language')

    def __str__(self):
        return f"{self.user.username}'s settings for {self.language}"

# UserStatus 模型
class UserStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='status')
    language = models.CharField(max_length=2)
    cur_word = models.CharField(max_length=255, help_text="使用者當前的目標單詞")
    cur_err = models.CharField(max_length=255, help_text="使用者當前的錯誤音素")
    cur_log = models.TextField(help_text="使用者當前的完整結果日誌")

    class Meta:
        unique_together = ('user', 'language')

    def __str__(self):
        return f"{self.user.username}'s status in {self.language}"

# UserProgressSummary 模型
class UserProgressSummary(models.Model):
    pid = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_summary')
    language = models.CharField(max_length=2)
    phoneme = models.CharField(max_length=255, help_text="使用者的錯誤音素")
    total_atmp = models.IntegerField(default=0, help_text="該音素的總嘗試次數")
    err_amount = models.IntegerField(default=0, help_text="該音素的錯誤次數")

    class Meta:
        unique_together = ('user', 'language', 'phoneme')

    def __str__(self):
        return f"Summary for {self.user.username} on phoneme '{self.phoneme}' in {self.language}"

    @property
    def avgErrRate(self):
        if self.total_atmp == 0:
            return 0.0
        return self.err_amount / self.total_atmp

# PracticeSession 模型
class PracticeSession(models.Model):
    psid = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    input_mp3_path = models.CharField(max_length=255, help_text="ASR 輸入的 MP3 路徑")
    output_txt = models.CharField(max_length=255, help_text="ASR 的輸出文字")
    language = models.CharField(max_length=2, choices=[('EN', 'English'), ('CH', 'Chinese')])
    target_word = models.CharField(max_length=255)
    diffi_level = models.CharField(max_length=20, help_text="難度等級")
    error_rate = models.FloatField()
    full_log = models.TextField(help_text="完整的輸出日誌")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.psid} for {self.user.username} at {self.created_at.strftime('%Y-%m-%d')}"
