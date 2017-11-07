from django.contrib import admin
from .models import Partner


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
