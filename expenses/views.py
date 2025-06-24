from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .models import Expense, ExpenseRole
from django.core.exceptions import PermissionDenied
from .forms import ExpenseForm

class ExpenseListView(ListView):
    model = Expense
    paginate_by = 10
    template_name = "expenses/expense_list.html"
    ordering = ['-updated_at'] 

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "expense_role", None).role

        if role in (ExpenseRole.Role.GLOBAL_VIEWER, ExpenseRole.Role.GLOBAL_EDITOR):
            return Expense.objects.all().order_by("-created_at")
        # SELF_SERVICE
        return Expense.objects.filter(created_by=user).order_by("-created_at")

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy("expenses:list")
    template_name = "expenses/expense_form.html"

    def form_valid(self, form):
        expense = form.instance
        expense.created_by = self.request.user
        expense.updated_by = self.request.user
        return super().form_valid(form)

class ExpenseDetailView(DetailView):
    model = Expense
    template_name = "expenses/expense_detail.html"
    context_object_name = "expense"

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy("expenses:list")
    template_name = "expenses/expense_form.html"

    def form_valid(self, form):
        expense = form.instance
        expense.updated_by = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        obj  = self.get_object()
        role = request.user.expense_role.role

        # SELF_SERVICE or GLOBAL_VIEWER may only edit their own
        if role != ExpenseRole.Role.GLOBAL_EDITOR and obj.created_by != request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
