from django.contrib import admin
from .models import WaitlistApplicant, ApplicantBase
from django.db.models import Q

@admin.register(WaitlistApplicant)
class WaitlistAdmin(admin.ModelAdmin):
    model = WaitlistApplicant

    search_fields = ['roll_number']
    list_display = ['name','roll_number','occupying_building','vacating_date']

    def get_queryset(self, request):
        return WaitlistApplicant.objects.filter(Q(occupying__gt=0) | Q(waitlist_t1__gt=0) | Q(waitlist_m__gt=0) | Q(waitlist_t__gt=0))
    
    def __str__(self) -> str:
        return super().__str__()
    