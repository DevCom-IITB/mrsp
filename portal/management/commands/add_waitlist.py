from django.core.management.base import BaseCommand
from portal.models import WaitlistApplicant
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import datetime
from django.db.models import Q

class Command(BaseCommand):
    help = "Adding Existing Applicants who have been alloted rooms"

    def add_arguments(self, parser):
        parser.add_argument("file-path", nargs=1)
        #parser.add_argument("building",nargs=1)

    def handle(self, *args, **options):
        data_file = Path(options["file-path"][0]).resolve()

        if not data_file.exists():
            raise ValueError("File Does Not Exist")
        
        df = pd.read_csv(data_file, encoding='utf-8')
        t1 = WaitlistApplicant.objects.filter(Q(waitlist_t1__gt=0)).count()+1
        t = WaitlistApplicant.objects.filter(Q(waitlist_t__gt=0)).count()+1
        m = WaitlistApplicant.objects.filter(Q(waitlist_m__gt=0)).count()+1
        for index,row in tqdm(df.iterrows()):
            try:
                roll = str(int(row['REGISTRATION NUMBER']))
            except:
                roll = str(row['REGISTRATION NUMBER'])
            try:
                applicant = WaitlistApplicant(
                    application_date=datetime.datetime.strptime(row['DATE OF APPLICATION'],'%d-%m-%y'),
                    name=row['NAME'],
                    roll_number=roll,
                    fellowship_date=datetime.datetime.strptime(row['DATE OF REGISTRATION'],'%d-%m-%y'),
                    waitlist_t1 = t1 if row['TYPE1'] else -2,
                    waitlist_m = m if row['MANAS'] else -2,
                    waitlist_t = t if row['TULSI'] else -2,
                    acad_verified=True,
                    marriage_certificate_verified=True,
                    photograph_verified=True,
                    grade_sheet_verified=True,
                    recommendation_verified=True,
                )
                t1+=1
                t+=1
                m+=1
                applicant.save()
            except Exception as e:
                tqdm.write(str(e))
        
        