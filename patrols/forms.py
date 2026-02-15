from django import forms

class CheckInForm(forms.Form):
    code = forms.CharField(max_length=32, label="Checkpoint code")
    notes = forms.CharField(max_length=255, required=False, label="Notes (optional)")
