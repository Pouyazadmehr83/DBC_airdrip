from django.urls import path
from . import views

app_name = 'airdrop'

urlpatterns = [
    path('', views.airdrop_dashboard, name='airdrop_dashboard'),
    path('register/', views.register_view, name='register'),
    path('referral/', views.referral_dashboard, name='referral_dashboard'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('profile/', views.user_profile, name='user_profile'),
]