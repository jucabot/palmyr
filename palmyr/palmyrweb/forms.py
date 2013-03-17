from django import forms
from django.core.exceptions import ValidationError

def csv_file_validator(value):
        if not value.name.lower().endswith('.csv'):
            raise ValidationError({'invalid type': 'Select a .csv file'})

class UploadFileForm(forms.Form):
    file  = forms.FileField(validators=[csv_file_validator])