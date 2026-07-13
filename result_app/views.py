from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
import pandas as pd
from .forms import UploadExcelForm, ColumnMappingForm, SchoolSettingsForm
from .models import SchoolSettings, ResultHistory
from .utils import process_excel, process_student_data, generate_pdf, get_color_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import CustomLoginForm


def index(request):
    """Home page view"""
    return render(request, 'result_app/index.html')

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'result_app/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')
    
    def get_success_url(self):
        return self.success_url

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    return redirect('login')


@login_required(login_url='/admin/login/')
def upload_excel(request):
    """Upload Excel file view"""
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            
            try:
                df = pd.read_excel(excel_file)
                columns = df.columns.tolist()
                request.session['excel_columns'] = columns
                request.session['excel_data'] = df.to_dict('records')
                
                # Store file for later use
                file_content = excel_file.read()
                request.session['excel_file_content'] = file_content.hex()
                
                return redirect('column_mapping')
            except Exception as e:
                messages.error(request, f'Error reading Excel file: {str(e)}')
                return redirect('upload_excel')
    else:
        form = UploadExcelForm()
    
    return render(request, 'result_app/upload.html', {'form': form})

@login_required(login_url='/admin/login/')
def column_mapping(request):
    """Column mapping view"""
    columns = request.session.get('excel_columns', [])
    if not columns:
        messages.error(request, 'Please upload an Excel file first.')
        return redirect('upload_excel')
    
    if request.method == 'POST':
        form = ColumnMappingForm(request.POST, columns=columns)
        if form.is_valid():
            mapping = {
                'name_column': form.cleaned_data['name_column'],
                'roll_column': form.cleaned_data['roll_column'],
                'class_column': form.cleaned_data['class_column'],
                'shift_column': form.cleaned_data['shift_column'],
                'section_column': form.cleaned_data['section_column'],
                'semester_column': form.cleaned_data['semester_column'],
                'subject_columns': form.cleaned_data['subject_columns'],
            }
            request.session['column_mapping'] = mapping
            
            # Process student data
            excel_data = request.session.get('excel_data', [])
            df = pd.DataFrame(excel_data)
            students = process_student_data(df, mapping)
            request.session['processed_students'] = students
            
            return redirect('result_preview')
    else:
        form = ColumnMappingForm(columns=columns)
    
    return render(request, 'result_app/column_mapping.html', {
        'form': form,
        'columns': columns
    })

@login_required(login_url='/admin/login/')
def result_preview(request):
    """Preview results before generating PDF"""
    students = request.session.get('processed_students', [])
    if not students:
        messages.error(request, 'No student data found. Please upload and map columns first.')
        return redirect('upload_excel')
    
    # Get or create settings
    settings, created = SchoolSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'school_name': 'ABC HIGH SCHOOL',
            'school_address': 'Dhaka, Bangladesh',
        }
    )
    
    context = {
        'students': students[:10],  # Show first 10 for preview
        'total_students': len(students),
        'settings': settings,
    }
    
    return render(request, 'result_app/result_preview.html', context)

@login_required(login_url='/admin/login/')
@login_required(login_url='/admin/login/')
def generate_results(request):
    """Generate and download PDF results"""
    students = request.session.get('processed_students', [])
    if not students:
        messages.error(request, 'No student data found.')
        return redirect('upload_excel')
    
    try:
        # Get or create settings
        settings_obj, created = SchoolSettings.objects.get_or_create(
            user=request.user,
            defaults={
                'school_name': 'ABC HIGH SCHOOL',
                'school_address': 'Dhaka, Bangladesh',
            }
        )
        
        # Generate PDF
        pdf_path = generate_pdf(students, settings_obj)
        
        # Save to history
        result_history = ResultHistory.objects.create(
            user=request.user,
            total_students=len(students),
        )
        
        # Save PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = ContentFile(f.read())
            result_history.pdf_file.save(
                f'result_{uuid.uuid4().hex[:8]}.pdf',
                pdf_content
            )
            result_history.save()
        
        # Return file
        response = FileResponse(
            open(pdf_path, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'student_results_{uuid.uuid4().hex[:8]}.pdf'
        )
        
        # Clean up the file after sending (optional)
        # You might want to keep it for history
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('result_preview')
# def generate_results(request):
    """Generate and download PDF results"""
    students = request.session.get('processed_students', [])
    if not students:
        messages.error(request, 'No student data found.')
        return redirect('upload_excel')
    
    settings = SchoolSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'school_name': 'ABC HIGH SCHOOL',
            'school_address': 'Dhaka, Bangladesh',
        }
    )[0]
    
    # Generate PDF
    try:
        pdf_path = generate_pdf(students, settings)
        
        # Save to history
        result_history = ResultHistory.objects.create(
            user=request.user,
            total_students=len(students),
        )
        
        # Save PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = ContentFile(f.read())
            result_history.pdf_file.save(
                f'result_{uuid.uuid4().hex[:8]}.pdf',
                pdf_content
            )
            result_history.save()
        
        # Return file
        return FileResponse(
            open(pdf_path, 'rb'),
            as_attachment=True,
            filename=f'student_results_{uuid.uuid4().hex[:8]}.pdf'
        )
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('result_preview')



@login_required(login_url='/admin/login/')
def settings_view(request):
    """School settings view"""
    settings_obj, created = SchoolSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'school_name': 'ABC HIGH SCHOOL',
            'school_address': 'Dhaka, Bangladesh',
        }
    )
    
    if request.method == 'POST':
        form = SchoolSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = SchoolSettingsForm(instance=settings_obj)
    
    return render(request, 'result_app/settings.html', {'form': form})

def download_sample_excel(request):
    """Download sample Excel file"""
    import pandas as pd
    from io import BytesIO
    
    data = {
        'Roll': [1, 2, 3, 4, 5],
        'Name': ['Student 1', 'Student 2', 'Student 3', 'Student 4', 'Student 5'],
        'Class': ['Ten', 'Ten', 'Ten', 'Ten', 'Ten'],
        'Shift': ['Morning', 'Morning', 'Morning', 'Morning', 'Morning'],
        'Section': ['A', 'A', 'A', 'A', 'A'],
        'Semester': ['Final', 'Final', 'Final', 'Final', 'Final'],
        'Bangla': [85, 70, 92, 78, 88],
        'English': [78, 65, 85, 72, 90],
        'Math': [92, 80, 88, 75, 85],
        'Science': [80, 75, 90, 70, 82],
        'ICT': [88, 72, 85, 68, 80],
    }
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="sample_student_results.xlsx"'
    return response