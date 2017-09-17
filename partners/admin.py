from django.contrib import admin
from .models import Partner


class PartnerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Partner._meta.fields]
    readonly_fields=["uuid"]

    class Meta:
        model = Partner

admin.site.register(Partner, PartnerAdmin)
