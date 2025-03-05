from django.contrib import admin

from .models import SendAttempt, Mailing, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "comments", "owner")
    list_filter = ("owner", "email")
    search_fields = ("username", "email", "comments")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "body_text", "created_at")
    search_fields = ("subject", "body_text")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("first_sent_at", "sent_completed_at", "status", "message", "owner")
    list_filter = ("status", "first_sent_at")
    search_fields = ("message__subject", "message__body")


@admin.register(SendAttempt)
class SendAttempAdmin(admin.ModelAdmin):
    list_display = ("attempt_at", "status", "response", "mailing")
    list_filter = ("status", "attempt_at")
    search_fields = ("user__username", "mailing")
