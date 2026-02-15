from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import guard_required, supervisor_required
from patrols.models import PatrolSession

from .forms import IncidentReportForm
from .models import IncidentReport

@login_required
@guard_required
def create_incident(request, session_id):
    session = get_object_or_404(PatrolSession, id=session_id, guard=request.user)

    # Only allow incidents for sessions that belong to this guard (active or completed)
    form = IncidentReportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        incident = form.save(commit=False)
        incident.session = session
        incident.created_by = request.user

        # If a checkpoint is selected, ensure it belongs to the session's route
        if incident.checkpoint and incident.checkpoint.route_id != session.route_id:
            messages.error(request, "That checkpoint does not belong to this route.")
        else:
            incident.save()
            messages.success(request, "Incident report submitted.")
            return redirect("patrol_checkin", session_id=session.id) if session.status == "ACTIVE" else redirect("patrol_summary", session_id=session.id)

    # Limit checkpoint dropdown to this route
    form.fields["checkpoint"].queryset = session.route.checkpoints.all()

    return render(request, "incidents/create.html", {"form": form, "session": session})

@login_required
@supervisor_required
def incident_list(request):
    qs = IncidentReport.objects.select_related(
        "session", "session__guard", "session__route", "session__route__site", "checkpoint"
    ).order_by("-created_at")

    severity = request.GET.get("severity", "").strip()
    site = request.GET.get("site", "").strip()

    if severity:
        qs = qs.filter(severity=severity)
    if site:
        qs = qs.filter(session__route__site__name__icontains=site)

    return render(request, "incidents/list.html", {"incidents": qs})

@login_required
@supervisor_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(
        IncidentReport.objects.select_related(
            "session", "session__guard", "session__route", "session__route__site", "checkpoint"
        ),
        id=incident_id
    )
    return render(request, "incidents/detail.html", {"incident": incident})
