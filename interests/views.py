# interests/views.py
from datetime import date, timedelta
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView

from .models import Interest, AuthorizedInterestUser
from django.contrib.auth.decorators import login_required
from .forms import InterestForm
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from django.views.generic import CreateView
from customers.forms import CustomerForm
from customers.models import Customer
from interests.models import Interest

from django.contrib import messages


from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from profiles.models import Department, DepartmentMembership
from .models import Interest

import logging
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

from django.http import HttpResponseForbidden

from customers.forms import CustomerForm  # or your InterestForm

import datetime
from django.utils import timezone


@require_POST
def adjust_dials(request, pk):
    if not request.user.is_authenticated:
        raise Http404()
    try:
        payload = json.loads(request.body)
        delta   = int(payload.get('delta', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid payload'}, status=400)

    interest = get_object_or_404(Interest, pk=pk)
    # optional: permissions check here...
    new_count = max(0, interest.dials + delta)
    interest.dials = new_count
    interest.updated_by = request.user
    interest.save()
    return JsonResponse({'dials': new_count})


class InterestListView(LoginRequiredMixin, ListView):
    model = Interest
    template_name = "interests/interest_list.html"
    paginate_by = 10
    ordering = ['-updated_at']

    def dispatch(self, request, *args, **kwargs):
        # lookup your specific department
        dept = Department.objects.filter(
            dept_type__name='Customer Support',
            region__name='Meerut',
            category__name='Lead Qualification Team'
        ).first()
        if not dept:
            # department doesn’t exist → show 403.html
            return render(request, "403.html", status=403)

        # check membership
        membership = DepartmentMembership.objects.filter(
            user=request.user,
            department=dept
        ).first()
        if not membership:
            # user not in that department → show 403.html
            return render(request, "403.html", status=403)

        # user is allowed
        self.department = dept
        self.user_level  = membership.level
        return super().dispatch(request, *args, **kwargs)


    def get_queryset(self):
        print("🔍 GET parameters: ", dict(self.request.GET))
        qs = super().get_queryset()

        # — 1) phone search —
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(phone_number__icontains=q)

        # — 2) date‐range —
        range_str = self.request.GET.get('range', '').strip()
        if range_str:
            try:
                start_str, end_str = [d.strip() for d in range_str.split(" to ", 1)]
                start_date = datetime.date.fromisoformat(start_str)
                end_date   = datetime.date.fromisoformat(end_str)
                # create datetimes at start‐of‐day and end‐of‐day, in your timezone
                start_dt = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
                end_dt   = timezone.make_aware(datetime.datetime.combine(end_date,   datetime.time.max))
            except Exception as e:
                # fallback to last 7 days
                today = timezone.localdate()
                start_dt = timezone.make_aware(datetime.datetime.combine(today - timedelta(days=7), datetime.time.min))
                end_dt   = timezone.make_aware(datetime.datetime.combine(today,                            datetime.time.max))
            print("🗓️ Filtering created_at between", start_dt, "and", end_dt)
            qs = qs.filter(created_at__gte=start_dt, created_at__lte=end_dt)
            print("📊 Count after date filter:", qs.count())

        # — 3) connected filter —
        conn = self.request.GET.get('connected', '')
        if conn == '1':
            qs = qs.filter(is_connected=True)
        elif conn == '0':
            qs = qs.filter(is_connected=False) 

        # — 4) now apply your level 1/2/3 access rules —
        if self.user_level == 3:
            return qs.filter(created_by=self.request.user)
        if self.user_level == 2:
            lvl3_ids = DepartmentMembership.objects.filter(
                department=self.department, level=3
            ).values_list('user_id', flat=True)
            return qs.filter(created_by__in=list(lvl3_ids) + [self.request.user.id])
        if self.user_level == 1:
            lvl123 = DepartmentMembership.objects.filter(
                department=self.department, level__in=[1,2,3]
            ).values_list('user_id', flat=True)
            return qs.filter(created_by__in=list(lvl123))

        return qs.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'q':         self.request.GET.get('q', ''),
            'range':     self.request.GET.get('range', ''),
            'connected': self.request.GET.get('connected', ''),
            'department': self.department,
            'user_level': self.user_level,
        })
        return ctx


class InterestCreateView(LoginRequiredMixin, CreateView):
    model = Interest
    form_class = InterestForm      # or CustomerForm if you’re creating a Customer from an Interest
    template_name = "interests/interest_form.html"
    success_url = reverse_lazy("interests:list")

    def dispatch(self, request, *args, **kwargs):
        # 1) find the correct department
        dept = Department.objects.filter(
            dept_type__name='Customer Support',
            region__name='Meerut',
            category__name='Lead Qualification Team'
        ).first()
        if not dept:
            return render(request, "403.html", status=403)

        # 2) check that the user belongs there (any level 1/2/3)
        membership = DepartmentMembership.objects.filter(
            user=request.user,
            department=dept
        ).first()
        if not membership:
            return render(request, "403.html", status=403)

        # passed — allow create
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # set created_by/updated_by exactly once
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)



class InterestCustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "interests/interest_create_from_interest.html"

    def get_initial(self):
        # grab ?from_interest, ?phone, ?source=XYZ from the URL
        initial = super().get_initial()
        interest_pk = self.request.GET.get("from_interest")
        phone        = self.request.GET.get("phone")
        source_pk    = self.request.GET.get("source")
        if interest_pk:
            initial["interest"]     = interest_pk
        if phone:
            initial["primary_phone"] = phone
        if source_pk:
            initial["source"]        = source_pk
        return initial

    def form_valid(self, form):
        # link the new Customer back to the Interest
        interest_pk = self.request.GET.get("from_interest")
        if interest_pk:
            interest = Interest.objects.get(pk=interest_pk)
            form.instance.linked_interest = interest
        return super().form_valid(form)

    def get_success_url(self):
        # once the Customer is created, go back to the Interest edit page
        interest_pk = self.request.GET.get("from_interest")
        return reverse_lazy("interests:edit", args=[interest_pk])


class InterestUpdateView(LoginRequiredMixin, UpdateView):
    model = Interest
    form_class = InterestForm
    template_name = "interests/interest_form.html"
    success_url = reverse_lazy("interests:list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Keep your role‐based guard
        auth = AuthorizedInterestUser.objects.filter(user=request.user).first()
        if not auth or (auth.role_type == "member" and obj.created_by != request.user):
            return render(request, "interests/interest_list.html", {"has_access": False})

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # If there’s already a Lead, disable every field
        if getattr(self.get_object(), 'lead', None) is not None:
            for field in form.fields.values():
                field.disabled = True
            # flash a notice so the user knows why it’s locked
            messages.info(self.request,
                "This interest is tied to a Lead, so fields are read-only."
            )
        return form

    def form_valid(self, form):
        # you may still want to prevent POST from actually doing anything
        if getattr(self.get_object(), 'lead', None) is not None:
            # just re-render without saving
            return self.render_to_response(self.get_context_data(form=form))
        form.instance.updated_by = self.request.user
        return super().form_valid(form)