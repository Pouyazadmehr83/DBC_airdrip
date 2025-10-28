from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AirdropUser, AirdropTask, TaskCompletion

@admin.register(AirdropUser)
class AirdropUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_username', 'wallet_address', 'total_points', 'created_at']
    search_fields = ['user__username', 'telegram_username', 'wallet_address']

@admin.register(AirdropTask)
class AirdropTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'points_reward', 'is_active']
    list_filter = ['task_type', 'is_active']

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'completed_at', 'verified', 'points_awarded']
    list_filter = ['verified', 'points_awarded', 'task']
    actions = ['verify_completions', 'award_points']
    
    def verify_completions(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f'{updated} tasks verified successfully.')
    
    def award_points(self, request, queryset):
        count = 0
        for completion in queryset.filter(verified=True, points_awarded=False):
            user = completion.user
            user.total_points += completion.task.points_reward
            user.save()
            completion.points_awarded = True
            completion.save()
            count += 1
        self.message_user(request, f'{count} users awarded points.')