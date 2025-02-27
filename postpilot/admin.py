from django.contrib import admin

from .models import SendAttempt


@admin.register(SendAttempt)
class SendAttempAdmin(admin.ModelAdmin):
    list_display = ("attempt_at", "status", "response", "mailing")
    list_filter = ("status", "attempt_at")
    search_fields = ("user__username", "mailing")
