from django import forms
from .models import SchoolSettings
from django.contrib.auth.forms import AuthenticationForm


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Upload Excel File',
        help_text='Supported formats: .xlsx, .xls',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )

class ColumnMappingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        super().__init__(*args, **kwargs)
        
        choices = [('', 'Select Column')] + [(col, col) for col in columns]
        
        self.fields['name_column'] = forms.ChoiceField(
            choices=choices,
            label='Student Name Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['roll_column'] = forms.ChoiceField(
            choices=choices,
            label='Roll Number Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['class_column'] = forms.ChoiceField(
            choices=choices,
            label='Class Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['shift_column'] = forms.ChoiceField(
            choices=choices,
            label='Shift Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['section_column'] = forms.ChoiceField(
            choices=choices,
            label='Section Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['semester_column'] = forms.ChoiceField(
            choices=choices,
            label='Semester Column',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        
        # Subject columns - will be added dynamically
        self.fields['subject_columns'] = forms.MultipleChoiceField(
            choices=[(col, col) for col in columns],
            label='Subject Columns',
            widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
            required=True
        )

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'school_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'school_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'signature_image': forms.FileInput(attrs={'class': 'form-control'}),
            'seal_image': forms.FileInput(attrs={'class': 'form-control'}),
            'paper_size': forms.Select(attrs={'class': 'form-select'}),
            'orientation': forms.Select(attrs={'class': 'form-select'}),
            'primary_color': forms.Select(attrs={'class': 'form-select'}),
            'font_style': forms.Select(attrs={'class': 'form-select'}),
            'grading_system': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }











class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)