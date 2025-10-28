from django.db import models
from django.contrib.auth.models import User
import uuid

class AirdropUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_username = models.CharField(max_length=100, blank=True)
    wallet_address = models.CharField(max_length=100, blank=True)
    total_points = models.IntegerField(default=0)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            # ساخت کد referral منحصر به فرد
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        """ساخت کد referral ۶ رقمی"""
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not AirdropUser.objects.filter(referral_code=code).exists():
                return code
    
    def get_referral_link(self):
        """لینک دعوت برای کاربر"""
        return f"http://localhost:8000/airdrop/register/?ref={self.referral_code}"
    
    def get_referral_count(self):
        """تعداد کاربرانی که این کاربر دعوت کرده"""
        return AirdropUser.objects.filter(referred_by=self).count()
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"

# بقیه مدل‌ها همون قبلی میمونن...

class AirdropTask(models.Model):
    TASK_TYPES = [
        ('follow_twitter', 'Follow Twitter'),
        ('join_telegram', 'Join Telegram'),
        ('subscribe_youtube', 'Subscribe YouTube'),
        ('retweet', 'Retweet Post'),
    ]
    
    name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    points_reward = models.IntegerField(default=100)
    verification_url = models.URLField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class TaskCompletion(models.Model):
    user = models.ForeignKey(AirdropUser, on_delete=models.CASCADE)
    task = models.ForeignKey(AirdropTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    proof_url = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    points_awarded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'task']
    
    def __str__(self):
        return f"{self.user.user.username} - {self.task.name}"