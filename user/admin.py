from django.contrib import admin

from user.models import SecurityQuestion


class SecurityQuestionAdmin(admin.ModelAdmin):
    model = SecurityQuestion
    readonly_fields = ('id',)
    list_display = ('id', 'question')

admin.site.register(SecurityQuestion)
