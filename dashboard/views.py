import base64
from io import BytesIO
import qrcode

from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render
from accounts.decorators import supervisor_required
from patrols.models import PatrolSession
from django.shortcuts import get_object_or_404
from patrols.models import Route
from django.contrib.auth.decorators import login_required
from accounts.decorators import supervisor_required

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


@login_required
@supervisor_required
def route_qr_pack(request, route_id):
    route = get_object_or_404(Route.objects.select_related("site"), id=route_id)
    checkpoints = route.checkpoints.all()

    items = []
    for cp in checkpoints:
        # QR just holds the checkpoint code for now (works even without session)
        # If you want QR to hold a URL, you'd generate it per active session instead.
        data = cp.code

        img = qrcode.make(data)
        buff = BytesIO()
        img.save(buff, format="PNG")
        b64 = base64.b64encode(buff.getvalue()).decode("utf-8")

        items.append({"checkpoint": cp, "qr_b64": b64})

    return render(request, "dashboard/route_qr_pack.html", {"route": route, "items": items})