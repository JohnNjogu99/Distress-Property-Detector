# listings/forms.py
from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ["title", "description", "location", "price"]

class PropertyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select CSV file')
