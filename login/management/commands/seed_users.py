from django.core.management.base import BaseCommand
from login.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not User.objects.filter(tr_number='26365').exists():
            User.objects.create_user(
                tr_number='26365',
                password='mala@1234',
                role='Admin',
                first_name='Aliasger',
                last_name='Mala',
                its_number='30477380',
                class_name='7',
                hizb='Firozaj'
            )
            self.stdout.write(self.style.SUCCESS('✅ Test user created'))
