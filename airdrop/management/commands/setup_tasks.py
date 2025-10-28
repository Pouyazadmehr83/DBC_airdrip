from django.core.management.base import BaseCommand
from airdrop.models import AirdropTask

class Command(BaseCommand):
    help = 'Create default airdrop tasks'
    
    def handle(self, *args, **options):
        tasks_data = [
            {
                'name': 'Follow us on Twitter',
                'task_type': 'follow_twitter',
                'points_reward': 100,
                'verification_url': 'https://twitter.com/donkeyblastcoin',
            },
            {
                'name': 'Join our Telegram channel',
                'task_type': 'join_telegram', 
                'points_reward': 150,
                'verification_url': 'https://t.me/DonkeyBlastCoin',
            },
            {
                'name': 'Subscribe to our YouTube',
                'task_type': 'subscribe_youtube',
                'points_reward': 200,
                'verification_url': 'https://youtube.com/',  # بعداً آدرس واقعی میزاریم
            },
            {
                'name': 'Retweet our pinned post',
                'task_type': 'retweet',
                'points_reward': 50,
                'verification_url': 'https://twitter.com/donkeyblastcoin',
            },
        ]
        
        created_count = 0
        for task_data in tasks_data:
            task, created = AirdropTask.objects.get_or_create(
                name=task_data['name'],
                defaults=task_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created task: {task.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} tasks')
        )