from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import datetime


class PortalConfig(AppConfig):
    name = 'portal'

    def ready(self):
        from portal.models import WaitlistApplicant
        from portal import db_lock

        def update_expired_offers():
            for applicant in WaitlistApplicant.objects.all():
                db_lock.obtain_lock()
                try:
                    if applicant.offer > 0 and applicant.get_offer_expiry_date() < datetime.date.today():
                        applicant.decline_offer()
                except:
                    pass
                db_lock.release_lock()

        scheduler = BackgroundScheduler()
        scheduler.add_job(update_expired_offers, 'cron', hour=0)
        scheduler.start()
