# profiles/views.py

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from .models import UserProfile, OnDutyChangeLog

class OnDutyView(TemplateView):
    template_name = "profiles/on_duty.html"

    def post(self, request, *args, **kwargs):
        # expected POST: profile_id + new_status
        pid = request.POST.get("profile_id")
        new_status = request.POST.get("new_status") == "on"
        profile = get_object_or_404(UserProfile, id=pid)

        old = profile.is_on_duty
        profile.is_on_duty = new_status
        profile.save()

        # record a change log
        OnDutyChangeLog.objects.create(
            who_changed = request.user,
            target_profile = profile,
            old_value = old,
            new_value = new_status
        )
        return redirect("profiles:on_duty")

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        profiles = UserProfile.objects.select_related("user")
        ctx["profiles"] = profiles

        # pull logs, newest first:
        all_logs = OnDutyChangeLog.objects.select_related(
            "who_changed", "target_profile__user"
        ).order_by("-timestamp")
        paginator = Paginator(all_logs, 10)
        page = self.request.GET.get("log_page") or 1
        ctx["log_page_obj"] = paginator.get_page(page)
        return ctx