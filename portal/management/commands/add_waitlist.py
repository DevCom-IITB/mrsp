from django.core.management.base import BaseCommand
from portal.models import WaitlistApplicant
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import datetime
from django.db.models import Q
from dateutil import parser
import chardet

class Command(BaseCommand):
    help = "Adding Existing Applicants who have been alloted rooms"

    def add_arguments(self, parser):
        parser.add_argument("file-path", nargs=1)
        parser.add_argument("building",nargs=1)

    def handle(self, *args, **options):
        data_file = Path(options["file-path"][0]).resolve()
        print("the file path is",data_file)
        building = options['building'][0]
        print("the building is",building)

        if not data_file.exists():
            raise ValueError("File Does Not Exist")
        

        df = pd.read_excel(data_file)
        for index,row in tqdm(df.iterrows()):
            try:
                roll = str(int(row['REGISTRATION NUMBER']))
                print(roll)
            except:
                roll = str(row['REGISTRATION NUMBER'])
                print(roll)
            
            try:
                print(row['DATE OF APPLICATION'])
                # date = datetime.datetime.strptime(row['DATE OF APPLICATION'], "%Y/%m/%d %H:%M:%S")
                date = row["DATE OF APPLICATION"]
                print(date)
            except:
                try:
                    date = parser.parse(row['DATE OF APPLICATION'])
                    print(date)
                except:
                    print("Incorrect date format")
                    tqdm.write(f"Incorrect date format for {roll}")
                    continue

            try:
                applicant = WaitlistApplicant.objects.get(roll_number=roll)
                print('applicant found')
            except:
                try:
                    applicant = WaitlistApplicant(
                        application_date=date,
                        name=row['NAME'],
                        roll_number=roll,
                        fellowship_date=row['DATE OF REGISTRATION'],
                        acad_verified=True,
                        marriage_certificate_verified=True,
                        photograph_verified=True,
                        grade_sheet_verified=True,
                        recommendation_verified=True,
                        waitlist_m=-1,
                        waitlist_t=-1,
                        waitlist_t1=-1
                    )
                    print('applicant created')
                except Exception as e:
                    tqdm.write(f"{str(e)} for {roll}")
                    continue
            if building=="Type1":
                applicant.waitlist_t1 = int(row['SR. NO.'])
            if building=="Manas":
                applicant.waitlist_m = int(row['SR. NO.'])
            if building=="Tulsi":
                applicant.waitlist_t = int(row['SR. NO.'])
            try:
                applicant.save()
            except Exception as e:
                tqdm.write(f"Error {e} for {roll}")

