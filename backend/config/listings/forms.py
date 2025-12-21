from django import forms

class PropertyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select CSV file')
