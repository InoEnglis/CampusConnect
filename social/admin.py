from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.contrib import admin
from django.urls import reverse
from .models import BannedUser, Post, PostImage, PostFile, UserUnderInvestigation
from .models import EventReminder, Feedback, GroupRule, MessageStatus, Notification, Post, UserProfile, Report, Rule, Conversation, Group, Event, UserStatus, Message
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib import admin
from .models import Evidence
from django.contrib import messages
from django.contrib import admin
from django.shortcuts import get_object_or_404
from .models import Report, Evidence, UserUnderInvestigation 
from social.models import Post  
from django.utils.timezone import now
from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now, timedelta
from .models import Report, Evidence, UserUnderInvestigation

from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now, timedelta
from .models import Report, Evidence, UserUnderInvestigation




class ReportAdmin(admin.ModelAdmin):
    change_form_template = "social/admin/report.html"

    list_display = ('post', 'reporter', 'reason', 'reported_on', 'resolved')
    list_filter = ('reported_on', 'reason')
    search_fields = ('post__body', 'reporter__username')
    actions = [
        'mark_as_resolved', 'ban_users', 'unban_user',
        'soft_delete_user', 'restore_user', 'permanently_delete_user',
        'ban_1_day', 'ban_3_days', 'ban_7_days', 'investigate_user',
    ]

    def has_add_permission(self, request):
        return False
    def changelist_view(self, request, extra_context=None):
        unresolved_count = Report.objects.filter(resolved=False).count()
        if unresolved_count > 0:
            messages.warning(request, f"You have {unresolved_count} unresolved report(s).")
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(resolved=False) 

    def change_view(self, request, object_id, form_url='', extra_context=None):
        report = get_object_or_404(self.model, pk=object_id)
        extra_context = extra_context or {}
        extra_context['report'] = report
        extra_context['post'] = report.post
        return super().change_view(request, object_id, form_url, extra_context)

    def new_reports_badge(self, request):
        """Returns a badge indicating the number of unresolved reports."""
        unresolved_reports_count = Report.objects.filter(resolved=False).count()
        if unresolved_reports_count > 0:
            return format_html(
                '<span style="color: white; background-color: red; padding: 5px; border-radius: 50%; font-weight: bold; font-size: 14px;">{}</span>',
                unresolved_reports_count
            )
        return ''

    def report_badge(self, request):
        """Override the admin index page to show the badge on the report section"""
        unresolved_reports_count = Report.objects.filter(resolved=False).count()
        if unresolved_reports_count > 0:
            return format_html(
                '<span style="color: white; background-color: red; padding: 5px; border-radius: 50%; font-weight: bold; font-size: 14px;">{}</span>',
                unresolved_reports_count
            )
        return ''


    def ban_users(self, request, queryset):
        self._ban_and_record_evidence(request, queryset, permanent=True)
    ban_users.short_description = "Permanently ban selected users"

    def ban_users_for_days(self, request, queryset, days):
        self._ban_and_record_evidence(request, queryset, days=days)

    def _ban_and_record_evidence(self, request, queryset, permanent=False, days=None):
        banned_users = []
        for report in queryset:
            user = report.post.author
            if not user.profile.is_banned or user.profile.is_currently_banned():
                # Ban user
                if permanent:
                    user.profile.ban()
                else:
                    user.profile.ban(duration_days=days)
                banned_users.append(user.username)

                Evidence.objects.create(
                    post=report.post,
                    report=report,
                    reported_by=report.reporter
                )

                report.resolved = True
                report.save()

        if banned_users:
            msg = f"Permanently banned: " if permanent else f"Banned for {days} day(s): "
            self.message_user(request, msg + ", ".join(banned_users))
        else:
            self.message_user(request, "No users were banned.")

    def ban_1_day(self, request, queryset):
        self.ban_users_for_days(request, queryset, 1)
    ban_1_day.short_description = "Ban users for 1 day"

    def ban_3_days(self, request, queryset):
        self.ban_users_for_days(request, queryset, 3)
    ban_3_days.short_description = "Ban users for 3 days"

    def ban_7_days(self, request, queryset):
        self.ban_users_for_days(request, queryset, 7)
    ban_7_days.short_description = "Ban users for 7 days"




def custom_admin_index(request):
    unresolved_reports_count = Report.objects.filter(resolved=False).count()
    badge = ReportAdmin().report_badge(request)
    return badge


# reporting
class BannedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'banned_at', 'ban_duration_days', 'get_latest_report_reason', 'get_status')
    search_fields = ('user__username',)
    actions = ['unban_users']
    change_form_template = "social/admin/banned_user.html"

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return ['user', 'banned_at']

    def get_latest_report_reason(self, obj):
        try:
            latest_report = obj.user.report_set.latest('reported_on')
            return latest_report.reason
        except:
            return "No report available"
    get_latest_report_reason.short_description = "Latest Report Reason"

    def get_status(self, obj):
        from .models import UserUnderInvestigation
        is_under_investigation = UserUnderInvestigation.objects.filter(user=obj.user).exists()
        if is_under_investigation:
            return "Banned & Under Investigation"
        return "Banned"
    get_status.short_description = "Status"

    def response_change(self, request, obj):
        if "_unban" in request.POST:
            obj.user.profile.unban()
            self.message_user(request, "User has been unbanned.")
            return redirect(reverse("admin:social_banneduser_changelist"))
        return super().response_change(request, obj)

    def unban_users(self, request, queryset):
        for banned in queryset:
            banned.user.profile.unban()
        self.message_user(request, "Selected users have been unbanned.")
    unban_users.short_description = "Unban selected users"

class PostAdmin(admin.ModelAdmin):
    change_form_template = "social/admin/post.html"

    search_fields = ('body', 'author__username')  

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    
    
    

class FeedbackAdmin(admin.ModelAdmin):
    change_list_template = "social/admin/feedback.html"
    list_display = ('user', 'feature', 'created_at', 'screenshot')
    list_filter = ('feature', 'created_at')
    search_fields = ('feedback_text', 'user__username')
    actions = ['mark_as_resolved']

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return True  

    def mark_as_resolved(self, request, queryset):
        queryset.update(resolved=True)
        self.message_user(request, "Selected feedback has been marked as resolved.")
    mark_as_resolved.short_description = "Mark selected feedback as resolved"


# evindence for reports

class EvidenceAdmin(admin.ModelAdmin):
    change_form_template = "social/admin/report.html"  
    list_display = ('post', 'report', 'reported_by', 'created_at')
    search_fields = ('post__body', 'report__reporter__username')
    readonly_fields = ('post', 'report', 'reported_by', 'created_at')

    def has_add_permission(self, request):
        return False  
    def change_view(self, request, object_id, form_url='', extra_context=None):
        evidence = self.get_object(request, object_id)
        extra_context = extra_context or {}
        extra_context['report'] = evidence.report
        extra_context['post'] = evidence.post
        extra_context['evidence'] = evidence
        return super().change_view(request, object_id, form_url, extra_context)
admin.site.register(Evidence, EvidenceAdmin)


class MessageAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


original_index = admin.site.index
def custom_admin_index(request, extra_context=None):
    unresolved_count = Report.objects.filter(resolved=False).count()
    if unresolved_count > 0:
        badge = format_html(
            '<span style="background: red; color: white; padding: 2px 6px; '
            'border-radius: 12px; font-size: 12px; margin-left: 8px;">{}</span>',
            unresolved_count
        )
        messages.warning(request, format_html("Unresolved reports: {} (see Reports section)", badge))
    return original_index(request, extra_context)

admin.site.index = custom_admin_index



# registered models
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(BannedUser, BannedUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Rule)
admin.site.register(Group)
admin.site.register(Event)




# unregistered ()
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)

# try
from django_apscheduler.admin import DjangoJobAdmin
from django.contrib import admin
from django_apscheduler.models import DjangoJob, DjangoJobExecution

for model in [DjangoJob, DjangoJobExecution]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass