from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render

from accounts.decorators import supervisor_required
from patrols.models import PatrolSession

@login_required
@supervisor_required
def live_dashboard(request):
    sessions = (
        PatrolSession.objects.filter(status=PatrolSession.Status.ACTIVE)
        .select_related("guard", "route", "route__site")
        .annotate(last_checkin=Max("checkins__checked_in_at"))
        .order_by("-started_at")
    )
    return render(request, "dashboard/live.html", {"sessions": sessions})

@login_required
@supervisor_required
def history(request):
    qs = PatrolSession.objects.select_related("guard", "route", "route__site").order_by("-started_at")

    site = request.GET.get("site", "").strip()
    guard = request.GET.get("guard", "").strip()
    status = request.GET.get("status", "").strip()

    if status:
        qs = qs.filter(status=status)
    if guard:
        qs = qs.filter(guard__username__icontains=guard)
    if site:
        qs = qs.filter(route__site__name__icontains=site)

    return render(request, "dashboard/history.html", {"sessions": qs})
