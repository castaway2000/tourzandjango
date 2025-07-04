from django.contrib import admin
from .models import *
from django_summernote.admin import SummernoteModelAdmin, SummernoteInlineModelAdmin


class GuideAnswerInline(admin.TabularInline, SummernoteInlineModelAdmin):
    model = GuideAnswer
    extra = 0


class GuideProfileAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in GuideProfile._meta.fields]
    inlines = [GuideAnswerInline]

    class Meta:
        model = GuideProfile

admin.site.register(GuideProfile, GuideProfileAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    readonly_fields = ["html_field_name"]

    class Meta:
        model = Service

admin.site.register(Service, ServiceAdmin)


class GuideServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideService._meta.fields]

    class Meta:
        model = GuideService

admin.site.register(GuideService, GuideServiceAdmin)


class QuestionAdmin(admin.ModelAdmin):

    class Meta:
        model = Question

admin.site.register(Question, QuestionAdmin)


class GuideAnswerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideAnswer._meta.fields]

    class Meta:
        model = GuideAnswer

admin.site.register(GuideAnswer, GuideAnswerAdmin)



