from django.contrib import admin
from .models import KsebCds, CdsDailyData, CdsDailyDataImport, CdsPreset

admin.site.register(KsebCds)
admin.site.register(CdsDailyData)
admin.site.register(CdsDailyDataImport)
admin.site.register(CdsPreset)