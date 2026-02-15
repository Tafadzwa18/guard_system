from django import forms
from .models import IncidentReport

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ["checkpoint", "title", "description", "severity", "photo"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
