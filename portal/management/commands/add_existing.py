from django.core.management.base import BaseCommand, CommandError
from portal.models import WaitlistApplicant
from tqdm import tqdm
from pathlib import Path

class Command(BaseCommand):
    help = "Adding Existing Applicants who have been alloted rooms"

    def add_arguments(self, parser):
        parser.add_argument("file-path", nargs=1)

    def handle(self, *args, **options):
        data_file = Path(options["file-path"][0]).resolve()

        if not data_file.exists():
            raise ValueError("File Does Not Exist")
        
        