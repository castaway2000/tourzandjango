from django.contrib import admin
from .models import Partner, IntegrationPartners, Endorsement


class PartnerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Partner._meta.fields]
    readonly_fields=["uuid", "user", "api_token"]

    class Meta:
        model = Partner


    def api_token(self, obj):
        #a model with API tokens has OneToOne relation with User model, so it can be accessed in this way
        if obj.user:
            return obj.user.auth_token
        else:
            return ""

admin.site.register(Partner, PartnerAdmin)


class IntegrationPartnersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IntegrationPartners._meta.fields]

    class Meta:
        model = IntegrationPartners

admin.site.register(IntegrationPartners, IntegrationPartnersAdmin)


class EndorsementAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Endorsement._meta.fields]

    class Meta:
        model = Endorsement

admin.site.register(Endorsement, EndorsementAdmin)
