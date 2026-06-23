from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from apps.authentication.mixins import AdminRequiredMixin, MultiRoleRequiredMixin
from apps.doctors.models import Doctor

from .forms import LabOrderFilterForm, LabOrderForm, LabResultFormSet, LabTestForm
from .models import LabOrder, LabOrderItem, LabTest
from .services import auto_flag_result
from .tasks import notify_critical_result


class LabAccessMixin(MultiRoleRequiredMixin):
    allowed_roles = ["ADMIN", "DOCTOR", "LAB_TECH"]


class LabTechAccessMixin(MultiRoleRequiredMixin):
    allowed_roles = ["ADMIN", "LAB_TECH"]


class LabOrderListView(LabAccessMixin, ListView):
    model = LabOrder
    template_name = "lab/order_list.html"
    context_object_name = "orders"
    paginate_by = 25

    def get_queryset(self):
        queryset = LabOrder.objects.select_related("patient", "doctor").prefetch_related("tests")
        if self.request.user.role == "DOCTOR":
            doctor = Doctor.objects.filter(user=self.request.user).first()
            queryset = queryset.filter(doctor=doctor) if doctor else queryset.none()

        self.filter_form = LabOrderFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            status = self.filter_form.cleaned_data.get("status")
            priority = self.filter_form.cleaned_data.get("priority")
            date = self.filter_form.cleaned_data.get("date")
            if status:
                queryset = queryset.filter(status=status)
            if priority:
                queryset = queryset.filter(priority=priority)
            if date:
                queryset = queryset.filter(ordered_at__date=date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", LabOrderFilterForm())
        context["status_choices"] = LabOrder.STATUS_CHOICES
        context["breadcrumbs"] = [{"label": "Laboratory"}, {"label": "Orders"}]
        return context


class LabOrderCreateView(LabAccessMixin, View):
    template_name = "lab/order_detail.html"

    def get(self, request):
        form = LabOrderForm(user=request.user)
        return render(request, self.template_name, self.get_context(form=form, mode="create"))

    @transaction.atomic
    def post(self, request):
        form = LabOrderForm(request.POST, user=request.user)
        if form.is_valid():
            tests = form.cleaned_data.pop("tests")
            order = form.save(commit=False)
            order.save()
            for test in tests:
                LabOrderItem.objects.create(order=order, test=test)
            messages.success(request, "Lab order created.")
            return redirect("laboratory:order_detail", pk=order.pk)
        return render(request, self.template_name, self.get_context(form=form, mode="create"))

    def get_context(self, **kwargs):
        context = {
            "order": None,
            "items": [],
            "breadcrumbs": [
                {"label": "Laboratory", "url": reverse_lazy("laboratory:order_list")},
                {"label": "New order"},
            ],
        }
        context.update(kwargs)
        return context


class LabOrderDetailView(LabAccessMixin, DetailView):
    model = LabOrder
    template_name = "lab/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        queryset = LabOrder.objects.select_related("patient", "doctor").prefetch_related("laborderitem_set__test")
        if self.request.user.role == "DOCTOR":
            doctor = Doctor.objects.filter(user=self.request.user).first()
            queryset = queryset.filter(doctor=doctor) if doctor else queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.laborderitem_set.select_related("test").all()
        context["items"] = items
        context["result_formset"] = LabResultFormSet(queryset=items)
        context["breadcrumbs"] = [
            {"label": "Laboratory", "url": reverse_lazy("laboratory:order_list")},
            {"label": f"Order #{self.object.pk}"},
        ]
        return context


class LabResultEntryView(LabTechAccessMixin, View):
    template_name = "lab/order_detail.html"

    def post(self, request, pk):
        order = get_object_or_404(
            LabOrder.objects.select_related("patient", "doctor").prefetch_related("laborderitem_set__test"),
            pk=pk,
        )
        items = order.laborderitem_set.select_related("test").all()
        formset = LabResultFormSet(request.POST, queryset=items)
        if formset.is_valid():
            with transaction.atomic():
                any_pending = False
                for form in formset:
                    item = form.save(commit=False)
                    old_flag = LabOrderItem.objects.filter(pk=item.pk).values_list("flag", flat=True).first()
                    item.flag = auto_flag_result(item.test, item.result)
                    if item.verified:
                        item.verified_by = request.user
                        item.completed_at = item.completed_at or timezone.now()
                    else:
                        any_pending = True
                    item.save()
                    if item.flag == "CRITICAL" and old_flag != "CRITICAL":
                        notify_critical_result.delay(item.pk)

                order.status = LabOrder.PROCESSING if any_pending else LabOrder.COMPLETED
                order.save(update_fields=["status"])
            messages.success(request, "Lab results saved.")
            return redirect("laboratory:order_detail", pk=order.pk)

        return render(
            request,
            self.template_name,
            {
                "order": order,
                "items": items,
                "result_formset": formset,
                "breadcrumbs": [
                    {"label": "Laboratory", "url": reverse_lazy("laboratory:order_list")},
                    {"label": f"Order #{order.pk}"},
                ],
            },
        )


class LabReportView(LabAccessMixin, DetailView):
    model = LabOrder
    template_name = "lab/report.html"
    context_object_name = "order"

    def get_queryset(self):
        queryset = LabOrder.objects.select_related("patient", "doctor").prefetch_related("laborderitem_set__test")
        if self.request.user.role == "DOCTOR":
            doctor = Doctor.objects.filter(user=self.request.user).first()
            queryset = queryset.filter(doctor=doctor) if doctor else queryset.none()
        return queryset


class LabTestCatalogueView(AdminRequiredMixin, View):
    template_name = "lab/catalogue.html"

    def get(self, request):
        editing = None
        form = None
        if request.GET.get("edit"):
            editing = get_object_or_404(LabTest, pk=request.GET["edit"])
            form = LabTestForm(instance=editing)
        return render(request, self.template_name, self.get_context(form=form, editing=editing))

    def post(self, request):
        action = request.POST.get("action", "create")
        test = None
        if action in {"update", "delete"}:
            test = get_object_or_404(LabTest, pk=request.POST.get("test_id"))
        if action == "delete":
            test.delete()
            messages.success(request, "Lab test deleted.")
            return redirect("laboratory:test_catalogue")

        form = LabTestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, "Lab test saved.")
            return redirect("laboratory:test_catalogue")
        return render(request, self.template_name, self.get_context(form=form, editing=test))

    def get_context(self, form=None, editing=None):
        return {
            "tests": LabTest.objects.order_by("category", "name"),
            "form": form or LabTestForm(),
            "editing": editing,
            "breadcrumbs": [{"label": "Laboratory", "url": reverse("laboratory:order_list")}, {"label": "Test catalogue"}],
        }
