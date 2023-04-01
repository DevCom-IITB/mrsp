from django.core.management.base import BaseCommand
from portal.models import WaitlistApplicant
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import datetime

class Command(BaseCommand):
    help = "Adding Existing Applicants who have been alloted rooms"

    def add_arguments(self, parser):
        parser.add_argument("file-path", nargs=1)
        parser.add_argument("building",nargs=1)

    def handle(self, *args, **options):
        data_file = Path(options["file-path"][0]).resolve()

        if not data_file.exists():
            raise ValueError("File Does Not Exist")
        
        df = pd.read_csv(data_file)

        for index,row in tqdm(df.iterrows()):
            try:
                roll = str(int(row['roll']))
            except:
                roll = str(row['roll'])
            try:
                applicant = WaitlistApplicant(
                    application_date=datetime.datetime.strptime(row['application date'],'%d-%m-%y'),
                    name=row['name'],
                    roll_number=roll,
                    fellowship_date=datetime.datetime.strptime(row['reg date'],'%d-%m-%y'),
                    waitlist_t1 = int(row['waitlist_t1']),
                    waitlist_mt = int(row['waitlist_mt']),
                    acad_verified=True,
                    marriage_certificate_verified=True,
                    photograph_verified=True,
                    grade_sheet_verified=True,
                    recommendation_verified=True,
                )
                applicant.save()
            except Exception as e:
                tqdm.write(str(e))
        
        