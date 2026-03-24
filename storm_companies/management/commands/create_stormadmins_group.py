from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create the StormAdmins group'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='StormAdmins')
        if created:
            self.stdout.write(self.style.SUCCESS('Created StormAdmins group'))
        else:
            self.stdout.write('StormAdmins group already exists')
