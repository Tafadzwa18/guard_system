import base64
from io import BytesIO
import qrcode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from accounts.decorators import guard_required
from .forms import CheckInForm
from .models import Shift, PatrolSession, Route, Checkpoint, CheckIn
from .models import PatrolSession

@login_required
@guard_required
def guard_home(request):
    shifts = Shift.objects.filter(guard=request.user, is_active=True).select_related("route", "route__site")
    active_session = PatrolSession.objects.filter(guard=request.user, status=PatrolSession.Status.ACTIVE).select_related("route").first()
    return render(request, "patrols/guard_home.html", {"shifts": shifts, "active_session": active_session})

@login_required
@guard_required
def start_patrol(request, route_id):
    route = get_object_or_404(Route, id=route_id, is_active=True)
    # End any existing active session (optional: block instead)
    PatrolSession.objects.filter(guard=request.user, status=PatrolSession.Status.ACTIVE).update(
        status=PatrolSession.Status.FLAGGED, ended_at=timezone.now()
    )
    session = PatrolSession.objects.create(guard=request.user, route=route)
    messages.success(request, f"Patrol started for {route.name}.")
    return redirect("patrol_checkin", session_id=session.id)

@login_required
@guard_required
def patrol_checkin(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)

    if session.status != PatrolSession.Status.ACTIVE:
        return redirect("patrol_summary", session_id=session.id)

    form = CheckInForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"].strip()
        notes = form.cleaned_data["notes"].strip()

        checkpoint = Checkpoint.objects.filter(route=session.route, code=code).first()
        if not checkpoint:
            messages.error(request, "Invalid checkpoint code for this route.")
        else:
            try:
                CheckIn.objects.create(session=session, checkpoint=checkpoint, notes=notes)
                messages.success(request, f"Checked in at: {checkpoint.name}")
                return redirect("patrol_checkin", session_id=session.id)
            except Exception:
                messages.warning(request, "That checkpoint has already been checked in for this patrol.")

    checkpoints = session.route.checkpoints.all()
    checked_ids = set(session.checkins.values_list("checkpoint_id", flat=True))
    return render(
        request,
        "patrols/patrol_checkin.html",
        {
            "session": session,
            "form": form,
            "checkpoints": checkpoints,
            "checked_ids": checked_ids,
        },
    )

@login_required
@guard_required
def end_patrol(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)
    if session.status == PatrolSession.Status.ACTIVE:
        session.end()
        messages.success(request, "Patrol ended.")
    return redirect("patrol_summary", session_id=session.id)

@login_required
@guard_required
def patrol_summary(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)
    checkpoints = session.route.checkpoints.all()
    checked_ids = set(session.checkins.values_list("checkpoint_id", flat=True))
    completed = [cp for cp in checkpoints if cp.id in checked_ids]
    missed = [cp for cp in checkpoints if cp.id not in checked_ids]
    return render(
        request,
        "patrols/patrol_summary.html",
        {"session": session, "completed": completed, "missed": missed},
    )

@login_required
@guard_required
def qr_scan_checkin(request, session_id, code):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)

    if session.status != PatrolSession.Status.ACTIVE:
        messages.info(request, "This patrol is not active.")
        return redirect("patrol_summary", session_id=session.id)

    checkpoint = Checkpoint.objects.filter(route=session.route, code=code).first()
    if not checkpoint:
        messages.error(request, "Invalid QR checkpoint for this route.")
        return redirect("patrol_checkin", session_id=session.id)

    try:
        CheckIn.objects.create(session=session, checkpoint=checkpoint, method=CheckIn.Method.QR)
        messages.success(request, f"QR check-in recorded: {checkpoint.name}")
    except Exception:
        messages.warning(request, "Checkpoint already checked in for this patrol.")

    return redirect("patrol_checkin", session_id=session.id)

@login_required
@guard_required
def scan_camera(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)

    if session.status != PatrolSession.Status.ACTIVE:
        messages.info(request, "This patrol is not active.")
        return redirect("patrol_summary", session_id=session.id)

    return render(request, "patrols/scan_camera.html", {"session": session})


@login_required
@guard_required
def session_qr_pack(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)

    if session.status != PatrolSession.Status.ACTIVE:
        messages.info(request, "This patrol is not active.")
        return redirect("patrol_summary", session_id=session.id)

    items = []
    for cp in session.route.checkpoints.all():
        url = request.build_absolute_uri(reverse("qr_scan_checkin", args=[session.id, cp.code]))
        img = qrcode.make(url)
        buff = BytesIO()
        img.save(buff, format="PNG")
        b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
        items.append({"checkpoint": cp, "qr_b64": b64, "url": url})

    return render(request, "patrols/session_qr_pack.html", {"session": session, "items": items})
