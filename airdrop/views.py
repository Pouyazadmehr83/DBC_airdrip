#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import AirdropUser, AirdropTask, TaskCompletion

def register_view(request):
    """
    صفحه ثبت‌نام با قابلیت referral
    """
    referral_code = request.GET.get('ref', '')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # ایجاد پروفایل ایردراپ
            airdrop_user = AirdropUser.objects.create(user=user)
            
            # اگر از طریق referral اومده، ثبت کن
            ref_code = request.POST.get('referral_code', '') or referral_code
            if ref_code:
                try:
                    referrer = AirdropUser.objects.get(referral_code=ref_code)
                    airdrop_user.referred_by = referrer
                    airdrop_user.save()
                    
                    # پاداش به دعوت کننده
                    referral_task = AirdropTask.objects.get(name='Refer a Friend')
                    TaskCompletion.objects.create(
                        user=referrer,
                        task=referral_task,
                        proof_url=f"Referred: {user.username}"
                    )
                    messages.success(request, f'You were referred by {referrer.user.username}!')
                    
                except AirdropUser.DoesNotExist:
                    messages.warning(request, 'Invalid referral code')
            
            # لاگین کردن کاربر
            login(request, user)
            messages.success(request, 'Account created successfully! Complete tasks to earn $DBC.')
            return redirect('airdrop:airdrop_dashboard')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'referral_code': referral_code,
    }
    return render(request, 'airdrop/register.html', context)

@login_required
def referral_dashboard(request):
    """
    صفحه مدیریت referral کاربر
    """
    airdrop_user = get_object_or_404(AirdropUser, user=request.user)
    referrals = AirdropUser.objects.filter(referred_by=airdrop_user)
    
    context = {
        'airdrop_user': airdrop_user,
        'referrals': referrals,
        'referral_count': referrals.count(),
        'referral_link': airdrop_user.get_referral_link(),
    }
    return render(request, 'airdrop/referral.html', context)

# بقیه ویوها همون قبلی میمونن...
# این decorator باعث میشه فقط کاربران لاگین شده بتونن این صفحه رو ببینن
@login_required
def airdrop_dashboard(request):
    """
    صفحه اصلی ایردراپ - کاربر تسک‌ها رو اینجا میبینه
    """
    # گرفتن یا ساخت پروفایل کاربر
    airdrop_user, created = AirdropUser.objects.get_or_create(user=request.user)
    
    # تمام تسک‌های فعال
    active_tasks = AirdropTask.objects.filter(is_active=True)
    
    # تسک‌هایی که کاربر انجام داده
    user_completions = TaskCompletion.objects.filter(user=airdrop_user)
    
    # لیست تسک‌ها با وضعیت انجام
    tasks_with_status = []
    for task in active_tasks:
        completed = user_completions.filter(task=task).exists()
        tasks_with_status.append({
            'task': task,
            'completed': completed,
            'completion': user_completions.filter(task=task).first() if completed else None
        })
    
    context = {
        'airdrop_user': airdrop_user,
        'tasks_with_status': tasks_with_status,
        'total_points': airdrop_user.total_points,
        'completed_count': user_completions.count(),
        'total_tasks': active_tasks.count(),
    }
    
    return render(request, 'airdrop/dashboard.html', context)

@login_required
def complete_task(request, task_id):
    """
    وقتی کاربر روی دکمه Complete Task کلیک میکنه
    """
    if request.method == 'POST':
        airdrop_user = get_object_or_404(AirdropUser, user=request.user)
        task = get_object_or_404(AirdropTask, id=task_id, is_active=True)
        
        # چک کن که کاربر قبلاً این تسک رو انجام نداده باشه
        existing_completion = TaskCompletion.objects.filter(
            user=airdrop_user, 
            task=task
        ).first()
        
        if existing_completion:
            messages.warning(request, 'You have already completed this task!')
        else:
            # ایجاد رکورد جدید برای انجام تسک
            completion = TaskCompletion.objects.create(
                user=airdrop_user,
                task=task,
                proof_url=request.POST.get('proof_url', '')  # کاربر میتونه لینک اثبات بذاره
            )
            messages.success(request, f'Task "{task.name}" completed! Waiting for verification.')
        
        return redirect('airdrop:airdrop_dashboard')

@login_required
def user_profile(request):
    """
    پروفایل کاربر - میتونه اطلاعاتش رو آپدیت کنه
    """
    airdrop_user = get_object_or_404(AirdropUser, user=request.user)
    
    if request.method == 'POST':
        # آپدیت اطلاعات کاربر
        airdrop_user.telegram_username = request.POST.get('telegram_username', '')
        airdrop_user.wallet_address = request.POST.get('wallet_address', '')
        airdrop_user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    context = {
        'airdrop_user': airdrop_user,
    }
    return render(request, 'airdrop/profile.html', context)