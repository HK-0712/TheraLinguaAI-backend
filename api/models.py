from django.db import models
from django.contrib.auth.models import User

# 擴充內建 User 模型，增加 is_new 和 current_language 欄位
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_new = models.BooleanField(default=True)
    current_language = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 使用者針對不同語言的設定
class UserSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settings')
    language = models.CharField(max_length=2)
    suggested_level = models.CharField(max_length=20)
    current_level = models.CharField(max_length=20)

    class Meta:
        unique_together = ('user', 'language')

    def __str__(self):
        return f"{self.user.username}'s setting for {self.language}"

# 使用者在特定語言中，對特定音素的進度總結
class UserProgressSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_summaries')
    language = models.CharField(max_length=2)
    phoneme = models.CharField(max_length=255)
    total_attempts = models.IntegerField(default=0)
    error_amount = models.IntegerField(default=0)

    @property
    def average_error_rate(self):
        if self.total_attempts == 0:
            return 0.0
        return self.error_amount / self.total_attempts

    class Meta:
        unique_together = ('user', 'language', 'phoneme')

    def __str__(self):
        return f"Summary for {self.user.username} on phoneme '{self.phoneme}' in {self.language}"

# 每一次的練習會話紀錄
class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    input_audio_path = models.CharField(max_length=255, default='no_audio.mp3')
    asr_output = models.CharField(max_length=255)
    language = models.CharField(max_length=2)
    target_word = models.CharField(max_length=255)
    difficulty_level = models.CharField(max_length=255)
    error_rate = models.FloatField()
    full_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Practice by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

