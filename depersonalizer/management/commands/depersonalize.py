from django.core.management.base import BaseCommand, CommandError

from depersonalizer.main import run_depersonalization


class Command(BaseCommand):
    help = "Run depersonalization process"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        run_depersonalization()
        self.stdout.write(self.style.SUCCESS('Depersonalization process finished'))
